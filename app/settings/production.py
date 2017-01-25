from basic import Config
from secret import remote as sec

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = sec.remote_secret
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
    if settings.store_user:
        MONGODB_HOST = sec['mongo']['host']
        MONGODB_PORT = sec['mongo']['port']
    if settings.payment_enabled:
        STRIPE_SECRET = sec['stripe']['secret']
        STRIPE_PUBLIC = sec['stripe']['public']
