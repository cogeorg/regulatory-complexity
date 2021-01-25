import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgres://tmieypabvktvoo:2cf2702c66fe446f3ab92e36bd1aa88f71205f6fa5c100ae948795c9df1ae72f@ec2-107-20-104-234.compute-1.amazonaws.com:5432/d6fgddh0b2no73') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
