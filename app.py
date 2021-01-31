import os
from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from random import *
from werkzeug.utils import secure_filename

UPLOAD_FILES = '~/static/uploadFiles'
MAX_CONTENT_PATH = 1000000

app = Flask(__name__, static_url_path="/")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FILES'] = UPLOAD_FILES
app.config['MAX_CONTENT_PATH'] = MAX_CONTENT_PATH

db = SQLAlchemy(app)


def generate_SK():
    import string
    characters = string.ascii_letters + string.punctuation + string.digits
    random_string = "".join(choice(characters) for x in range(256))
    return random_string


random_SKstring = generate_SK()
app.config['SECRET_KEY'] = random_SKstring
login_manager = LoginManager(app)
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(40), nullable=False)


class throwData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credits = db.Column(db.Integer)
    gpa = db.Column(db.String(80))
    major = db.Column(db.String(80))
    graduation_year = db.Column(db.String(80))


@login_manager.user_loader
def load_user(uid):
    user = Users.query.get(uid)
    return user


@app.route('/')
def home():
    return render_template('Home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    from app import db
    db.create_all()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username).first()
        if user != None:
            if password == user.password:
                login_user(user)
                return redirect('/index')
    return render_template('login.html')


@app.route('/createAccount', methods=['GET', "POST"])
def createAccount():
    from app import db, Users
    db.create_all()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['password2']
        name = request.form['name']
        if password != confirm_password:
            render_template('password_error.html')
            redirect('/')
        else:
            db.session.add(Users(username=username, password=password, name=name))
            db.session.commit()
        return redirect('/login')
    return render_template("createAccount.html")


@app.route('/index')
@login_required
def index():
    user = current_user.username
    return render_template('index.html', user=user)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    from app import db, throwData
    db.create_all()
    if request.method == 'POST':
        file = request.files['File']
        fileName = secure_filename(file.filename)
        pathS = "static\\uploadFiles"
        fullPaths = os.path.join(pathS, fileName)
        file.save(fullPaths)
        print(fullPaths)
        f = open(fullPaths, "r")
        f.readline()
        dataString = f.readlines()
        for i in range(len(dataString)):
            line = dataString[i].split(",")
            hours = line[0]
            gpa = line[1]
            major = line[2]
            year = line[3]
            db.session.add(throwData(credits=hours, gpa=gpa, major=major, graduation_year=year))
            db.session.commit()

        return redirect('/database')
    return render_template('upload.html')


@app.route('/database')
@login_required
def database():
    throw_data = throwData.query.all()
    return render_template('database.html', throw_data=throw_data)


@app.errorhandler(404)
def error(err):
    return render_template('404.html', err=err)


@app.errorhandler(401)
def error(err):
    return render_template('401.html', err=err)


@app.route('/logout')
@login_required
def logout():
    login_user()
    redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
