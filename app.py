from flask import Flask,request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  email = db.Column(db.String(50))
  password = db.Column(db.String(50))

@app.route('/signup', methods=['POST'])
def signup():
    print(12)
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    
    return "pk"

if __name__ == '__main__':
  app.run(debug=True)
