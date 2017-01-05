from flammable import Model, Flammable, ReflectModel, ReverseModel
from time import time
from errs import PayloadErr, IntegrityErr, ReflectErr, APIForbiddenErr, ReverseErr
from . import dbs, app

db = Flammable(app.config['REALTIME_URL'],
               'app/settings/{}'.format(app.config['REALTIME_CRED_PATH']),
               app.config['REALTIME_KEY']
               )

Model.db = db

# CRUMB: add additional realtime models here

def _remove_db():
    # CRUMB: call any additional realtime models _rebuild functions here
    pass

def _init_data():
    fetch = dbs.fetch
    # CRUMB: get dependency from relational db and fetch them here
    # CRUMB: add additional model tests here
    pass

# ---- Supports ----
def _RESET_DB():
    """
    Delete and reset all DB Data
    """
    # CRUMB: Call all _rebuild functions to additional tables here
    _remove_db()
    _init_data()

# -- Builder --
# CRUMB: add building sequence helpers here

# -- Doggy --
# CRUMB: add fetch path and getter helpers here


