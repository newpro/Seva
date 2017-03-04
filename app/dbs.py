from . import db, db_util as util, app
from sqlalchemy.orm import relationship
from datetime import datetime

# ---- Secondary Tables ----
user_roles = db.Table('user_role',
    db.Column('user_fk', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_fk', db.Integer, db.ForeignKey('role.id'))
)

role_hierarchys = db.Table('role_hierarchy',
    db.Column('index', db.Integer, primary_key=True),
    db.Column('primary_fk', db.Integer, db.ForeignKey('role.id')),
    db.Column('role_fk', db.Integer, db.ForeignKey('role.id'))
)

social_logins = db.Table('social_login',
    db.Column('index', db.Integer, primary_key=True),
    db.Column('user_fk', db.Integer, db.ForeignKey('user.id')),
    db.Column('soc_fk', db.Integer, db.ForeignKey('social.id'))
)

chat_clients = db.Table('chat_client',
    db.Column('index', db.Integer, primary_key=True),
    db.Column('user_fk', db.Integer, db.ForeignKey('user.id')),
    db.Column('chat_fk', db.Integer, db.ForeignKey('chat.id'))
)

user_locations = db.Table('user_location',
    db.Column('index', db.Integer, primary_key=True),
    db.Column('user_fk', db.Integer, db.ForeignKey('user.id')),
    db.Column('loc_fk', db.Integer, db.ForeignKey('location.id'))
)

# ---- Tables ----
class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    color = db.Column(db.String(6), unique=True, nullable=True) # 6 digits hash code
    icon = db.Column(db.String(25), unique=True, nullable=True) # font awesome icon code

    # -- Role Hierarchy --
    hierarchy = relationship("Role",
                             secondary=role_hierarchys,
                             primaryjoin=id==role_hierarchys.c.primary_fk,
                             secondaryjoin=id==role_hierarchys.c.role_fk,
                             backref=db.backref("role_hierarchys"),
                             lazy='dynamic')

    # -- Helpers --
    def __repr__(self):
        return '<Role %r>' % (self.name)

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

    def add_hierarchy(self, role_list):
        for role_ref in role_list:
            if role_ref.id == self.id:
                raise Exception('can not add itself to hierarchy, prevent loop')
            if not self.is_higher(role_ref):
                self.hierarchy.append(role_ref)
            else:
                raise Exception('already in role hierarchy')
        util.commit()
        return self

    def is_higher(self, role):
        return self.hierarchy.filter(role_hierarchys.c.role_fk == role.id).count() > 0

class SocialPlatform(db.Model):
    __tablename__ = 'social'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=True)
    icon = db.Column(db.String(25), unique=True, nullable=True)

    # -- Helpers --
    def __repr__(self):
        return '<Role %r>' % (self.name)

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=True)

    # -- Helpers --
    def __repr__(self):
        return '<Role %r>' % (self.name)

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

class Chat(db.Model):
    __tablename__ = 'chat'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(25), unique=True, nullable=True)
    clients = relationship("User",
                           secondary=chat_clients,
                           lazy='dynamic')

    # -- Helpers --
    def __repr__(self):
        return '<Chat id: %r, %r>' % (self.id, self.title)

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

class Address(db.Model):
    """
    User Address, cleaned by stripe

    Core idea: 

    * Record first time made a purchase
    * Update every purchase if there is a change
    """
    __tablename__ = 'address'

    id = db.Column(db.Integer, primary_key=True)
    # ---- billing ----
    bill_name = db.Column(db.String, nullable=True)
    bill_address = db.Column(db.String, nullable=True)
    bill_zip = db.Column(db.String, nullable=True)
    bill_state = db.Column(db.String, nullable=True)
    bill_city = db.Column(db.String, nullable=True)
    bill_country = db.Column(db.String, nullable=True)
    # ---- shipping ----
    ship_name = db.Column(db.String, nullable=True)
    ship_address = db.Column(db.String, nullable=True)
    ship_zip = db.Column(db.String, nullable=True)
    ship_state = db.Column(db.String, nullable=True)
    ship_city = db.Column(db.String, nullable=True)
    ship_country = db.Column(db.String, nullable=True)

    # -- Helpers --
    def __repr__(self):
        return '<Address %r>' % (self.id)

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

from flask_user import UserMixin
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    """
    User Data Model, represent one user within system

    * index: auto assigned index
    * first: first name
    * last: last name
    * role: one of older/caregiver/stuff
    * target: the person's care target, older will be none
    """
    id = db.Column(db.Integer, primary_key=True)
    # -- User Authentication information --
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    create_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=datetime.now)
    reset_password_token = db.Column(db.String(100), nullable=False, default='')

    # -- User Email information --
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime(), nullable=True)

    # -- User information --
    is_enabled = db.Column(db.Boolean(), nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')
    social_id = db.Column(db.String(64), nullable=True, unique=True)

    # -- Seva Field --
    phone = db.Column(db.String(20), nullable=True)

    # -- Optional field --
    profile_url = db.Column(db.String(200), nullable=False, default='')
    stripe_customer_id = db.Column(db.String, nullable=True) # quick charge support
    # -- shipment --
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=True) # allow null
    address = relationship(Address, uselist=False) # one to one

    # -- Relationships --
    roles = relationship("Role",
                         secondary=user_roles,
                         lazy='dynamic')

    social = relationship("SocialPlatform",
                         secondary=social_logins,
                         lazy='dynamic')

    chats = relationship("Chat",
                         secondary=chat_clients,
                         lazy='dynamic')

    # each user linked to a list of locations they can help
    locations = relationship("Location",
                         secondary=user_locations,
                         lazy='dynamic')

    # -- Column overwrite --
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.password:
            self.password = user_manager.hash_password(self.password)

    # -- Helpers --
    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

    def active(self):
        self.is_enabled = True

    def is_active(self):
        return self.is_enabled

    def verify_password(self, hashcode):
        return user_manager.verify_password(hashcode, self)

    # ---- Role Helpers ----
    def has_role(self, role, ref=False):
        if not ref:
            role = fetch('role', role)
        return role in self.roles.all()

    def has_any_role(self, roles, ref=False):
        """
        Give a list of roles, check if it has any of the role
        """
        for role in roles:
            if self.has_role(role, ref=ref):
                return True
        return False

    def add_role(self, role_name):
        """
        Add the role and all roles lower than it
        """
        role_ref = fetch('role', role_name)
        lower_roles = role_ref.hierarchy.all() # fetch all lower roles
        for role in lower_roles: # add all lower roles
            self.add_one_role(role, ref=True)
        self.add_one_role(role_ref, ref=True)
        util.commit()

    def add_one_role(self, role, ref=False):
        """
        Add one role without hierarchy check
        """
        if ref:
            _add_to_secondary(self.roles, role)
        else:
            _add_to_secondary(self.roles, role, fetch_table='role')

    # ---- Social Helpers ----
    def has_social_provider(self, provider, ref=False):
        if not ref:
            provider = fetch('provider', provider)
        return provider in self.social.all()

    def add_social(self, provider, ref=False):
        if ref:
            _add_to_secondary(self.social, provider)
        else:
            _add_to_secondary(self.social, provider, fetch_table='provider')

    def add_chat(self, chat, ref=False):
        if ref:
            _add_to_secondary(self.chats, chat)
        else:
            _add_to_secondary(self.chats, chat, fetch_table='chat')

    # ---- Location Helpers ----
    def add_loc(self, loc, ref=False):
        if ref:
            _add_to_secondary(self.locations, loc)
        else:
            _add_to_secondary(self.locations, loc, fetch_table='location')

    def has_loc(self, loc, ref=False):
        if not ref:
            loc = fetch('location', loc)
        return loc in self.locations.all()

    # ---- Payment Helpers ----
    def get_stripe(self):
        """
        check if user already have stripe record
        
        if have it, return record. Otherwise return false
        """
        if self.stripe_customer_id:
            return self.stripe_customer_id
        return False

    def set_stripe(self, customer_id):
        """
        setup stripe id
        """
        self.stripe_customer_id = customer_id
        util.commit()

    def set_address(self, ship=None, bill=None):
        address = {}
        if bill:
            address['bill_name'] = bill['name']
            address['bill_address'] = bill['address']
            address['bill_zip'] = bill['zip']
            address['bill_state'] = bill['state']
            address['bill_city'] = bill['city']
            address['bill_country'] = bill['country']
        # ---- shipping ----
        if ship:
            address['ship_name'] = ship['name']
            address['ship_address'] = ship['address']
            address['ship_zip'] = ship['zip']
            address['ship_state'] = ship['state']
            address['ship_city'] = ship['city']
            address['ship_country'] = ship['country']
        self.address = Address(**address)
        util.commit()

    def get_video_room(self):
        return "1"

    def __repr__(self):
        return '<User %r, %r>' % (self.id, self.username)

app_currency = app.config['CURRENCY']
class Product(db.Model):
    """
    Basic expandable product model
    
    The prime focus of this model is to support payment system and admin.
    
    U should keeps all fields and expand this. 
    """
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    # -- Market info --
    is_active = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default=app_currency)
    digital = db.Column(db.Boolean, default=False) # if digital, product does not need to ship

    def __repr__(self):
        return '<Product %r %r>' % (self.id, self.name)
    
    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

class Purchase(db.Model):
    __tablename__ = 'purchase'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    mongo_id = db.Column(db.String, unique=True, nullable=True) # if you have mongo, change nullable to false
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = relationship(Product)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer = relationship(User)
    # -- safty field, return data from stripe --
    email = db.Column(db.String, nullable=True) # stripe email from stripe, if none, means quickcharge

    def __repr__(self):
        return '<Purchase id: %r customer: %r, product: %r>' % (self.uuid, self.email, self.product_id)

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

class DeliveryState(db.Model):
    """
    Delivery record support
    
    Record all changes of record state, and who changed it.
    
    Map to secondary table.
    """
    __tablename__ = 'delivery_state'

    id = db.Column(db.Integer(), primary_key=True)
    state = db.Column(db.String(10), unique=True, nullable=False)

    def __repr__(self):
        return '<DeliveryState %r>' % (self.name)

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

class Delivery(db.Model):
    """
    One to one mapping to purchase table
    
    Reason for isolation: different view level for information for service role
    """
    __tablename__ = 'delivery'

    id = db.Column(db.Integer(), primary_key=True)
    # -- record --
    state = db.Column(db.String, db.ForeignKey('delivery_state.state'), nullable=False, default='purchased')
    state_ref = relationship(DeliveryState)
    # -- purchase --
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False)
    purchase = relationship(Purchase, uselist=False) # one to one

    def __repr__(self):
        return '<DeliveryState %r>' % (self.name)

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self
    
    def start_delivery(self):
        """
        mark this delivery from purchased to dispatched
        """
        self.state = 'dispatched'
        util.commit()

# CRUMB: add additional tables here

# ---- Support ----
# -- Doggy --
def fetch_by_id(column, index):
    """
    fetch one entry by index number
    """
    if column == 'user':
        _db = User
    elif column == 'role':
        _db = Role
    else:
        raise ('Column not recognizable')
    return _db.query.get(id)

def fetch(column, index):
    """
    fetch one entry by main entry
    """
    if column == 'user':
        _db = User
        field = User.username
    elif column == 'role':
        _db = Role
        field = Role.name
    elif column == 'provider':
        _db = SocialPlatform
        field = SocialPlatform.name
    elif column == 'delivery_state':
        _db = DeliveryState
        field = DeliveryState.state
    elif column == 'chat':
        _db = Chat
        field = Chat.id
    elif column == 'location':
        _db = Location
        field = Location.name
    # CRUMB: add additional tables for fetching
    else:
        raise Exception('Column not recognizable')
    return _db.query.filter(field==index).first()

def _add_to_secondary(secondary, data, fetch_table=False):
    """
    add the data to secondary

    Param:
    * ref: Can be False, or a string for table fetch
    """
    # -- fetch the data object, if necessary --
    if not fetch_table: # if data is an object
        data_ref = data
    else: # data is a string
        data_ref = fetch(fetch_table, data)
    if not data_ref:
        raise Exception('Data not exists')
    # -- check if already in --
    if data_ref in secondary.all():
        print '--- Warning: data "{}" already exists, ignored ---'.format(data_ref.id)
    secondary.append(data_ref)
    util.commit()

# -- Validators --
def exists_or_exception(column, index):
    """
    Use as one chain of validators
    """
    entry = fetch(column, index)
    if not entry:
        raise Exception('Entry not exists')

# -- DB reset --
def _init_roles():
    """
    Initialize basic roles, only use it after reset DB

    * Level control: 'user', 'service', 'admin', 'boss'
    """
    user = Role(name='user', color='4DBD33', icon='user').pip()
    care_receiver = Role(name='care_receiver').pip().add_hierarchy([user])
    care_giver = Role(name='care_giver').pip().add_hierarchy([user, care_receiver])
    admin = Role(name='admin', color='F16236', icon='user-plus').pip().add_hierarchy([user, care_giver, care_receiver])
    # CANDY: add additional roles

def _init_loc():
    Location(name='Toronto').add()
    Location(name='Waterloo').add()

def _init_social():
    SocialPlatform(name='twitter', icon='twitter-square').add()
    SocialPlatform(name='facebook', icon='facebook-square').add()

def _init_delivery_state():
    purchase_state = DeliveryState(state='purchased').pip()
    dispatched_state = DeliveryState(state='dispatched').pip()

def _init_data():
    # ---- User Tests ----
    User(username='user1', email='user1@email.com', active=True,
         password = '007', first_name = 'duck1', last_name = 'mcgill1',
         is_enabled=True, confirmed_at=datetime.now()).pip().add_role('user')

    User(username='user2', email='user2@email.com', active=True,
         password = '007', first_name = 'duck2', last_name = 'mcgill2',
         is_enabled=True, confirmed_at=datetime.now()).pip().add_role('user')

    # ---- Care test ----
    neil = User(username='neil', email='care1@email.com', active=True,
                password = '007', first_name = 'Neil', last_name = 'Abilio',
                is_enabled=True, confirmed_at=datetime.now()).pip()
    neil.add_role('care_giver')
    neil.add_loc('Toronto')

    judy = User(username='judy', email='receive1@email.com', active=True,
                password = '007', first_name = 'Judy', last_name = 'Porto',
                is_enabled=True, confirmed_at=datetime.now()).pip()
    judy.add_role('care_receiver')
    judy.add_loc('Waterloo')

    admin_test = User(username='admin_test', email='admin1@email.com', active=True,
                      password = '007', first_name = 'sponge', last_name = 'bob',
                      is_enabled=True, confirmed_at=datetime.now()).pip()
    admin_test.add_role('admin')
    admin_test.add_social('facebook')

    # ---- Product Tests ----
    watch = Product(name='watch_test', price=123.45, is_active=True).pip()

    # CANDY: add additional user for roles here
    # CRUMB: add additional table tests here

def _RESET_DB():
    # -- reset in dependency order --
    util.reset()
    _init_social()
    _init_delivery_state()
    _init_roles()
    _init_loc()
    if app.config['RUNTIME'] != 'production':
        _init_data()

# ---- DB setups ----
from flask_user import SQLAlchemyAdapter, UserManager
db_adapter = SQLAlchemyAdapter(db, User) # Register the User model
user_manager = UserManager(db_adapter, app) # expose to others
