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
TRACK_DETAIL_URL = "https://api.spotify.com/v1/tracks"
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

    response = requests.get(f"{LIKED_URL}?limit=50", headers=auth_header)
    response_data = response.json()

    if response.status_code != 200:
        logging.error(
            f"get_liked_songs() failed - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
        # TO DO: handle 403 and other errors gracefully
        abort(response.status_code)

    # keep fetching if there is "next page" in result json
    next_page = response_data.get("next")

    while True:
        for idx, item in enumerate(response_data["items"]):
            tracks.append(
                {
                    "number": f"{(idx+1):02d}",
                    "track_name": item.get("track").get("name"),
                    "track_album": item.get("track").get("album").get("name"),
                    "track_artist": item.get("track").get("artists")[0].get("name"),
                    "track_uri": item.get("track").get("uri"),
                }
            )

        if next_page:
            # fetch next 50
            more = requests.get(next_page, headers=auth_header)
            response_data = more.json()
            next_page = response_data.get("next")
        else:
            # no more results to fetch
            break

    return tracks


def get_playlists():
    """Current user's Spotify Playlists
    Note: does not return each Track, need to call get_playlist_tracks()
    https://developer.spotify.com/console/get-current-user-playlists/
    """
    playlists = []
    auth_header = get_auth_header()

    response = requests.get(f"{PLAYLISTS_URL}?limit=50", headers=auth_header)
    response_data = response.json()

    if response.status_code != 200:
        logging.error(
            f"get_playlists() failed - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
        # TO DO: handle 403 and other errors gracefully
        abort(response.status_code)

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


def get_track(track_uri):
    """ Fetch spotify track details """
    auth_header = get_auth_header()

    track_id = track_uri.split(":")[-1]

    response = requests.get(f"{TRACK_DETAIL_URL}/{track_id}", headers=auth_header)
    response_data = response.json()

    if response.status_code != 200:
        logging.error(
            f"get_track() failed - HTTP {response.status_code} {response_data.get('error', 'No error message was returned.')}")
        # TO DO: handle 403 and other errors gracefully
        abort(response.status_code)

    return response_data


def get_auth_header():
    """ Assemble the bearer token for various API calls """
    at = session['tokens'].get('access_token')
    bt = {'Authorization': f"Bearer {at}"}
    return bt
