from flask import render_template, request, url_for, current_app, redirect, flash, abort
from flask_user import login_required, roles_required, current_user
from . import app, dbs, db, forms, db_util
from flask_s3 import create_all
from flask_login import login_user, logout_user
import uuid

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
    return render_template('main/index.html')

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

# ---- Stripe Views ----
from . import stripe

@app.route('/product/<product_id>', methods=['GET'])
@login_required
def stripe_payment(product_id):
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
    mongo_id = str(app.mongo['charge'].insert_one(charge).inserted_id)
    purchase = dbs.Purchase(uuid=unique_id,
                            mongo_id=mongo_id,
                            customer_id=current_user.id,
                            product_id=product.id).pip()
    dbs.Delivery(purchase=purchase).add()
    # CRUMB: add post purchase operations
    flash('stripe quickcharge complete', category='success')
    return redirect(url_for('index'))

@app.route('/stripe/charge', methods=['POST'])
@login_required
def stripe_charge():
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
    mongo_id = str(app.mongo['charge'].insert_one(charge).inserted_id)
    purchase = dbs.Purchase(uuid=unique_id,
                            email=email,
                            mongo_id=mongo_id,
                            customer_id=current_user.id,
                            product_id=product.id).pip()
    dbs.Delivery(purchase=purchase).add()
    # CRUMB: add post purchase operations
    flash('stripe charge complete', category='success')
    return redirect(url_for('index'))
