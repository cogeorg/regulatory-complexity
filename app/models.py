from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    db.create_all()
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    submissions = db.relationship('Submission', backref = 'author', lazy = 'dynamic')
    student_id = db.Column(db.String(64), index = True, unique = True)
    sex = db.Column(db.String(64), index = True)
    age = db.Column(db.String(64), index = True)
    education = db.Column(db.String(64), index = True)
    year = db.Column(db.String(64), index = True)
    area = db.Column(db.String(120), index = True)
    institution = db.Column(db.String(256), index = True)
    experience = db.Column(db.String(128), index = True)
    years_experience = db.Column(db.String(128), index = True)

    def __repr__(self) :
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

def load_correctanswer(correctanswer):
    return User.query.get(correctanswer)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120))
    answer = db.Column(db.String(120))
    correctanswer = db.Column(db.Float())
    verifyanswer = db.Column(db.Float())
    # timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    totaltime = db.Column(db.String(120))
    regulation = db.Column(db.String(120))
    balance_sheet = db.Column(db.String(120))
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Submission {}>'

class CorrectAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correctanswer = db.Column(db.Float())
    n_reg = db.Column(db.Integer())

    def __repr__(self):
        return '<CorrectAnswer {}'.format(self.correctanswer)

db.create_all()