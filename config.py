import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'proudly-developed-by-NotNull-team'
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:rootpassword@db/mydatabase'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace(
        'postgres://', 'postgresql://')  or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_FOLDER = os.path.join(basedir, 'app', 'static', 'images')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')