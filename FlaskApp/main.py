from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key = params["secret_key"]
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/windowsshortkey'
db = SQLAlchemy(app)



class Contacts(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(80),unique = False, nullable= False)
    Email = db.Column(db.String(80),unique = True, nullable= False)
    Mobile = db.Column(db.String(80),unique = True, nullable= False)
    Messge = db.Column(db.String(80),unique = False, nullable= False)
    date = db.Column(db.String(80),unique = False, nullable= True)

class Posts(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80),unique = False, nullable= False)
    tagline = db.Column(db.String(80),unique = False, nullable= False)
    slug = db.Column(db.String(80),unique = True, nullable= False)
    content = db.Column(db.String(1000),unique = True, nullable= False)
    imgfile = db.Column(db.String(1000),unique = True, nullable= False)
    date = db.Column(db.String(80),unique = False, nullable= True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['no-of-post']]
    return render_template("index.html",params=params,posts =posts)
    #return ("Semant")

@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/contact",methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('Name')
        mobile = request.form.get('Mobile')
        email = request.form.get('Email')
        message = request.form.get('Message')
        entry = Contacts(Name = name,Email =email,Mobile = mobile,Messge = message, date= datetime.now() )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + mobile
                          )

    return render_template('contact.html',params=params)
       
    

@app.route("/post/<string:post_slug>",methods=['GET'])
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post = post)


@app.route("/semant")
def semant():
    return render_template('semant.html',params=params)

@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if ('user' in session and session['user']==params["password"]):
        return render_template('dashboard.html',params=params,posts = posts)


    if(request.method=='POST'):
        username = request.form.get("uname")
        password = request.form.get("pass")
        if(username==params["admin"] and password==params["password"]):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params,posts = posts)
    
    else:
        return render_template('login.html',params=params)
        
@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user']==params["password"]):
        if request.method=='POST':
            Title = request.form.get("title")
            Tagline = request.form.get("tagline")
            Slug = request.form.get("slug")
            Content = request.form.get("content")
            Image = request.form.get("file")
            if sno=='0':
                post = Posts(title = Title, tagline = Tagline, slug = Slug,content = Content,imgfile = Image,date = datetime.now())
                db.session.add(post)
                db.session.commit()     
        return render_template('edit.html',params=params) 

        
    
@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
     if ('user' in session and session['user']==params["password"]):
         post = Posts.query.filter_by(sno = sno).first()
         db.session.delete(post)
         db.session.commit()
     return redirect('/dashboard')
    



app.run(debug=True)