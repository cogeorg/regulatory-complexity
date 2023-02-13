from flask import Flask
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

from .config import Config
from .models import db, login
from .routes import routes


app = Flask(__name__)
app.register_blueprint(routes)
app.config.from_object(Config)

db.init_app(app)
login.init_app(app)

with app.app_context():
    db.create_all()

migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
