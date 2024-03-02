import re
from flask import Flask
from .extensions import oauth
from .views.main import main
from datetime import timedelta

import os

def create_app():

    # format for ms
    def format_duration(duration_ms):
        minutes = duration_ms // 60000
        seconds = (duration_ms % 60000) // 1000
        return f"{minutes}:{seconds:02}"
    
    # format for iso 8601
    def parse_duration(duration):
        match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration).groups()
        hours = int(match[0][:-1]) if match[0] else 0
        minutes = int(match[1][:-1]) if match[1] else 0
        seconds = int(match[2][:-1]) if match[2] else 0
        return str(timedelta(hours=hours, minutes=minutes, seconds=seconds))

    app = Flask(__name__) 
    app.secret_key = os.getenv('SECRET_KEY')

    app.jinja_env.filters['format_duration'] = format_duration
    app.jinja_env.filters['parse_duration'] = parse_duration

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