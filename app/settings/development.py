from basic import Config
import settings
from secret import local as sec

class DevelopmentConfig(Config):
    DEBUG = True
    if settings.s3:
        FLASKS3_DEBUG = True # force serving s3
    SQLALCHEMY_ECHO = True # Log any sqlalchemy error
    SECRET_KEY = sec['secret']
    if 'url' in sec['db']:
        SQLALCHEMY_DATABASE_URI = sec['db']['url']
    else:
        SQLALCHEMY_DATABASE_URI = ('postgresql://{}:{}@{}/{}').format(sec['db']['user'],
                                                                      sec['db']['password'],
                                                                      sec['db']['location'],
                                                                      sec['db']['name'])
    REALTIME_URL = sec['realtime']['url']
    REALTIME_CRED_PATH = sec['realtime']['cred_path']
    REALTIME_KEY = sec['realtime']['api_key']
