from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random
import re
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Hello'
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'f5f2374c7de0da'
app.config['MAIL_PASSWORD'] = 'f609186e4ec7e1'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(30),unique=True)
    password = db.Column(db.String(50))
    otp = db.Column(db.Integer)

def send_email(email, otp):
    with app.app_context():
        message = Message(
            subject='OTP Verification',
            sender=('Your Name', 'your_email@example.com'),
            recipients=[email])
        message.html = f'<strong>Your OTP is: {otp}</strong>'
        mail.send(message)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dash')
def dash():
    return render_template('dashboard.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['email'] = user.email
            session['verified'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', exits="Invalid username or password")
    else:
        # check if user is already logged in, if yes, redirect to dashboard
        if 'email' in session and session['verified']:
            return redirect(url_for('dashboard'))
        else:
            # render the login page
            return render_template('login.html')


@app.route('/signup', methods=['POST'])
def signup1():
    name = request.form['fullname']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # check if email or username already exists in the database
    user_email = User.query.filter_by(email=email).first()
    user_username = User.query.filter_by(username=username).first()
    if user_email:
        return render_template('signup.html', exits="Email already exits")
    if user_username:
        return render_template('signup.html', exits="Username already taken")

    # check if password and confirm password match
    password_regex = r"^(?=.*[A-Z])(?=.*[@#$%^&+=])(?=.*[0-9])(?=.*[a-z]).{6,}$"
    if password != confirm_password:
        return render_template('signup.html', exits="Password do not match")

    # check if password meets criteria
    if not re.match(password_regex, password):
        return render_template('signup.html', exits="Password should be: Exam@123")

    # generate OTP and create new user in the database
    otp = random.randint(100000, 999999)
    user = User(name=name, email=email, username=username, password=password, otp=otp)
    db.session.add(user)
    db.session.commit()
    send_email(email, otp)

    # store user information in session
    session['email'] = email
    session['verified'] = False

    return render_template('verify.html', email=email)


@app.route('/verify', methods=['POST'])
def verify():
    email = session['email']
    otp = request.form['otp']
    user = User.query.filter_by(email=email).first()
    if user and str(user.otp) == otp:
        user.otp = None
        db.session.commit()
        session['verified'] = True
        return redirect(url_for('dashboard'))
    return render_template('verify.html',error="OTP not matched")


@app.route('/dashboard', methods=['GET'])
def dashboard():
    # check if user is logged in, if not redirect to signup page
    if 'email' not in session or not session['verified']:
        return redirect(url_for('signup1'))
    else:
        # render the dashboard page
        return render_template('dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5050)
