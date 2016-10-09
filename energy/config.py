# Flask Config

class Configuration(object):
    DEBUG = True
    SECRET_KEY = 'PASSWORD'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False