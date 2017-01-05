"""
Exception warper

This allows users to catch and deal with different kinds of exceptions when use APIs
"""
# ---- Config Errors ----
class ConfigErr(Exception):
    """
    Trigger when required config files are missing
    """
    pass

# ---- APIs Usages Errors ----
class UsageErr(Exception):
    """
    Triggered When there is a direct wrong usage with APIs
    """
    pass

class ParaErr(UsageErr):
    """
    Raise when provide a wrong parameter, includes:
    1. Required parameter missing
    2. Parameter has wrong format
    3. Parameter not fit specific requirements
    """
    pass

class LoadedErr(UsageErr):
    """
    Raise when try to load data with a already loaded object
    """
    pass

# ---- Data Operations Errors ----
class DataErr(Exception):
    """
    Raise when error happened in data operations
    For example, write to a existing data when overwrite not allowed
    """
    pass

class MountErr(DataErr):
    """
    Raise when mount a data point,
    Most likely a non-exist data point, or data integrity damaged
    """
    pass

class KeyErr(DataErr):
    """
    Write when key already exists, and overwrite not allowed
    """
    pass

class PayloadErr(Exception):
    """
    Triggered when provided prameter is incorrect
    """
    pass

class IntegrityErr(DataErr):
    """
    Triggered when the index can not reference to an exist object in DB
    """
    pass

class ReflectErr(UsageErr):
    """
    Trigger when wrong usage of reflection or reflection fails to setup.
    """
    pass

class ReverseErr(UsageErr):
    pass

class APIForbiddenErr(UsageErr):
    """
    Trigger for a closed API point
    """
    pass

class ExistsException(Exception):
    """
    A specific exception type that raise my exists_or_exception
    """
    pass
