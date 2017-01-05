from basic import Config
import secret as sec

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = sec.local_secret
    SQLALCHEMY_DATABASE_URI = ('postgresql://{}:{}@{}/{}').format(sec.local_db_user,
                                                                  sec.local_db_password,
                                                                  sec.local_db_location,
                                                                  sec.local_db_name)
    REALTIME_URL = sec.local_realtime_url
    REALTIME_CRED_PATH = sec.local_realtime_cred_path
    REALTIME_KEY = sec.local_realtime_api_key
