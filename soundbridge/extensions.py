import os
import pathlib
from authlib.integrations.flask_client import OAuth
from ytmusicapi import YTMusic

oauth = OAuth()

def get_ytmusic_client():
    headers_path = '/Users/heidaraliy/Documents/programs/soundbridge/oauth.json'
    return YTMusic(headers_path)
