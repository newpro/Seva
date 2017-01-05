"""
Flammable Interface

Abstract DB Interface for Google Firebase

Build on pyrebase (https://github.com/thisbejim/Pyrebase)

Author: Aaron Li

MIT licenced

This file contains two major parts of flammable interface:

* Flammable Class
* Model Class
"""
import pyrebase
from errs import ParaErr, MountErr, DataErr, KeyErr, LoadedErr, ConfigErr, ReverseErr, ExistsException
from time import time

# ---- Generic Database Object ----
class Model():
    """Generic Database Object Interface
    
    Base class for custom db models

    This is used for inheretence of all objects that referenced to a database object
    """
    def __init__(self, path, db = None): # db is a Flammable instance
        self._id = None
        if not db:
            if not Model.db: # if forget to set static db
                raise ConfigErr('Have to provide static db or instance db')
            self.db = Model.db
        else:
            self.db = db # use passin reference as instance db
        if (self.db).__class__.__name__ != 'Flammable':
            raise ConfigErr('DB is not a Flammable object')
        if not self.db.connected:
            raise ConfigErr('DB has not been connected')
        try:
            self._path = self.db._mount(path)
        except:
            raise MountErr('Unable to mount path')

    def __repr__(self): # overwrite in subclass
        if self._id:
            return '<FirebaseObject %r>', self._id
        return '<FirebaseRawObject>'

    def new(self, data, _id = None):
        """
        Create a new object in DB, and Hook to this model object

        Have the option to write a key value pair(we call id/data pair), or just append data
        """
        if (self._id):
            raise LoadedErr('Object already loaded')
        if _id: # insert _id/data pair
            self.db._write(self._path, _id, data)
        else: # insert data
            _id = self.db._append(self._path, data) # append and fetch new index
        self._path = self.db._mount(self._path, loc=_id) # update from parent path to current path
        self._id = _id
        return self

    def bind(self, _id):
        """
        Hook up with one exist object in db that has the id
        """
        if (self._id):
            raise LoadedErr('Object already loaded')
        try:
            self._path = self.db._mount(self._path, loc=_id)
        except:
            raise Exception('Bind Unsuccessful, path: %r, loc: %r', (self._path, _id))
        self._id = _id
        return self

    def data(self):
        """
        Get data of the object
        """
        return self.db._data(self._path)

    def peek(self):
        """
        Return all keys in datasets, or the name if already loaded
        It is useful sometimes before load, for example get a list of names before bind
        
        Warning: There might be inconsistancy before load.
        No consistancy control in REST APIs, u have been WARNED.
        """
        if self._id:
            return self._id
        return self.data().keys()

    def remove(self):
        """
        Remove all children within loaded object.

        Optional, Purge: default false. If true, remove all children and the branch.

        Warnings:

        * no recovery on deletion
        * after call, the reference to the object is not reuseable (_path is removed).
        """
        if not self._id:
            raise Exception('From flammable.py: Can not remove non-loaded object (Check doc for purge)')
        self.db._remove(self._path)
        self._path = None
        self._id = None

    def overwrite(self, data):
        """
        Overwrite path with data

        Use with caution
        """
        if not self._id:
            raise Exception('Can not overwrite an unloaded object')
        self.db._reset(self, self._path, data)

    def _rebuild(self, init_data=None):
        """
        Programmatically rebuild the branch. Avoid the trouble of import at Firebase console.

        Rebuild will delete all data in the position if have any, and insert true as the first space holder.

        Rebuild deletion can not be recovered, u have been warned.
        """
        if self._id:
            raise Exception('Can not rebuild a loaded object, have to be a branch (non-loaded).')
        if init_data and (not isinstance(init_data, dict)):
            raise DataErr('Sample data have to be dictionary.')
        # -- Set up --
        if init_data:
            self.db._reset(self._path, init_data)
        else:
            self.db._reset(self._path, True)
        self._path = self.db._mount(self._path)

    def exists_or_exception(self, index=None, attribute=None):
        """
        Check exist or raise exception

        This function does not change the current object

        Options:

        * index: check if the index exists
        * index with attribute: check a dictional structure, key is attribute, value should be index
        """
        if not self._path:
            raise DataErr('No path')
        try:
            if index:
                if attribute:
                    value = self.db._data(self._path)[attribute]
                    if not (value == index):
                        raise Exception('Attribute not equal: ' + attribute)
                else:
                    self.db._mount(self._path, loc=index)
            else:
                self.db._mount(self._path)
        except:
            #import traceback
            #import logging
            #logging.error(traceback.format_exc())
            raise ExistsException('Not exists from exists_or_exception')

class ReflectModel(Model):
    """
    Reflect one branch in a model.

    For example, message model can reflect to chat model. Check docs for more information.

    Params:

    * model: reference to a instance of Model object.
    * delete_propagation: if the reflected model is gone
    """
    def __init__(self, path, reflect_model=None, db=None, delete_propagation=True):
        """
        Target is a loaded Model instance that this model should reflect.
        """
        Model.__init__(self, path, db=db)
        if not reflect_model: # general class
            return self

        if not issubclass(reflect_model.__class__, Model):
            raise ParaErr('reflect_model is not a subclass of Model')
        if not reflect_model._id:
            raise ParaErr('reflect_model is not loaded')
        try:
            reflect_model.exists_or_exception()
        except:
            raise DataErr('reflect_model is not accessable')
        # -- Set up this model --
        self.reflect_model = reflect_model
        self.delete_propagation = delete_propagation
        try:
            self._path = self.db._mount(self._path, loc=(reflect_model._id))
        except: # first time, build the path
            self.db._write(self._path, reflect_model._id, True) # get ready
            self._path = self.db._mount(self._path, loc=(reflect_model._id))

    def new(self, data, _id=None):
        if not self.reflect_model:
            raise ReflectErr('Have to provide reflection first')
        try:
            self.reflect_model.exists_or_exception()
        except:
            raise ParaErr('Reflect Integrity')
        return Model.new(self, data, _id=_id)

    def exists(self, branch, key):
        """
        Check if the key is in the branch

        For example, key is a person id, and branch is the chat id, check if the person is in chat
        """
        try:
            self.reflect_model # can not exists
            raise Exception('Can not be loaded (because it is on subpath), use exists_or_exception instead')
        except:
            pass
        self.bind(branch) # warning: does change (destoryed) this object
        if key in self.data():
            return True
        return False

class ReverseModel(Model):
    """
    Reverse Model is a complete key value pair reverse of the target model.

    For example, chat id to username can be a reverse model of username to chat id
    """
    def __init__(self, path, reverse_model=None, db=None, delete_propagation=True, store_structure='dict'):
        Model.__init__(self, path, db=db)
        if not reverse_model: # general class
            return self
        if not reverse_model._id:
            raise ParaErr('reverse_model is not loaded')
        try:
            reverse_model.exists_or_exception()
        except:
            raise DataErr('reverse_model is not accessable')
        self.reverse_model = reverse_model
        self.delete_propagation = delete_propagation
        if not (store_structure in ['dict', 'list']):
            raise ParaErr('Store structure not recognized')
        self.store_structure = store_structure

    def new(self, track_value, data=True, validate_field=None):
        if not self.reverse_model:
            raise ReverseErr('Have to provide reverse first')
        try:
            self.reverse_model.exists_or_exception()
            if not validate_field: # direct reverse
                self.reverse_model.exists_or_exception(index=track_value)
            else:
                self.reverse_model.exists_or_exception(index=track_value, attribute=validate_field)
        except:
            raise ParaErr('Reverse Integrity')
        try:
            self.exists_or_exception(index=track_value) # check the exists project, raise exists exception
            self._path = self.db._mount(self._path, loc=(track_value))
            if self.store_structure == 'dict':
                Model.new(self, data, _id=(self.reverse_model._id)) # if not exists, insert
            else: # list
                self.overwrite(self, self.reverse_model._id)
        except ExistsException:
            if self.store_structure == 'dict':
                Model.new(self, {self.reverse_model._id: data}, _id=track_value)
            else: # list
                Model.new(self, self.reverse_model._id, _id=track_value)

def refresh_token(timestamp, user):
    if not timestamp: # admin account enabled
        return # does not need to refresh
    if time() - timestamp > 55*60: # one hour expire time, refresh at 55 mins
        user = auth.refresh(user['refreshToken'])

class Flammable():
    """
    Flammable interface
    """
    def __init__(self, database_url, cred_path, api_key, email=None, password=None, mod='TESTING'):
        """
        Initial configuration requires the following parameters:
        * database_url: the url of the database
        * cred_path: the path to the credential file
        * api_key: api access key for the firebase
        * mod (optional): the mod it runs, one of TESTING/DEPLOYING, DEPLOYING does not perform db integrity checks

        Check Docs for more information.
        """
        config = {
            'apiKey': api_key, 
            'authDomain': '', # dummy
            'databaseURL': database_url,
            'storageBucket': '', # dummy
            'serviceAccount': cred_path
        }
        try:
            _firebase = pyrebase.initialize_app(config)
            self.db = _firebase.database()
        except:
            import traceback
            import logging
            logging.error(traceback.format_exc())
            raise ConfigErr('Initialization Failure, check your setup parameters')

        if not email:
            self.user = {'idToken': None}
            self.token_timestamp = None
        else:
            times = 3
            while times > 0:
                try:
                    self.token_timestamp = time()
                    self.user = _firebase.auth().sign_in_with_email_and_password(email, password)
                    break
                except:
                    from time import sleep
                    times -= 1
                    if times <= 0:
                        raise ConfigErr('Email and password failure')
                    print 'LOGIN ERROR, retrying after 4s, times left:', times
                    sleep(4)

        #self.Model = Entry(self.db, self.token) # create data model entry
        if mod != 'TESTING' and mod != 'DEPLOYING':
            raise ConfigErr('Mod not recognizable')
        self.mod = mod
        self.connected = True

    def __repr__(self):
        if self.connected:
            return '<Flammable(Connected)>'
        return '<Flammable(Empty)>'

    def _mount(self, mount_point, loc='', request_ref=False, check=True):
        """
        check validility of a mount point (only during testing), and then mount the data point, return the reference
        
        :Optional, loc: specify a attached data location, this location will not be checked for validility
        :Optional, ref: return a reference point instead of a path string

        Return: 
        if ref is false, will return a string indicate the path of the data
        otherwise it will return the reference of the data
        -
        Warning:
        * If reference get returned, this statement has to append with a get to clear path data!
        * Otherwise it will interfere with other mount
        Read this git issue: 
        https://github.com/thisbejim/Pyrebase/issues/56
        -
        For a wrong usage example:
        print _mount('hardwares/objects')
        print _mount('knowledge/sensor_types').get().val()

        Error:
        Mount point or data in mount point not exists,
        this will only be checked in testing

        # Check if mount_point exists
        >>> _mount('hardwares/sensors', path_only=True)
        hardwares/sensors/

        # Check if data exists at mount_point
        >>> _mount('hardwares/sensors', 'kinect1', path_only=True)
        hardwares/sensors/kinect1

        # Mount a data point
        _mount('mount_point').get().val()
        """
        if mount_point[-1] == '/':
            path = mount_point + loc
        else:
            path = mount_point + '/' + loc
        if (self.mod == "TESTING" and check and not (self.db.child(path).get().val())): # only check in testing
            raise MountErr('Mount point invalid: ' + path)
        if request_ref:
            return self.db.child(path)
        return path

    def _data(self, mount_point):
        """
        request data segment of a mount point

        Return:
        Directory, Data from the mount point

        # get data from a mount point
        _data('knowledge/sensor_types')
        """
        return self._mount(mount_point, request_ref=True).get().val()

    def _key(self, mount_point):
        return self._mount(mount_point, request_ref=True).shallow().get().val()

    def _write(self, path, key, value, overwrite = False):
        """
        Write a key value pair to assigned path location
        Optional: overwrite the data

        Notes:
        This function is differet from _write function.
        It enforces key value pairs and have in theory O(1) access/write time

        Error:
        Duplicate key pair exists

        Return:
        None for success insert

        >>> _set('knowledge/sensor_types', 'new_type', {'info1': '1', 'info2': 2})
        None
        """
        if (not key) or (not value):
            raise DataErr('Write data can not be empty')
        if not overwrite: # if not allow duplicate key
            try:
                if key in self._data(path).keys():
                    raise KeyErr('Duplicate key not allowed:' + key)
            except AttributeError:
                pass # forgive no keys and only True (rebuild case)
        refresh_token(self.token_timestamp, self.user)
        self._mount(path, request_ref=True, check=False, loc=key).set(value, self.user['idToken'])

    def _append(self, path, data):
        """
        Write data to a path location

        Return key of the new appended record

        Notes:
        This function is different from _insert function

        It only appends data to the path location.
        """
        refresh_token(self.token_timestamp, self.user)
        return (self._mount(path, request_ref=True).push(data, self.user['idToken']))['name']

    def _reset(self, path, data):
        """
        Remove all child in path and reset to new data
        """
        refresh_token(self.token_timestamp, self.user)
        self._mount(path, request_ref=True).set(data, self.user['idToken'])

    def _remove(self, path):
        """
        Remove all data in path
        """
        refresh_token(self.token_timestamp, self.user)
        self._mount(path, request_ref=True).set(None, self.user['idToken'])
