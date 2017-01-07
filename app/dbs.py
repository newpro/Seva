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

# ---- Tables ----
class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=True) 
    color = db.Column(db.String(6), unique=True, nullable=True) # 6 digits hash code
    icon = db.Column(db.String(30), unique=True, nullable=True) # font awesome icon code

    # -- Role Hierarchy --
    hierarchy = relationship("Role",
                        secondary=role_hierarchys,
                        primaryjoin=id==role_hierarchys.c.primary_fk,
                        secondaryjoin=id==role_hierarchys.c.role_fk,
                        backref=db.backref("role_hierarchys"),
                        lazy='dynamic')

    def __init__(self, name, color=None, icon=None):
        self.name = name
        self.color = color
        self.icon = icon

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
    roles = relationship("Role",
                         secondary=user_roles,
                         lazy='dynamic')

    def __init__(self, username, email, password,
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
        # CANDY: add optional user fields in init

    def add(self):
        util.add(self)

    def pip(self):
        self.add()
        return self

    def active(self):
        self.is_enabled = True

    def is_active(self):
        return self.is_enabled

    def has_role(self, role_ref):
        return role_ref in self.roles.all()

    def add_role(self, role_name):
        """
        Add the role and all roles lower than it
        """
        role_ref = fetch('role', role_name)
        lower_roles = role_ref.hierarchy.all() # fetch all lower roles
        for role in lower_roles: # add all lower roles
            self.add_one_role(role, ref=True)
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
        if self.has_role(role_ref):
            print '--- Warning: role "{}" already exists, ignored ---'.format(role_ref.name)
            return
        self.roles.append(role_ref)
        util.commit()

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
    else:
        raise ('Column not recognizable')
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
    user = Role('user', color='4DBD33', icon='user').pip()
    service = Role('service', color='57A8BB', icon='fax').pip().add_hierarchy([user])
    admin = Role('admin', color='F16236', icon='user-plus').pip().add_hierarchy([user, service])
    boss = Role('boss', color='E63E3B', icon='user-secret').pip().add_hierarchy([user, service, admin])
    # CANDY: add additional roles

def _init_data():
    User(username='user_test', email='user1@email.com', active=True,
         password = '007', first_name = 'duck', last_name = 'mcgill').pip().add_role('user')
    User(username='service_test', email='service1@email.com', active=True,
         password = '007', first_name = 'goose', last_name = 'abilio').pip().add_role('service')
    User(username='admin_test', email='admin1@email.com', active=True,
         password = '007', first_name = 'sponge', last_name = 'bob').pip().add_role('admin')
    User(username='boss_test', email='boss1@email.com', active=True,
         password = '007', first_name = 'lion', last_name = 'king').pip().add_role('boss')
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
