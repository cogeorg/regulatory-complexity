import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Comment out below when in heroku environment
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL").replace(
        "postgres://", "postgresql://"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
