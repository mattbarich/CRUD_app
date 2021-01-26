from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from random import *

app = Flask(__name__, static_url_path="/")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def generate_SK():
    random_string = ''
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


@login_manager.user_loader
def load_user(uid):
    user = Users.query.get(uid)
    return user


@app.route('/', methods=['GET', 'POST'])
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
    return render_template("createAccount.html")


@app.route('/index')
@login_required
def index():
    user = current_user.username
    return render_template('index.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
