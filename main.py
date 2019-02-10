from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:admin@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '5!MB6orN&205m962'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def show_blog():

    id = request.args.get('id')
    if id:
        blog_entry = Blog.query.filter_by(id=id).first()

        return render_template('display-post.html', blog=blog_entry)
    
    posts = Blog.query.all()
    return render_template('blog.html', title = "Build a Blog", posts = posts)

@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():

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
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id=' + str(new_post.id))
        else:
            return render_template('newpost.html', page_title = "Add a Blog Entry",
                title=title, err_title=err_title, body=body, err_body=err_body )

    return render_template('newpost.html', page_title="Add a Blog Entry")


    


if __name__ == '__main__':
    app.run()