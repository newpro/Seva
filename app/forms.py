from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TextField, validators, ValidationError, SubmitField, SelectField, DecimalField, IntegerField, HiddenField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms_sqlalchemy.orm import model_form
from flask_uploads import UploadSet, IMAGES
from . import dbs

# ---- Helpers ----
images_set = UploadSet('images', IMAGES)

def _required_text(note):
    return TextField(note, [validators.Required('This field is required!')])

def _required_decimal(note):
    return DecimalField(label=note,
                        validators=[validators.Required('This field is required or not in decimal format!')])

def _required_integer(note):
    return IntegerField(label=note,
                        validators=[validators.Required('This field is required or not in Integer format!')])

def _required_date(note):
    return DateField(label=note,
              validators=[validators.Required('This date is required!')],
              format='%Y-%m-%d')

def _required_choice(note):
     # prepend default selection as empty
    return SelectField(label=note,
                       validators=[validators.Required('This choice is required!')],
                       choices=[])

def _choices(choices):
    # overwrite choice option after _required_choices
    choices.insert(0, ('',''))
    return choices

def _validators(conflicts, msg = 'This field is required!'):
    validators_ = [validators.Required(msg)]
    validators_.append(validators.NoneOf(conflicts, message='Already exists!'))
    return validators_

def _image(note):
    return FileField(note, validators=[
        FileRequired(),
        FileAllowed(images_set, 'Images only!')
    ])

# ---- Safe redirect form support ----
# Credit to Armin Ronacher: http://flask.pocoo.org/snippets/63/
from urlparse import urlparse, urljoin
from flask import request, url_for, redirect

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))

# ---- Forms ----
class UploadAll(FlaskForm):
    filter_regex = TextField("Optional file regex")

class SocialRegister(FlaskForm):
    provider = HiddenField()
    username = _required_text('Your user name')
    email = _required_text('You email')
    first_name = TextField('Optional, first name')
    last_name = TextField('Optional, last name')
    remember = BooleanField('Remember me')

# CRUMBS: add your forms here
