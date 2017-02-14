import settings
from secret import global_ as g

class Config(object):
    # ---- Basic ----
    DEBUG = False
    USER_APP_NAME = settings.app_name
    CSRF_ENABLED = True
    RESET_DB = settings.reset_db
    SQLALCHEMY_TRACK_MODIFICATIONS = True # SQL debug printout
    # ---- Static Serving ----
    FLASKS3_ONLY_MODIFIED = True # only upload modified
    if settings.s3_caching:
        FLASKS3_HEADERS = {
            'Expires': 'Thu, 15 Apr 2200 20:00:00 GMT',
            'Cache-Control': 'max-age=86400',
        }
    # ---- USER ----
    USER_LOGIN_TEMPLATE = 'flask_user/login_or_register.html'
    USER_REGISTER_TEMPLATE = 'flask_user/login_or_register.html'
    # ---- Payment ----
    CURRENCY = settings.payment_currency
