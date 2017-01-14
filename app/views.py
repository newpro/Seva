from flask import render_template, request, url_for, current_app, redirect
from flask_user import login_required, roles_required, current_user
from . import app, dbs, db

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

# ---- Non-Management Views ----
@app.route('/')
def index():
    return 'ONLINE'

@app.route('/s3/<path:path>')
def static_file(path):
    #if current_app.config
    return redirect('https://s3.amazonaws.com/firefire/{}'.format(path), code=301)

@app.route('/playground')
def playground():
    return render_template('playground/index.html')
