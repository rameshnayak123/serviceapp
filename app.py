from flask import Flask, render_template, request, redirect, url_for
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
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['fullname']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # check if email or username already exists in the database
    user_email = User.query.filter_by(email=email).first()
    user_username = User.query.filter_by(username=username).first()
    if user_email:
        return render_template('index.html',exits="Email already exits")
    if user_username:
        return render_template('index.html',exits="Username already taken")

    # check if password and confirm password match
    password_regex = r"^(?=.*[A-Z])(?=.*[@#$%^&+=])(?=.*[0-9])(?=.*[a-z]).{6,}$"
    if password != confirm_password:
        return render_template('index.html',exits="Password do not match")
    
    # check if password meets criteria
    if not re.match(password_regex, password):
        return render_template('index.html',exits="Password should be: Exam@123")

    # generate OTP and create new user in the database
    otp = random.randint(100000, 999999)
    user = User(name=name, email=email, username=username, password=password, otp=otp)
    db.session.add(user)
    db.session.commit()
    send_email(email, otp)
    return render_template('verify.html', email=email)

@app.route('/ver')
def ver():
    return render_template('verify.html')

@app.route('/verify', methods=['POST'])
def verify():
    email = request.form['email']
    otp = request.form['otp']
    user = User.query.filter_by(email=email).first()
    if user and str(user.otp) == otp:
        user.otp = None
        db.session.commit()
        return 'Email verification successful'
    return 'Invalid OTP'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
