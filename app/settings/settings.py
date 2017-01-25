# Your app name
app_name = 'flaskboost'

# Safeguard for reset db (relational and realtime) or not. False can guard against dev mistake to erase data in production server
reset_db = True

# Force to serve remote s3 in development for testing propose
s3 = False

# Enable 24 hours caching
# If True, recommand to change static file name by each releases (yahoo guide for static caching)
s3_caching = False

# Store user details to Mongo db everytime a new user login via social platforms
# If true, additional Mongo db connection has to be set in secrets
store_user = True

# Charging currency
# Depend on countries, check out stripe guideline: 
# https://support.stripe.com/questions/which-currencies-does-stripe-support#supportedcurrencies
payment_enabled = True
payment_currency = 'cad'
store_payment = True
