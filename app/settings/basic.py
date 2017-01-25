import settings
from secret import global_ as g

class Config(object):
    DEBUG = False
    USER_APP_NAME = settings.app_name
    RESET_DB = settings.reset_db
    SQLALCHEMY_TRACK_MODIFICATIONS = True # SQL debug printout
    FLASKS3_ONLY_MODIFIED = True # only upload modified
    if settings.s3_caching:
        FLASKS3_HEADERS = {
            'Expires': 'Thu, 15 Apr 2200 20:00:00 GMT',
            'Cache-Control': 'max-age=86400',
        }

    if g['aws']:
        AWS_ACCESS_KEY_ID = g['aws']['key']
        AWS_SECRET_ACCESS_KEY = g['aws']['secret']
        FLASKS3_BUCKET_NAME = g['aws']['bucket']
        if 'region' in g['aws']:
            FLASKS3_REGION = g['aws']['region']

    # ---- USER ----
    USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    USER_REGISTER_TEMPLATE = 'flask_user/login_or_register.html'
    STORE_USER = settings.store_user
    OAUTHS = {}
    if g['oauth']:
        if 'twitter' in g['oauth']:
            OAUTHS['twitter'] = {
                'id': g['oauth']['twitter']['key'],
                'secret': g['oauth']['twitter']['secret']
            }
        if 'facebook' in g['oauth']:
            OAUTHS['facebook'] = {
                'id': g['oauth']['facebook']['key'],
                'secret': g['oauth']['facebook']['secret']
            }
    # ---- Payment ----
    if settings.payment_enabled:
        PAYMENT_ENABLED = True
        CURRENCY = settings.payment_currency
        STORE_PAYMENT = settings.store_payment
