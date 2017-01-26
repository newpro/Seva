from basic import Config
from secret import remote as sec

class ProductionConfig(Config):
    # -- basic --
    DEBUG = False
    SECRET_KEY = sec.remote_secret
    # -- DB --
    if sec['db']['url']:
        SQLALCHEMY_DATABASE_URI = sec['db']['url']
    else:
        SQLALCHEMY_DATABASE_URI = ('postgresql://{}:{}@{}/{}').format(sec['db']['user'],
                                                                      sec['db']['password'],
                                                                      sec['db']['location'],
                                                                      sec['db']['name'])
    RESET_DB = False # default not allows reset DB
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
