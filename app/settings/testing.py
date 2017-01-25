from basic import Config
import secret as sec

class TestingConfig(Config):
    TESTING = True
    RESET_DB = True # default to reset db before test
