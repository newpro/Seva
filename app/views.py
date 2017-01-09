from flask import render_template, request, flash, abort, url_for, current_app
from flask.views import View, MethodView
from flask_user import login_required, roles_required, current_user
from . import app

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
