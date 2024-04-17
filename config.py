import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    @staticmethod
    def get_db_uri():
        res = os.environ.get('DATABASE_URL')
        if res:
            res = res.replace('postgres://', 'postgresql://')
        else:
            res = 'sqlite:///' + os.path.join(basedir, 'app.db')

        return res
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'proudly-developed-by-NotNull-team'
    SQLALCHEMY_DATABASE_URI = get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_FOLDER = os.path.join(basedir, 'app', 'static', 'images')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

