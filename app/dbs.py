from . import db, db_util as util, app
from sqlalchemy.orm import relationship
from datetime import datetime

# ---- Relations Tables ----
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

# ---- Tables ----
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=True) 
    color = db.Column(db.String(6), unique=True, nullable=True) # 6 digits hash code
    icon = db.Column(db.String(30), unique=True, nullable=True) # font awesome icon code

    def __init__(self, name, color=None, icon=None):
        self.name = name
        self.color = color
        self.icon = icon

    def __repr__(self):
        return '<Role %r>' % (self.name)

    def add(self):
        util.add(self)

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
    reset_password_token = db.Column(db.String(100), nullable=False, default='')

    # -- User Email information --
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # -- User information --
    is_enabled = db.Column(db.Boolean(), nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')
    confirmed_at = db.Column(db.DateTime())

    # -- Optional field --
    # CANDY: Optional user fields
    profile_url = db.Column(db.String(200), nullable=False, default='')

    # -- Relationships --
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username, email, password, first_role,
                 active=False, first_name = None, last_name = None,
                 profile_url=None):
        self.username = username
        self.email = email
        self.is_enabled = active
        if active:
            self.confirmed_at = datetime.utcnow()
        self.password = user_manager.hash_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.profile_url = profile_url
        self.add_role(first_role)
        # CANDY: add optional user fields in init

    def add(self):
        util.add(self)

    def active(self):
        self.is_enabled = True

    def is_active(self):
        return self.is_enabled

    def add_role(self, role_name):
        exist_role = fetch('role', role_name)
        if exist_role: # if role already created
            self.roles.append(exist_role)
        else:
            raise Exception('Role not exists')
        util.add(self)

    def __repr__(self):
        return '<User %r, %r>' % (self.id, self.username)

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

def fetch(column, main_field):
    """
    fetch one entry by main entry
    """
    if column == 'user':
        _db = User
        field = User.username
    elif column == 'role':
        _db = Role
        field = Role.name
    # CRUMB: add additional tables for fetching
    else:
        raise ('Column not recognizable')
    return _db.query.filter(field==main_field).first()

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

    * Level control: 'caregiver', 'elder', 'expert', 'service', 'admin', 'super'
    * Default experts: 'medical', 'hardware', 'interior', 'developer'
    """
    Role('user', color='4DBD33', icon='user').add()
    Role('service', color='57A8BB', icon='fax').add()
    Role('admin', color='F16236', icon='user-plus').add()
    Role('boss', color='E63E3B', icon='user-secret').add()
    # CANDY: add additional roles

def _init_data():
    user = self.db.User(username='user_test', email='user1@email.com', active=True,
                         password = '007', first_role = 'user', first_name = 'duck', last_name = 'mcgill')
    service = self.db.User(username='service_test', email='service1@email.com', active=True,
                         password = '007', first_role = 'service', first_name = 'goose', last_name = 'abilio')
    admin = self.db.User(username='admin_test', email='admin1@email.com', active=True,
                             password = '007', first_role = 'admin', first_name = 'sponge', last_name = 'bob')    
    boss = self.db.User(username='boss_test', email='boss1@email.com', active=True,
                             password = '007', first_role = 'boss', first_name = 'lion', last_name = 'king')
    # CANDY: add additional user for roles here
    # CRUMB: add additional table tests here

def _RESET_DB():
    # -- reset in dependency order --
    util.reset()
    _init_roles()
    _init_data()

# ---- DB setups ----
from flask_user import SQLAlchemyAdapter, UserManager
db_adapter = SQLAlchemyAdapter(db, User) # Register the User model
user_manager = UserManager(db_adapter, app) # expose to others
