# soundbridge/views/main.py
import os
import requests

from flask import Blueprint, redirect, request, url_for, session, render_template
from ..clients.spotify_client import get_user_playlists, get_playlist_tracks, get_playlist_name_by_id
from ..clients.youtube_client import get_youtube_playlist_tracks, get_youtube_playlists, get_youtube_playlist_name
from google_auth_oauthlib.flow import Flow
from ..extensions import oauth
from authlib.integrations.base_client.errors import OAuthError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

main = Blueprint('main', __name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # dont use in prod

# index/main page
@main.route('/')
def index():
    user_connected_to_spotify = False
    user_connected_to_youtube = False
    spotify_token = session.get('token')
    youtube_credentials = session.get('youtube_credentials')

    if spotify_token and is_spotify_token_valid(spotify_token['access_token']):
        user_connected_to_spotify = True
    else:
        session.pop('token', None)
    
    youtube_credentials = session.get('youtube_credentials')
    if youtube_credentials:
        credentials = Credentials(**youtube_credentials)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            session['youtube_credentials'] = credentials_to_dict(credentials)
            user_connected_to_youtube = True
        elif not credentials.expired:
            user_connected_to_youtube = True

    return render_template('login.html', 
                           user_connected_to_spotify=user_connected_to_spotify,
                           user_connected_to_youtube=user_connected_to_youtube)

# auth route to spotify
@main.route('/spotify_login')
def spotify_login():
    redirect_uri = url_for('main.spotify_authorize', _external=True)
    print("Redirect URI:", redirect_uri)
    return oauth.spotify.authorize_redirect(redirect_uri)

# auth spotify w/ callback
@main.route('/spotify_login/authorize')
def spotify_authorize():
    try:
        token = oauth.spotify.authorize_access_token()
        session['token'] = token
        return redirect(url_for('main.index'))
    except OAuthError as error:
        print("OAuthError occurred: ", error)
        return render_template('login.html', error=error.description)

# get spotify playlists
@main.route('/spotify_playlists/page/<int:page>', methods=['GET'])
def show_spotify_playlists(page=1):
    per_page = 5
    token = session.get('token')
    
    if not token:
        return redirect(url_for('main.spotify_login'))

    playlists = get_user_playlists(token['access_token'])
    total_playlists = len(playlists['items'])
    playlists_to_show = playlists['items'][(page-1)*per_page:page*per_page]

    return render_template('spotify_playlists.html', 
                           playlists=playlists_to_show, 
                           total_playlists=total_playlists, 
                           per_page=per_page, 
                           current_page=page)

# get spotify playlist details
@main.route('/spotify_playlists/<playlist_id>')
def show_spotify_playlist_tracks(playlist_id):
    token = session.get('token')
    if not token:
        return redirect(url_for('main.login'))
    
    tracks = get_playlist_tracks(token['access_token'], playlist_id)
    playlist_name = get_playlist_name_by_id(token['access_token'], playlist_id)
    print("Playlist Name:", playlist_name)
    return render_template('spotify_playlist_tracks.html', 
                           tracks=tracks, 
                           playlist_name=playlist_name)

# spotify token check
def is_spotify_token_valid(token):
    response = requests.get(
        'https://api.spotify.com/v1/me', 
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.status_code == 200

@main.route('/youtube_login')
def youtube_login():
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    redirect_uri = os.getenv('YOUTUBE_REDIRECT_URI')

    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/youtube'],
        redirect_uri=redirect_uri
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state

    return redirect(authorization_url)

@main.route('/youtube_login/authorize')
def youtube_authorize():

    state = session['state']
    redirect_uri=os.getenv('YOUTUBE_REDIRECT_URI')

    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/youtube'],
        state=state,
        redirect_uri=redirect_uri
    )

    flow.fetch_token(authorization_response=request.url)

    youtube_credentials = flow.credentials

    if not youtube_credentials.valid:
        return 'Invalid credentials', 401

    youtube_credentials_dict = {
        'token': youtube_credentials.token,
        'refresh_token': youtube_credentials.refresh_token,
        'token_uri': youtube_credentials.token_uri,
        'client_id': youtube_credentials.client_id,
        'client_secret': youtube_credentials.client_secret,
        'scopes': youtube_credentials.scopes
    }

    session['youtube_credentials'] = youtube_credentials_dict
    print("Redirect URI:", redirect_uri)

    return redirect(url_for('main.index'))

@main.route('/youtube_playlists/page/<int:page>')
def show_youtube_playlists(page=1):
    per_page = 5

    youtube_credentials = session.get('youtube_credentials')

    if not youtube_credentials:
        return redirect(url_for('main.youtube_authorize'))

    playlists = get_youtube_playlists(youtube_credentials)
    total_playlists = len(playlists)
    playlists_to_show = playlists[(page-1)*per_page:page*per_page]

    return render_template('youtube_playlists.html', 
                           playlists=playlists_to_show,
                           total_playlists=total_playlists,
                           per_page=per_page,
                           current_page=page)

@main.route('/youtube_playlists/<playlist_id>')
def show_youtube_playlist_tracks(playlist_id):
    youtube_credentials = session.get('youtube_credentials')

    if not youtube_credentials:
        return redirect(url_for('main.youtube_login'))

    tracks = get_youtube_playlist_tracks(youtube_credentials, playlist_id)
    playlist_name = get_youtube_playlist_name(youtube_credentials, playlist_id)

    return render_template('youtube_playlist_tracks.html', 
                           tracks=tracks, 
                           playlist_name=playlist_name)



def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
# playlist transfer page
@main.route('/playlist_transfers')
def playlist_transfers():
    user_connected_to_spotify = False
    user_connected_to_youtube = False
    spotify_token = session.get('token')
    youtube_credentials = session.get('youtube_credentials')

    if spotify_token and is_spotify_token_valid(spotify_token['access_token']):
        user_connected_to_spotify = True
    else:
        session.pop('token', None)
    
    youtube_credentials = session.get('youtube_credentials')
    if youtube_credentials:
        credentials = Credentials(**youtube_credentials)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            session['youtube_credentials'] = credentials_to_dict(credentials)
            user_connected_to_youtube = True
        elif not credentials.expired:
            user_connected_to_youtube = True

    return render_template('playlist_transfers.html', 
                           user_connected_to_spotify=user_connected_to_spotify,
                           user_connected_to_youtube=user_connected_to_youtube)



