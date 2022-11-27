from flask import redirect, render_template, request, session, abort
from functools import wraps
import logging
# import os
import requests
# import urllib.parse
# import app


ME_URL = "https://api.spotify.com/v1/me"
LIKED_URL = "https://api.spotify.com/v1/me/tracks"
PLAYLISTS_URL = "https://api.spotify.com/v1/me/playlists"

def get_me():
    """ Current user's Spotify profile
    https://developer.spotify.com/console/get-current-user/
    """
    auth_header = get_auth_header()
    # auth_header = {'Authorization': f"Bearer {session['tokens'].get('access_token')}"}

    response = requests.get(ME_URL, headers=auth_header)
    response_data = response.json()

    if response.status_code != 200:
        logging.error(
            f"Failed in get_me() - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
        # TO DO: handle 403 and other errors gracefully
        abort(response.status_code)

    return response_data


def get_liked_songs():
    """ LIKED songs a.k.a. user's saved tracks
    https://developer.spotify.com/console/get-current-user-saved-tracks
    """
    tracks = []
    auth_header = get_auth_header()

    response = requests.get(LIKED_URL, headers=auth_header)
    response_data = response.json()

    if response.status_code != 200:
        logging.error(
            f"Failed in get_liked_songs() - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
        # TO DO: handle 403 and other errors gracefully
        abort(response.status_code)

    for idx, item in enumerate(response_data["items"]):
        track = item["track"]
        tracks.append(f"{idx} {track['artists'][0]['name']} - {track['name']}")
        print(f"{idx} {track['artists'][0]['name']} – {track['name']}")

    return tracks


def get_playlists():
    """Current user's Spotify Playlists
    https://developer.spotify.com/console/get-current-user-playlists/
    """
    playlists = []
    auth_header = get_auth_header()


def get_auth_header():

    at = session['tokens'].get('access_token')
    bt = {'Authorization': f"Bearer {at}"}
    return bt
