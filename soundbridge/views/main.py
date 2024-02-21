# soundbridge/views/main.py
from flask import Blueprint, redirect, url_for, session, render_template
from ..clients.spotify_client import get_user_playlists, get_playlist_tracks, get_playlist_name_by_id
from ..extensions import oauth
from ..extensions import get_ytmusic_client
from authlib.integrations.base_client.errors import OAuthError
import requests

main = Blueprint('main', __name__)

# index/main page
@main.route('/')
def index():
    user_connected_to_spotify = False
    token = session.get('token')

    if token and is_spotify_token_valid(token['access_token']):
        user_connected_to_spotify = True
    else:
        session.pop('token', None)
    return render_template('login.html', user_connected_to_spotify=user_connected_to_spotify)

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
        return redirect(url_for('main.login'))

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
    return render_template('spotify_playlist_tracks.html', tracks=tracks, playlist_name=playlist_name)

def is_spotify_token_valid(token):
    response = requests.get(
        'https://api.spotify.com/v1/me', 
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.status_code == 200

# get youtube playlists
@main.route('/youtube_music_playlists', methods=['GET'])
def show_youtube_music_playlists():
    ytmusic = get_ytmusic_client()  # Ensure this gets the client properly
    youtube_playlists = ytmusic.get_library_playlists()  # Fetch playlists
    playlist_names = [playlist['title'] for playlist in youtube_playlists]
    # You may need to transform `youtube_playlists` to match the expected format in your template
    return render_template('youtube_playlists.html', playlists=playlist_names)




