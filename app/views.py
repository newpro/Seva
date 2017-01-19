from flask import render_template, request, url_for, current_app, redirect, flash
from flask_user import login_required, roles_required, current_user
from . import app, dbs, db, forms
from flask_s3 import create_all
from flask_login import login_user

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
        return redirect(url_for('user/login', next=request.url))

class UserAdmin(AdminView):
    column_exclude_list = column_restrictions['User']
    form_excluded_columns = column_restrictions['User']

# -- load management views --
admin = Admin(app, name='flaskboost', template_mode='bootstrap3')
admin.add_view(UserAdmin(dbs.User, db.session))
admin.add_view(AdminView(dbs.Role, db.session))

@app.route('/upload', methods=['POST', 'GET'])
def upload_all():
    form = forms.UploadAll()
    if form.validate_on_submit():
        create_all(app, filepath_filter_regex=form.filter_regex.data)
        flash('upload success')
    return render_template('admin/upload.html', form=form)

# ---- Non-Management Views ----
@app.route('/')
def index():
    return 'ONLINE'

@app.route('/playground')
def playground():
    return render_template('playground/index.html')

from oauths import OAuthBase
@app.route('/oauth/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthBase.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthBase.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = dbs.User.query.filter_by(social_id=social_id).first()
    if not user:
        form = forms.SocialRegister()
        form.username.data = username
        form.email.data = email
        form.provider.data = provider
        return render_template('soc_user/finish.html', form=form, provider=provider)
    login_user(user, remember=form.remember.data)
    return redirect(url_for('index'))

@app.route('/oauth_finish', methods=['POST', 'GET'])
def oauth_finish():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    form = forms.SocialRegister()
    if request.method == 'POST' and form.validate():
        user = dbs.User(username=form.username.data, email=form.email.data,
                        first_name = form.first_name.data, last_name = form.last_name.data).pip()
        user.add_role('user')
        user.add_social(form.provider.data)
        flash('Register success!')
        login_user(user, remember=form.remember.data)
        return redirect(url_for('index'))
    return render_template('soc_user/finish.html', form=form, provider=provider)
