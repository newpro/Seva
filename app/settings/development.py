from basic import Config
import settings

class DevelopmentConfig(Config):
    # -- basic --
    DEBUG = True
    if settings.s3_forceserve:
        FLASKS3_DEBUG = True # force serving s3
    SQLALCHEMY_ECHO = settings.sql_echo # Log any sqlalchemy error
    RESET_DB = True
