from basic import Config

class TestingConfig(Config):
    TESTING = True
    RESET_DB = True # default to reset db before test
