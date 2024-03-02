from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError


def get_youtube_playlists(credentials_dict):
    credentials = Credentials(**credentials_dict)
    youtube = build('youtube', 'v3', credentials=credentials)

    playlists = []

    request = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=25  # You can adjust this value
    )

    while request is not None:
        response = request.execute()

        for playlist in response.get('items', []):
            playlists.append({
                'id': playlist['id'],
                'title': playlist['snippet']['title'],
                'itemCount': playlist['contentDetails']['itemCount']
            })

        request = youtube.playlists().list_next(request, response)

    return playlists

def get_youtube_playlist_name(credentials_dict, playlist_id):
    credentials = Credentials(**credentials_dict)
    youtube = build('youtube', 'v3', credentials=credentials)

    response = youtube.playlists().list(
        part="snippet",
        id=playlist_id
    ).execute()

    if 'items' in response and response['items']:
        return response['items'][0]['snippet']['title']
    else:
        return "Unknown Playlist"

def get_youtube_playlist_tracks(credentials_dict, playlist_id):
    credentials = Credentials(**credentials_dict)
    youtube = build('youtube', 'v3', credentials=credentials)

    video_ids = []
    videos = []

    try:
        # First, get all video IDs from the playlist
        nextPageToken = None
        while True:
            response = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=nextPageToken
            ).execute()

            video_ids += [item['snippet']['resourceId']['videoId'] for item in response['items']]
            nextPageToken = response.get('nextPageToken')
            if not nextPageToken:
                break

        # Fetch details in batches
        for i in range(0, len(video_ids), 50):  # YouTube API allows a max of 50 IDs per request
            batch_ids = video_ids[i:i+50]
            video_response = youtube.videos().list(
                part="snippet,contentDetails",
                id=','.join(batch_ids)
            ).execute()

            for video_item in video_response.get('items', []):
                video = {
                    'title': video_item['snippet']['title'],
                    'artist': video_item['snippet']['channelTitle'],
                    'duration': video_item['contentDetails']['duration'],  # ISO 8601 format
                    'videoId': video_item['id']
                }
                videos.append(video)

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")

    return videos


