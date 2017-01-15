from basic import Config
from secret.secrets import remote as sec

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True # Log any sqlalchemy error
    SECRET_KEY = sec['secret']
    if sec['db']['url']:
        SQLALCHEMY_DATABASE_URI = sec['db']['url']
    else:
        SQLALCHEMY_DATABASE_URI = ('postgresql://{}:{}@{}/{}').format(sec['db']['user'],
                                                                      sec['db']['password'],
                                                                      sec['db']['location'],
                                                                      sec['db']['name'])
    REALTIME_URL = sec['realtime']['url']
    REALTIME_CRED_PATH = sec['realtime']['cred_path']
    REALTIME_KEY = sec['realtime']['api_key']
