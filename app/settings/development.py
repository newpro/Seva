from basic import Config
import settings
from secret import local as sec

class DevelopmentConfig(Config):
    # -- basic --
    DEBUG = True
    if settings.s3_forceserve:
        FLASKS3_DEBUG = True # force serving s3
    SQLALCHEMY_ECHO = settings.sql_echo # Log any sqlalchemy error
    SECRET_KEY = sec['secret']
    # -- DB --
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
    # -- mongo --
    if settings.mongo:
        MONGODB_HOST = sec['mongo']['host']
        MONGODB_PORT = sec['mongo']['port']
    # -- oauth --
    if 'oauth' in sec:
        OAUTHS = {}
        if 'twitter' in sec['oauth']:
            OAUTHS['twitter'] = {
                'id': sec['oauth']['twitter']['key'],
                'secret': sec['oauth']['twitter']['secret']
            }
        if 'facebook' in sec['oauth']:
            OAUTHS['facebook'] = {
                'id': sec['oauth']['facebook']['key'],
                'secret': sec['oauth']['facebook']['secret']
            }
    # -- payment --
    if settings.payment:
        STRIPE_SECRET = sec['stripe']['secret']
        STRIPE_PUBLIC = sec['stripe']['public']
