#
# Environment loader
#
from os import environ

def get(env_var):
    """
    Raise exception when can not fetch a env variable
    """
    return environ[env_var]

class Loader():
    """
    Propose of this class:

    * Smart load the environment
    * Hold information and provides access abilities for human code readbility

    * Local: load from .env
    * Production: load from environment variables
    """
    def __init__(self, runtime, config_pointer=None):
        """
        Init the loader, and optionally passin to config directly
        """
        if runtime == 'development':
            # load from local .env file
            from dotenv import load_dotenv, find_dotenv
            load_dotenv(find_dotenv())

        # load from environment variables
        self.secret = get('SECRET_KEY')
        self.db_url = get('DATABASE_URL')
        self.tps = [] # mark which third party service are enabled
        keys = ['SECRET_KEY', 'DATABASE_URL'] # wait to write into config pointer

        # ---- AWS ----
        try:
            self.aws = {
                'key': get('AWS_ACCESS_KEY_ID'),
                'secret': get('AWS_SECRET_ACCESS_KEY'),
                'bucket': get('FLASKS3_BUCKET_NAME')
            }
            keys.extend(['AWS_ACCESS_KEY_ID',
                         'AWS_SECRET_ACCESS_KEY',
                         'FLASKS3_BUCKET_NAME'])  
        except:
            pass
        try:
            self.aws['region'] = get('FLASKS3_REGION')
        except:
            pass

        # ---- Firebase ----
        try:
            self.firebase = {
                'id': get('FIREBASE_ID'),
                'url': get('FIREBASE_DB_URL'),
                'account': get('FIREBASE_SERVICE_ACCOUNT'),
                'key': get('FIREBASE_PRIVATE_KEY'),
                'api': get('FIREBASE_API')
            }
            keys.extend(['FIREBASE_ID',
                         'FIREBASE_SERVICE_ACCOUNT',
                         'FIREBASE_PRIVATE_KEY',
                         'FIREBASE_API',
                         'FIREBASE_DB_URL'])
            self.tps.append('firebase')
        except:
            pass
        try:
            # optional fields
            self.firebase['cred_path'] = get('FIREBASE_CRED_PATH')
        except:
            pass

        # ---- Oauth ----
        # -- Twitter --
        try:
            self.twitter = {
                'id': get('TWITTER_KEY'),
                'secret': get('TWITTER_SECRET')
            }
            keys.extend(['TWITTER_KEY', 'TWITTER_SECRET'])
            self.tps.append('twitter')
        except:
            pass
        # -- Facebook --
        try:
            self.facebook = {
                'id': get('FACEBOOK_KEY'),
                'secret': get('FACEBOOK_SECRET')
            }
            keys.extend(['FACEBOOK_KEY', 'FACEBOOK_SECRET'])
            self.tps.append('facebook')
        except:
            pass

        # ---- Payment ----
        try:
            self.stripe = {
                'id': get('STRIPE_SECRET'),
                'public': get('STRIPE_PUBLIC')
            }
            keys.extend(['STRIPE_SECRET', 'STRIPE_PUBLIC'])
            self.tps.append('stripe')
        except:
            pass

        # ---- Twilio ----
        try:
            self.twilio = {
                'sid': get('TWILIO_ACCOUNT_SID'),
                'key': get('TWILIO_API_KEY'),
                'secret': get('TWILIO_API_SECRET'),
                'config_sid': get('TWILIO_CONFIGURATION_SID')
            }
            keys.extend(['TWILIO_ACCOUNT_SID',
                         'TWILIO_API_KEY',
                         'TWILIO_API_SECRET',
                         'TWILIO_CONFIGURATION_SID'])
            self.tps.append('twilio')
        except:
            pass

        # ---- Mongo ----
        try:
            self.mongo = {
                'secret': get('MONGO_HOST'),
                'port': get('MONGO_PORT')
            }
            keys.extend(['MONGO_HOST', 'MONGO_PORT'])
            self.tps.append('mongo')
        except:
            pass

        # ---- Load all into config ----
        if config_pointer:
            for key in keys:
                config_pointer[key] = get(key)
            # additional configs
            config_pointer['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']

    def enabled(self, third_party):
        """
        Check if a thrid party is enabled
        """
        return third_party in self.tps

    def get_oauth(self, third_party):
        if third_party == 'facebook':
            return self.facebook
        if third_party == 'twitter':
            return self.twitter
        raise Exception('Oauth third party not find: {}'.format(third_party))
