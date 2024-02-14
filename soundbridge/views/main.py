# soundbridge/views/main.py
from flask import Blueprint, redirect, url_for, session, render_template
from ..extensions import oauth

main = Blueprint('main', __name__)

@main.route('/login')
def login():
    redirect_uri = url_for('main.authorize', _external=True)
    print("Redirect URI:", redirect_uri)
    return oauth.spotify.authorize_redirect(redirect_uri)

@main.route('/login/authorize')
def authorize():
    token = oauth.spotify.authorize_access_token()
    session['token'] = token
    return redirect(url_for('main.index'))

@main.route('/')
def index():
        return render_template('login.html')

