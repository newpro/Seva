from flask import render_template, request, flash, abort, url_for

from . import app

@app.route('/')
def index():
    return 'ONLINE'
