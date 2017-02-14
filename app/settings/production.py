from basic import Config
import settings

class ProductionConfig(Config):
    # -- basic --
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # -- DB --
    RESET_DB = False # default not allows reset DB
    SQLALCHEMY_ECHO = settings.sql_echo
