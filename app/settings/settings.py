# Your app name
app_name = 'flaskboost'

# Safeguard for reset db (relational and realtime) or not. False can guard against dev mistake to erase data in production server
reset_db = True

# log sql operations
sql_echo = True

# AWS 24 hours caching
s3_caching = False

# Force to serve remote s3 in development for testing propose
s3_forceserve = False

# Depend on countries, check out stripe guideline: 
# https://support.stripe.com/questions/which-currencies-does-stripe-support#supportedcurrencies
payment_currency = 'cad'
