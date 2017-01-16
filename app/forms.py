from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TextField, validators, ValidationError, SubmitField, SelectField, DecimalField, IntegerField
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

# ---- Forms ----
class UploadAll(FlaskForm):
    filter_regex = TextField("Optional file regex")

# CRUMBS: add your forms here
