from flask import Flask, render_template, request, session, config, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import requests
import validators

app =Flask(__name__)
app.secret_key = os.urandom(16)

################################### SQL ALCHEMY CONFIGURATION ################################
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
db=SQLAlchemy(app)
Migrate(app,db)
################################### SQL ALCHEMY CONFIGURATION ################################


################################### CREATE A MODEL ################################
class User(db.Model):
    __tablename__ = 'userdata'
    id =db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(255), unique=True, nullable=False)
    email= db.Column(db.String(255), unique=True, nullable= False)
    password=db.Column(db.String(255), nullable=False)
    def __init__(self, username, email, password):
        self.username= username
        self.email= email
        self.password= password

    def __repr__(self):
        return "Hello {} Welcome to our website".format(self.username)
        
################################### CREATE A MODEL ################################


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email= request.form.get('email')
        password= request.form.get('password')

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            return redirect(url_for('dashboard', username=user.username))
        else:
            return redirect(url_for('register'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        email= request.form.get('email')
        password= request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            return redirect(url_for('login'))
        else:
            new_user= User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('dashboard', username=username))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/urlform')
def urlform():
    return render_template("urlform.html")


@app.route("/shorten_url", methods=["POST"])
def shorten_url():
    url = request.form["url"]

    if not validators.url(url):
        return render_template("urlform.html", error="Invalid URL")

    try:
        response = requests.head(url)
        if response.status_code >= 400:
            return render_template("urlform.html", error="Unreachable URL")
    except requests.exceptions.RequestException as e:
        return render_template("urlform.html", error="Unreachable URL")

    tinyurl_api = "https://tinyurl.com/api-create.php?url="
    short_url = requests.get(tinyurl_api + url).text.strip()

    # Store the original and shortened URLs in the session
    session.setdefault('urls', []).append({'original_url': url, 'shortened_url': short_url})

    return render_template("urlform.html", redirect_url=short_url)


@app.route("/history")
def history():
    urls = session.get('urls', [])

    return render_template("history.html", urls=urls)

@app.route("/home")
def navigation():
    return render_template('home.html')

@app.route('/layout')
def llayout():
    return render_template('layout.html')

if __name__=='__main__':
    app.run(debug=True)