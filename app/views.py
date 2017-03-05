from flask import render_template, request, url_for, current_app, redirect, flash, abort, jsonify, make_response
from flask.views import MethodView
from flask_user import login_required, roles_required, current_user
from . import app, dbs, db, forms, db_util, loader
from flask_s3 import create_all
from flask_login import login_user, logout_user
import uuid
from twilio.access_token import AccessToken as TAccessToken, VideoGrant
# -- jwt support --
from python_jwt import generate_jwt
import Crypto.PublicKey.RSA as RSA
import datetime
import json
from flask_cors import cross_origin

# ---- Helper functions ----
def build_jwt(iss, sub, uid, aud, claims, private_key, encrption_method="RS256", exp_min=60):
    """
    Function for create general JWT token, read:

    * w3c JWT: https://www.w3.org/TR/webcrypto-usecases/
    * py-jwt: https://jwt.io/
    """
    try:
        payload = {
            "iss": iss,
            "sub": sub,
            "aud": aud,
            "uid": uid,
            "claims": claims
        }
        exp = datetime.timedelta(minutes=exp_min)
        return generate_jwt(payload, RSA.importKey(private_key), encrption_method, exp)
    except Exception as e:
        raise Exception("JWT: Error creating custom token: {}".format(e.message))


def write_charge(charge, unique_id, user_id, product_id, email=None):
    """
    Write the charge record to DB
    """
    mongo_id = None
    if loader.enabled('mongo'):
        mongo_id = str(app.mongo['charges'].insert_one(charge).inserted_id)
    purchase = dbs.Purchase(uuid=unique_id,
                            email=email,
                            mongo_id=mongo_id,
                            customer_id=user_id,
                            product_id=product_id).pip()
    dbs.Delivery(purchase=purchase).add()

def dump_user(user):
    """
    dump data of current_user to view
    """
    return {'username': user.username,
            'email': user.email,
            'roles': [{'name': x.name,
                       'color': x.color,
                       'icon': x.icon
                       } for x in user.roles]
            }

def get_dependency_path(dependency, user_id): # DUMMY
    base_path = '' 
    if dependency == 'chat': 
        base_path = 'chats' 
    elif dependency == 'draw': 
        base_path = 'draws' 
    else: 
        raise Exception('no dependency') 
    return '{}/{}'.format(base_path, 1) # dummy

# ---- Management Views ----
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
# -- admin restrictions --
column_restrictions = {
    'User': ('password', 'reset_password_token', ),
}

class AdminView(ModelView):
    column_auto_select_related = True

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.has_role('admin')
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('user.login', next=request.url))

class UserAdmin(AdminView):
    column_exclude_list = column_restrictions['User']
    form_excluded_columns = column_restrictions['User']

# -- load management views --
admin = Admin(app, name=app.config['USER_APP_NAME'], template_mode='bootstrap3')
admin.add_view(UserAdmin(dbs.User, db.session))
admin.add_view(AdminView(dbs.Role, db.session))
admin.add_view(AdminView(dbs.Purchase, db.session))
admin.add_view(AdminView(dbs.Delivery, db.session))
admin.add_view(AdminView(dbs.Product, db.session))

@app.route('/upload', methods=['POST', 'GET'])
@roles_required('admin')
def upload_all():
    form = forms.UploadAll()
    if form.validate_on_submit():
        create_all(app, filepath_filter_regex=form.filter_regex.data)
        flash('upload success')
    return render_template('admin/upload.html', form=form)

# ---- Non-Management Views ----
@app.route('/')
def index():
    return render_template('main/index.html', runtime=app.config['RUNTIME'])

@app.route('/playground')
@roles_required('admin')
def playground():
    return render_template('playground/index.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logout Complete', category='info')
    return redirect(url_for('index'))

# ---- OAuths Views ----
from oauths import OAuthBase
@app.route('/oauth/provider/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        flash('Already login', category='warning')
        return redirect(url_for('index'))
    oauth = OAuthBase.get_provider(provider)
    return oauth.authorize()

@app.route('/oauth/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        flash('Already login', category='warning')
        return redirect(url_for('index'))
    oauth = OAuthBase.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed', category='danger')
        return redirect(url_for('index'))
    user = dbs.User.query.filter_by(social_id=social_id).first()
    if not user:
        form = forms.SocialRegister()
        form.username.data = username
        form.email.data = email
        form.provider.data = provider
        return render_template('soc_user/finish.html', form=form, provider=provider)
    login_user(user, remember=form.remember.data)
    flash('Oauth Success', category='success')
    return redirect(url_for('index'))

@app.route('/oauth/finish', methods=['POST', 'GET'])
def oauth_finish():
    if not current_user.is_anonymous:
        flash('Already registered', category='warning')
        return redirect(url_for('index'))
    form = forms.SocialRegister()
    if request.method == 'POST' and form.validate():
        user = dbs.User(username=form.username.data, email=form.email.data,
                        first_name = form.first_name.data, last_name = form.last_name.data).pip()
        user.add_role('user')
        user.add_social(form.provider.data)
        flash('Register success!')
        login_user(user, remember=form.remember.data)
        flash('New User Login Success', category='success')
        return redirect(url_for('index'))
    return render_template('soc_user/finish.html', form=form, provider=provider)

# ---- Seva Views ----
@app.route('/profile_test')
@login_required
def profile_test():
    # assume current user var is set correctly
    # -- Mars the profile data --
    user_info = dump_user(current_user)
    locs = []
    for loc in current_user.locations:
        locs.append(loc.name)
    return render_template('seva_test/profile.html',
                           locs=locs,
                           user_info=user_info)

@app.route('/ai')
def cities():
    #return jsonify({
        #'cities': ['Toronto', 'Waterloo']
    #})
    results = {}
    # grab all locations
    locs = dbs.Location.query.all()
    for loc in locs:
        tmp_users = []
        for user in loc.users:
            tmp_users.append(user.username)
        results[loc.name] =  tmp_users
    return jsonify(results)

def get_one_service(service):
    package = dbs.Package.query.get(service.package)
    # write data
    s_data = {}
    s_data['id'] = service.id
    s_data['category'] = package.name
    s_data['title'] = service.title
    s_data['location'] = service.addr
    s_data['latitude'] = service.lat
    s_data['lon'] = service.lon
    if service.rush:
        s_data['price'] = package.price * 1.5
    else:
        s_data['price'] = package.price
    s_data['rush'] = service.rush
    s_data['url'] = package.url
    return s_data

@app.route('/data/map')
@app.route('/data/map/<sid>')
@cross_origin()
def map_points(sid=None):
    service_list = []
    if sid:
        service = dbs.Service.query.get(sid)
        return jsonify(get_one_service(service))
    for service in dbs.Service.query.all():
        # fetch package
        s_data = get_one_service(service)
        service_list.append(s_data)
    return jsonify({'data': service_list})

@app.route('/data/remove/<sid>')
@cross_origin()
def del_point(sid):
    service = dbs.Service.query.get(sid)
    if not service:
        return jsonify({'resp': 'fail to locate service'})
    db.session.delete(service)
    db_util.commit()
    return jsonify({'resp': 'success'}) 

def makeWebhookResult(req):
    if req.get("result").get("action") != "shipping.cost":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    zone = parameters.get("shipping-zone")
    cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}
    speech = "The cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }

def makeWebhookResult2(req):
    if req.get("result").get("action") != "service.upload":
        print '--- empty request---'
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    location = parameters.get("location")
    pack = parameters.get('packages')
    title = parameters.get('title')
    speech = "Your appointment has been published. location: {}, package: {}, title: {}".format(location, pack, title)    
    try:
        type_ = dbs.fetch('package', pack)
    except:
        speech = 'package not find'
    me = dbs.fetch('user', 'jan')
    if not title:
        title = 'request for help {}'.format(pack)
    try:
        me.request_service(title=title, package=type_.name, rush=False, addr=location)
    except:
        speech = 'Location can not be located :{}'.format(location)

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "agent"
    }

@app.route('/ai/hook', methods=['POST'])
@cross_origin()
def ai_hook():
    #data = request.values
    #try:
        #me = dbs.fetch('user', data['me'])
        #msg = data['msg']
        #type_ = dbs.fetch('package', data['type'])
        #rush = False
        #if 'rush' in data:
            #rush = data['rush']
        #addr=''
        #if 'addr' in data:
            #addr = data['addr']
    #except:
        #return jsonify({
            #'state': 'err',
            #'msg': 'Data format err'
        #})
    #if not me:
        #return jsonify({
            #'state': 'err',
            #'msg': 'Cannot find user'
        #})
    #if not type_:
        #return jsonify({
            #'state': 'err',
            #'msg': 'Cannot find package'
        #})
    #try:
        #me.request_service(title=msg, package=type_.name, rush=rush, addr=addr)
    #except:
        #return jsonify({
            #'state': 'err',
            #'msg': 'unknow error'
        #})
    ##return jsonify({
        ##'state': 'success',
        ##'msg': request.values
    ##})

    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult2(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

# ---- Stripe Views ----
from . import stripe

@app.route('/product/<product_id>', methods=['GET'])
@login_required
def stripe_payment(product_id):
    if not loader.enabled('stripe'):
        raise Exception('Stripe not enabled')
    product = dbs.Product.query.get(product_id)
    if (not product) or (not product.is_active):
        raise Exception('product not fit for sale')
    product_info = {
        'id': product.id,
        'name': 'Payment for {}'.format(product.name),
        'store': current_app.config['USER_APP_NAME'],
        'amount': product.price*100,
        'currency': product.currency,
        'digital': product.digital
    }
    # -- pre-set variables --
    user_email = None # user email used to charge
    if current_user.confirmed_at: # email confirmed
        user_email = current_user.email
    qc_form = None # if the user need to provide shipment info
    if current_user.get_stripe():
        qc_form = forms.QuickCharge()
        qc_form.product_id.data = product_id
    return render_template('stripe/payment.html',
                           key=current_app.config['STRIPE_PUBLIC'],
                           user_email=user_email,
                           qc_form=qc_form,
                           product=product_info) # do not forget about 100

@app.route('/stripe/declined', methods=['POST'])
def stripe_declined():
    return """<html><body><h1>Card Declined</h1><p>Your chard could not
            be charged. Please check the number and/or contact your credit card
            company.</p></body></html>"""

@app.route('/stripe/quickcharge', methods=['POST'])
@login_required
def stripe_quickcharge():
    if not loader.enabled('stripe'):
        raise Exception('Stripe not enabled')
    unique_id = str(uuid.uuid4()) # unique code accross all records
    stripe_id = current_user.get_stripe()
    if not stripe_id:
        raise Exception('Stripe quick checkout did not setup')

    # -- product integrity checking --
    form = forms.QuickCharge()
    product_id = form.product_id.data
    product = dbs.Product.query.get(product_id)
    if (not product) or (not product.is_active):
        raise Exception('product not fit for sale')

    # -- charge --
    charge_meta = { # display to stripe dashboard
                    'uuid': unique_id,
                    'product_id': product_id,
                    'user': current_user.username
    }
    try: # charge to customer instead of charge to card
        charge = stripe.Charge.create(amount=int(product.price * 100),
                                      currency=product.currency,
                                      customer=stripe_id,
                                      metadata=charge_meta)
    except stripe.CardError, e:
        redirect(url_for(stripe_declined))       
    # -- record charge --
    write_charge(charge, unique_id, current_user.id, product.id)
    # CRUMB: add post purchase operations
    flash('stripe quickcharge complete', category='success')
    return redirect(url_for('index'))

@app.route('/stripe/charge', methods=['POST'])
@login_required
def stripe_charge():
    if not loader.enabled('stripe'):
        raise Exception('Stripe not enabled')
    # -- fetch form info --
    unique_id = str(uuid.uuid4()) # unique code accross all records
    stripe_token = request.form['stripeToken']
    email = request.form['stripeEmail']
    product_id = request.form['product_id']

    charge_meta = { # display to stripe dashboard
                    'uuid': unique_id,
                    'product_id': product_id,
                    'user': current_user.username
    }
    # -- fetch product (do not trust form from client side) --
    product = dbs.Product.query.get(product_id)
    if (not product) or (not product.is_active):
        raise Exception('product not fit for sale')

    # -- create new customer(if necessary) and charge it --
    stripe_id = current_user.stripe_customer_id
     
    if not stripe_id: # if not have one, create a record
        user_meta = {'id': current_user.id,
                     'username': current_user.username,
                     'first_name': current_user.first_name,
                     'last_name': current_user.last_name}     
        customer = stripe.Customer.create(
            email=email,
            source=stripe_token,
            metadata=user_meta
        )
        stripe_id = customer.id
        current_user.stripe_customer_id = stripe_id # write to db
        db_util.commit()
        try: # charge to customer instead of charge to card
            charge = stripe.Charge.create(amount=int(product.price * 100),
                                          currency=product.currency,
                                          customer=stripe_id,
                                          metadata=charge_meta)
        except stripe.CardError, e:
            redirect(url_for(stripe_declined))    
    else:
        try:
            charge = stripe.Charge.create(amount=int(product.price * 100),
                                          currency=product.currency,
                                          card=stripe_token,
                                          metadata=charge_meta)
        except stripe.CardError, e:
            redirect(url_for(stripe_declined))

    # -- update user address info --
    bill = None
    if 'stripeBillingName' in request.form:
        bill = {
            'name': request.form['stripeBillingName'],
            'address': request.form['stripeBillingAddressLine1'],
            'zip': request.form['stripeBillingAddressZip'],
            'state': request.form['stripeBillingAddressState'],
            'city': request.form['stripeBillingAddressCity'],
            'country': request.form['stripeBillingAddressCountry']
        }
    ship = None
    if 'stripeShippingName' in request.form:
        ship = {
            'name': request.form['stripeShippingName'],
            'address': request.form['stripeShippingAddressLine1'],
            'zip': request.form['stripeShippingAddressZip'],
            'state': request.form['stripeShippingAddressState'],
            'city': request.form['stripeShippingAddressCity'],
            'country': request.form['stripeShippingAddressCountry']
        }
    current_user.set_address(ship=ship, bill=bill)

    # -- record charge --
    write_charge(charge, unique_id, current_user.id, product.id, email)
    # CRUMB: add post purchase operations
    flash('stripe charge complete', category='success')
    return redirect(url_for('index'))

# ---- JWT Acquire ----
@app.route('/jwt/<party>', methods=['GET'])
@login_required # thrird party normally have services that might cost u (like get video call)
def jwt_token(party):
    if not loader.enabled(party):
        raise Exception('Party is not enabled: {}'.format(party))    
    if party == 'twilio':
        # twilio reference: https://github.com/TwilioDevEd/video-quickstart-python
        # Create an Access Token
        token = TAccessToken(app.config['TWILIO_ACCOUNT_SID'],
                             app.config['TWILIO_API_KEY'],
                             app.config['TWILIO_API_SECRET'])
        # Set the Identity of this token
        token.identity = current_user.username
        # Grant access to Video
        grant = VideoGrant()
        grant.configuration_profile_sid = app.config['TWILIO_CONFIGURATION_SID']
        token.add_grant(grant)
        # Return token info as JSON
        return jsonify(identity=token.identity,
                       token=token.to_jwt())
    elif party == 'firebase':
        # firebase reference: https://firebase.google.com/docs/auth/admin/create-custom-tokens
        service_account = app.config['FIREBASE_SERVICE_ACCOUNT']
        private_key = app.config['FIREBASE_PRIVATE_KEY']
        return jsonify(api=app.config['FIREBASE_API'],
                       pid=app.config['FIREBASE_ID'],
                       token=build_jwt(iss=service_account,
                                       sub=service_account,
                                       uid=current_user.username,
                                       aud='https://identitytoolkit.googleapis.com/google.identity.identitytoolkit.v1.IdentityToolkit',
                                       claims={"admin": current_user.has_role('admin')},
                                       private_key=private_key))
    else:
        abort(404)

# ---- Video Chat ----
@app.route('/video')
@login_required # need jwt token
def video():
    return render_template('twilio/video.html')

# ---- Firebase Resources Group ----
class FirebaseView(MethodView):
    decorators = [login_required]

    def get_template_name(self):
        return 'firebase/' + self.template_name

    def get(self):
        data = self.get_data() # child data
        data['current_user'] = dump_user(current_user)
        context = {'injection': data}
        return render_template(self.get_template_name(), **context)

class ChatView(FirebaseView):
    def __init__(self, template_name):
        self.template_name = template_name

    def get_data(self):
        """
        Find the chat_id, the only entry point allow current user to write
        """
        #pass
        return {'chat_ref': get_dependency_path('chat', current_user.id),
                'draw_ref': get_dependency_path('draw', current_user.id),
                'video_room': current_user.get_video_room()}

app.add_url_rule('/chat',
                 view_func=ChatView.as_view('chat_page',
                                            template_name='chat.html'))

@app.route('/firebase')
@login_required
def firebase():
    return render_template('frame/firebase.html',
                           injection={'current_user': dump_user(current_user)})

@app.route('/design')
def design():
    return render_template('twilio/design.html')
