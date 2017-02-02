import settings
from secret import global_ as g

class Config(object):
    # ---- Basic ----
    DEBUG = False
    USER_APP_NAME = settings.app_name
    CSRF_ENABLED = True
    RESET_DB = settings.reset_db
    SQLALCHEMY_TRACK_MODIFICATIONS = True # SQL debug printout
    # ---- Default Values ----
    OAUTHS = {}
    # ---- Static Serving ----
    FLASKS3_ONLY_MODIFIED = True # only upload modified
    if settings.s3_caching:
        FLASKS3_HEADERS = {
            'Expires': 'Thu, 15 Apr 2200 20:00:00 GMT',
            'Cache-Control': 'max-age=86400',
        }
    if 'aws' in g:
        AWS_ACCESS_KEY_ID = g['aws']['key']
        AWS_SECRET_ACCESS_KEY = g['aws']['secret']
        FLASKS3_BUCKET_NAME = g['aws']['bucket']
        if 'region' in g['aws']:
            FLASKS3_REGION = g['aws']['region']
    # ---- USER ----
    USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    USER_REGISTER_TEMPLATE = 'flask_user/login_or_register.html'
    STORE_USER = settings.store_user
    # Warning: if oauth also provide in runtime specific settings, this will be overwrite
    if 'oauth' in g:
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
    if settings.payment:
        PAYMENT_ENABLED = True
        CURRENCY = settings.payment_currency
        STORE_PAYMENT = settings.store_payment
    # ---- Twilio Support ----
    if settings.twilio:
        TWILIO_ENABLED = True
        if 'twilio' in g:
            TWILIO_ACCOUNT_SID = g['twilio']['sid']
            TWILIO_API_KEY = g['twilio']['key']
            TWILIO_API_SECRET = g['twilio']['secret']
            TWILIO_CONFIGURATION_SID = g['twilio']['config_sid']
