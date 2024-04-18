import logging
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from .commands import register_commands

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'staff_login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
register_commands(app)
if app.config['LOG_TO_STDOUT']:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Backend Startup')

# must place it at the end, to prevent circular import
from app import routes, models
