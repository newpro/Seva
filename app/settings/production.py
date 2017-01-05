from basic import Config
import secret as sec

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = sec.remote_secret
    SQLALCHEMY_DATABASE_URI = ('postgresql://{}:{}@{}/{}').format(sec.remote_db_user,
                                                                  sec.remote_db_password,
                                                                  sec.remote_db_location,
                                                                  sec.remote_db_name)
    RESET_DB = False # default not allows reset DB
    REALTIME_URL = sec.remote_realtime_url
    REALTIME_CRED_PATH = sec.remote_realtime_cred_path
    REALTIME_KEY = sec.remote_realtime_api_key
