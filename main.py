from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '5!MB8orN&205j962'

#define class to correspond to db table and fields
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#DEFINE REQUEST HANDLERS
#pre-screen all requests to preven unauthorized access to pages reserved for registerd/signed-in users
@app.before_request 
def require_login():
    allowed_routes = ['login', 'signup', 'show_blog', 'logout', 'index'] 
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("Sorry, you must be logged in to see that page")
        return redirect('/login')

#Log in, put user in session and send to /newpost, else return to /login w/ err msgs
@app.route('/login', methods=['POST', 'GET'])
def login():

    err_username = ''
    err_password = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first() #is user in db?
        
        if existing_user:
            if password == existing_user.password:
                session['username'] = username
                flash("Logged in")
                return redirect('/newpost') 
            else:
                err_password = "User password is not correct."
                return render_template('login.html', username=username, err_password=err_password)
        else:
            err_username = "That user name is not recognzed. Please try again or sign up for a new account."
            return render_template('login.html', page_title = "Log In To Your Blogz Account!", username=username, err_username=err_username)
        
    #if not POST, then simply displsy login.html template
    return render_template('login.html', page_title = "Log In To Your Blogz Account!")

#Register new users; put new user in session and send to /newpost, else return to signup.html w/ err msgs
@app.route('/signup', methods=['POST', 'GET'])
def signup():

    err_username = ''
    err_password = ''
    err_verify = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        existing_user = User.query.filter_by(username=username).first() #is user in db?
        
        #validate username input
        if not is_blank(username):
            if not has_space(username):
                if not is_wrongsize(username):
                    if not existing_user:
                        err_username = ''
                        username = username
                    else:
                        err_username = "That username is already taken."
                else:
                    err_username = "The user name must be at least 3 characters long."
            else:
                err_username = "The user name cannot contain spaces."
        else:
            err_username = "The user name cannot be blank."
            
        #validate password input
        if not is_blank(password):
            if not has_space(password):
                if not is_wrongsize(password):
                    err_password = ''
                    password = password
                else:
                    err_password = "The password must be at least 3 characters long."
            else:
                err_password = "The password cannot contain spaces."
        else:
            err_password = "Please enter a password."
            
        #validate verify password input
        if verify != password:
            err_verify = "The passwords do not match."
        else:
            pass
            
        if not err_username and not err_password and not err_verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', page_title = "Sign Up For A Blogz Account!",
                username = username, err_username=err_username, err_password=err_password, err_verify=err_verify)
                           
    #if not POST, then simply display register.html template    
    return render_template('signup.html', page_title = "Sign Up For A Blogz Account!")#display register.html template

#Get all users from db using User.id, and send that list to index.html for display
@app.route('/')
def index():

    err_users = ''

    users = User.query.order_by(User.id).all()
    if not users:
        err_users = "There are no users signed up yet."
        return render_template('index.html', err_users=err_users, title="Blog Users", page_title="Blog Users")
    else:
        return render_template('index.html', users=users, title="Blog Users", page_title="Blog Users")

#Based on GET param (user vs blog) send to display-post.html(blogID) or all-byuser.html(userID)
@app.route('/blog')
def show_blog():

    blogID = request.args.get('blogID')
    userID = request.args.get('userID')    

    if blogID:

        single_blog_entry = Blog.query.filter_by(id=blogID).first()
        user = User.query.filter_by(id=single_blog_entry.owner_id).first()
        return render_template('display-post.html', user=user, blog=single_blog_entry)
    
    if userID:
        user = User.query.filter_by(id=userID).first()
        blogs_list = Blog.query.filter_by(owner_id = userID).all()
        return render_template('all-byuser.html', page_title=user.username, blogs_list=blogs_list, user=user)
    
    blogs = Blog.query.all()
    users= User.query.all()
    return render_template('blog.html', title = "Blogz Entries", users=users, blogs=blogs)

#Validat iput, add post to db, and redirect to /blog w/ blogID (/blog will take that and send to display-post.html)
@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    err_title = ''
    err_body = ''

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title or title.strip() == '':
            #flash("Please add a title for your new post!")
            #return redirect('/newpost')
            err_title = "Please add a title!"
        if not body or body.strip() == '':
            #flash("Please add the content for your new post!")
            #return redirect('/newpost')
            err_body = "Please add your content!"

        if not err_title and not err_body:
            blog = Blog(title, body, owner)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?blogID=' + str(blog.id))
        else:
            return render_template('newpost.html', page_title = "Add a Blog Entry",
                title=title, err_title=err_title, body=body, err_body=err_body )

    return render_template('newpost.html', page_title="Add a Blog Entry")

@app.route('/logout')
def logout():
    if session.get('logged_in') is not None:
        del session['username']
        return redirect('/blog')
    else:
        flash("Okay, but there was no one logged in. No harm, no foul!")
        return redirect('/blog') 

#define global functions
def is_blank(field):
    if not field or not field.strip():
        return True

def is_wrongsize(field):
    if len(field) < 3:
        return True

def has_space(field):
    if ' ' in field:
        return True

def will_verify(f1, f2):
    if f1 == f2:
        return True

if __name__ == '__main__':
    app.run()