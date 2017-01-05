import settings

class Config(object):
    TESTING = False
    USER_APP_NAME = settings.app_name
    RESET_DB = settings.reset_db
    SQLALCHEMY_TRACK_MODIFICATIONS = True
