from flask import Flask
app = Flask(__name__)

# -- Import settings --
import os
try:
    RUNTIME = os.environ['RUNTIME']
except:
    RUNTIME = 'development'
    print '--!! WARNING: No RUNTIME find, use development !!--'

# -- Load environment variables --
app.config['RUNTIME'] = RUNTIME
from settings.loader import Loader
loader = Loader(RUNTIME, app.config)

# -- Load runtime specific configs --
if RUNTIME == 'development':
    from settings import development
    app.config.from_object(development.DevelopmentConfig)
elif RUNTIME == 'production':
    from settings import production
    app.config.from_object(production.ProductionConfig)
elif RUNTIME == 'testing':
    from settings import testing
    app.config.from_object(testing.TestingConfig)
else:
    raise Exception('RUNTIME not recognized, have to be one of development / production / testing')

# -- Expose variables to sub-modules --
# ---- relational db ----
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
# ---- relational db utlities ----
from utilities import DB_util
db_util = DB_util(db)

# ---- load location parse support
from geopy.geocoders import Nominatim
geolocator = Nominatim() # expose

# ---- load schema ----
import dbs
# ---- load Amazon static support ----
from flask_s3 import FlaskS3
s3 = FlaskS3()
s3.init_app(app)
# ---- load mongo support ----
if loader.enabled('mongo'):
    from pymongo import MongoClient
    app.mongo = MongoClient(app.config['MONGO_HOST'],
                            int(app.config['MONGO_PORT']))[app.config['USER_APP_NAME']]
# ---- load stripe support ----
import stripe
if loader.enabled('stripe'):
    stripe.api_key = app.config['STRIPE_SECRET']

# -- Pre operations --
@app.before_first_request
def setup(*args, **kwargs):
    print app.config['RESET_DB']
    if app.config['RESET_DB']:
        from utilities import Preload
        preload = Preload(db_schema=dbs,
                          db_util=db_util)
        preload.reset_db(relational=False)

# -- Views --
import views
