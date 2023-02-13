from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

login = LoginManager()
login.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    businessemail = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    submissions = db.relationship("Submission", backref="author", lazy="dynamic")
    affiliation = db.Column(db.String(64), index=True, unique=True)
    student_id = db.Column(db.String(64), index=True, unique=True)
    sex = db.Column(db.String(64), index=True)
    age = db.Column(db.String(64), index=True)
    education = db.Column(db.String(64), index=True)
    year = db.Column(db.String(64), index=True)
    area = db.Column(db.String(120), index=True)
    institution = db.Column(db.String(256), index=True)
    usertype = db.Column(db.String(256), index=True)
    experience = db.Column(db.String(128), index=True)
    years_experience = db.Column(db.String(128), index=True)

    def __repr__(self):
        return "<User {}>".format(self.username)

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
    question = db.Column(db.VARCHAR(120))
    answer = db.Column(db.VARCHAR(120))
    correctanswer = db.Column(db.Float())
    verifyanswer = db.Column(db.Boolean())
    totaltime = db.Column(db.VARCHAR(120))
    regulation = db.Column(db.VARCHAR(120))
    balance_sheet = db.Column(db.VARCHAR(120))
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    usertype = db.Column(db.String(120))
    student_id = db.Column(db.String(128))
    affiliation = db.Column(db.String(128))

    def __repr__(self):
        return "<Submission {}>"


class CorrectAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correctanswer = db.Column(db.Float())
    n_reg = db.Column(db.Integer())

    def __repr__(self):
        return "<CorrectAnswer {}".format(self.correctanswer)
