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
    db.Column('soc_id', db.Integer, db.ForeignKey('social.id'))
)

# ---- Tables ----
class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=True)
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
    create_at = db.Column(db.DateTime, onupdate=datetime.now)
    reset_password_token = db.Column(db.String(100), nullable=False, default='')

    # -- User Email information --
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime(), nullable=True)

    # -- User information --
    is_enabled = db.Column(db.Boolean(), nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')
    social_id = db.Column(db.String(64), nullable=True, unique=True)

    # -- Optional field --
    # CANDY: Optional user fields
    profile_url = db.Column(db.String(200), nullable=False, default='')

    # -- Relationships --
    roles = relationship("Role",
                         secondary=user_roles,
                         lazy='dynamic')

    social = relationship("SocialPlatform",
                         secondary=social_logins,
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

    def has_role(self, role, ref=False):
        if not ref:
            role = fetch('role', role)
        return role in self.roles.all()

    def has_social_provider(self, provider, ref=False):
        if not ref:
            provider = fetch('provider', provider)
        return provider in self.social.all()

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
        if ref: # if role is an object
            role_ref = role
        else: # role is a string
            role_ref = fetch('role', role)
        if not role_ref:
            raise Exception('Role not exists')
        if self.has_role(role_ref, ref=True):
            print '--- Warning: role "{}" already exists, ignored ---'.format(role_ref.name)
            return
        self.roles.append(role_ref)
        util.commit()

    def add_social(self, provider, ref=False):
        if ref:
            provider_ref = provider
        else:
            provider_ref = fetch('provider', provider)
        if not provider_ref:
            raise Exception('Provide does not exists')
        if self.has_social_provider(provider_ref, ref=True):
            print '--- Warning: social provider "{}" already in user, ignored ---'.format(provider_ref.name)
            return
        self.social.append(provider_ref)
        util.commit()

    def verify_password(self, hashcode):
        return user_manager.verify_password(hashcode, self)

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
    # CRUMB: add additional tables for fetching
    elif column == 'provider':
        _db = SocialPlatform
        field = SocialPlatform.name
    else:
        raise Exception('Column not recognizable')
    return _db.query.filter(field==index).first()

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
    service = Role(name='service', color='57A8BB', icon='fax').pip().add_hierarchy([user])
    admin = Role(name='admin', color='F16236', icon='user-plus').pip().add_hierarchy([user, service])
    # CANDY: add additional roles

def _init_social():
    SocialPlatform(name='twitter', icon='twitter-square').add()
    SocialPlatform(name='facebook', icon='facebook-square').add()

def _init_data():
    User(username='user_test', email='user1@email.com', active=True,
         password = '007', first_name = 'duck', last_name = 'mcgill', is_enabled=True).pip().add_role('user')
    User(username='service_test', email='service1@email.com', active=True,
         password = '007', first_name = 'goose', last_name = 'abilio', is_enabled=True).pip().add_role('service')
    admin_test = User(username='admin_test', email='admin1@email.com', active=True,
                      password = '007', first_name = 'sponge', last_name = 'bob',
                      is_enabled=True, confirmed_at=datetime.now()).pip()
    admin_test.add_role('admin')
    admin_test.add_social('facebook')
    # CANDY: add additional user for roles here
    # CRUMB: add additional table tests here

def _RESET_DB():
    # -- reset in dependency order --
    util.reset()
    _init_social()
    _init_roles()
    _init_data()

# ---- DB setups ----
from flask_user import SQLAlchemyAdapter, UserManager
db_adapter = SQLAlchemyAdapter(db, User) # Register the User model
user_manager = UserManager(db_adapter, app) # expose to others
