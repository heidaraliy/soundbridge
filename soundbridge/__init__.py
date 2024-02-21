from flask import Flask
from .extensions import oauth
from .views.main import main

import os

def create_app():

    def format_duration(duration_ms):
        minutes = duration_ms // 60000
        seconds = (duration_ms % 60000) // 1000
        return f"{minutes}:{seconds:02}"

    app = Flask(__name__) 
    app.secret_key = os.getenv('SPOTIFY_SECRET_KEY')

    app.jinja_env.filters['format_duration'] = format_duration

    app.register_blueprint(main)

    oauth.init_app(app)

    oauth.register(
        name='spotify',
        client_id= os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET'),
        authorize_url='https://accounts.spotify.com/authorize',
        authorize_params=None,
        base_url = 'https://api.spotify.com/v1/',
        access_token_url='https://accounts.spotify.com/api/token',
        access_token_params = None,
        refresh_token_url=None,
        redirect_uri='http://localhost:5000/callback',
        client_kwargs={'scope': 'user-read-private user-read-email'}
    )

    return app