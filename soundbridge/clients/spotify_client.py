import requests

def get_user_playlists(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
    return response.json()

def get_playlist_tracks(token, playlist_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    response = requests.get(url, headers=headers)
    return response.json()

def get_playlist_name_by_id(token, playlist_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    response = requests.get(url, headers=headers)
    
    if response.ok:
        data = response.json()
        return data['name']
    else:
        response.raise_for_status()


