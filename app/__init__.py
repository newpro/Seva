from flask import Flask
app = Flask(__name__)

# -- Import settings --
import os
try:
    RUNTIME = os.environ['RUNTIME']
    app.config['RUNTIME'] = RUNTIME
except:
    raise Exception('Environmental variable "RUNTIME" has not been set (try export RUNTIME="development")')

if RUNTIME == 'development':
    from settings import development
    app.config.from_object(development.DevelopmentConfig)
elif RUNTIME == 'production':
    from settings import production
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'] # dynamic assigned
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
# ---- load schema ----
import dbs, firedbs
# ---- load Amazon static support ----
from flask_s3 import FlaskS3
s3 = FlaskS3()
s3.init_app(app)
# ---- load mongo support ----
if app.config['MONGODB_HOST']:
    from pymongo import MongoClient
    app.mongo = MongoClient(app.config['MONGODB_HOST'],
                            app.config['MONGODB_PORT'])[app.config['USER_APP_NAME']]
# ---- load stripe support ----
import stripe
if app.config['PAYMENT_ENABLED']:
    stripe.api_key = app.config['STRIPE_SECRET']

# -- Pre operations --
@app.before_first_request
def setup(*args, **kwargs):
    if app.config['RESET_DB']:
        from utilities import Preload
        preload = Preload(db_schema=dbs,
                          fire_schema=firedbs,
                          db_util=db_util)
        preload.reset_db(relational=False, realtime=False)

# -- Views --
import views
