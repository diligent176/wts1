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
# PLAYLISTITEMS_URL = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
# e.g. get tracks at https://api.spotify.com/v1/playlists/27hR4eUcVxpfZzZT7hKd4A/tracks


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
            f"get_me() failed - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
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
            f"get_liked_songs() failed - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
        # TO DO: handle 403 and other errors gracefully
        abort(response.status_code)

    for idx, item in enumerate(response_data["items"]):
        track = item["track"]
        # tracks.append(f"{(idx+1):02d} - {track['name']} ({track['artists'][0]['name']})")
        # print(f"{(idx+1):02d} - {track['name']} ({track['artists'][0]['name']})")

        tracks.append(
            {
                "number": f"{(idx+1):02d}",
                "track_name": item.get("track").get("name"),
                "track_album": item.get("track").get("album").get("name"),
                "track_artist": item.get("track").get("artists")[0].get("name"),
                "track_uri": item.get("track").get("uri"),
            }
        )

    return tracks


def get_playlists():
    """Current user's Spotify Playlists
    Note: does not return each Track, need to call get_playlist_tracks()
    https://developer.spotify.com/console/get-current-user-playlists/
    """
    playlists = []
    auth_header = get_auth_header()

    response = requests.get(PLAYLISTS_URL, headers=auth_header)
    response_data = response.json()

    if response.status_code != 200:
        logging.error(
            f"get_playlists() failed - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
        # TO DO: handle 403 and other errors gracefully
        abort(response.status_code)

    # for idx, item in enumerate(response_data["items"]):
    for item in response_data["items"]:
        playlists.append(
            {
                "name": item["name"],
                "id": item["id"],
                "public": item["public"],
                "playlist_url": item["href"],
                "tracks_url": item["tracks"].get("href"),
                "tracks_count": item["tracks"].get("total"),
                "image0": item.get("images")[0].get("url"),
            }
        )
        # print(f"{idx} {item}")
    
    sorted_playlists = sorted(playlists, key=lambda d: d['tracks_count'], reverse=True)

    return sorted_playlists


def get_playlist_tracks(playlist_url):
    """ get tracks from a playlist
    https://developer.spotify.com/console/get-playlist-tracks/
    """
    playlist_tracks = []
    auth_header = get_auth_header()

    response = requests.get(playlist_url, headers=auth_header)
    response_data = response.json()

    if response.status_code != 200:
        logging.error(
            f"get_playlist_tracks() failed - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
        # TO DO: handle 403 and other errors gracefully
        abort(response.status_code)

    # for idx, item in enumerate(response_data["items"]):
    for item in response_data["tracks"]["items"]:
        playlist_tracks.append(
            {
                "track_id": item.get("track").get("id"),
                "track_name": item.get("track").get("name"),
                "track_artist": item.get("track").get("artists")[0].get("name"),
                "track_album": item.get("track").get("album").get("name"),
                "track_uri": item.get("track").get("uri"),
                "track_href": item.get("track").get("href"),
                "image0": item.get("track").get("album").get("images")[0].get("url"),
            }
        )
    
    sorted_tracks = sorted(playlist_tracks, key=lambda d: d['track_name'])

    return sorted_tracks


def get_auth_header():
    """ Assemble the bearer token for various API calls """
    at = session['tokens'].get('access_token')
    bt = {'Authorization': f"Bearer {at}"}
    return bt
