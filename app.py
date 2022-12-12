from flask import (
    abort,
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_from_directory
)
# from flask_session import Session
from urllib.parse import urlencode
import json
import logging
import os
import requests
import secrets
import string
import db_helper
import game_helper
import spotify_helper
# from spotify_helper import get_me, get_liked_songs, get_playlists, get_playlist_tracks


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR
)

# Spotify AuthN API endpoints
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# FETCH environment constants
CLIENT_ID = os.environ.get("WTS_CLIENT_ID")
CLIENT_SECRET = os.environ.get("WTS_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("WTS_REDIRECT_URI")

# CHECK environment constants
if not CLIENT_ID:
    raise RuntimeError("CLIENT_ID not set")
if not CLIENT_SECRET:
    raise RuntimeError("CLIENT_SECRET not set")
if not REDIRECT_URI:
    raise RuntimeError("REDIRECT_URI not set")


# set flask app
app = Flask(__name__)

# for flask signed cookies
app.secret_key = os.urandom(16)

# set flask templates auto-reload
# app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

MIN_TRACKS_TO_PLAY = 15
ENOUGH_TRACKS = 100


@app.after_request
def after_request(response):
    # to disable browser caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def index():

    # Check if logged in user
    if "user_id" not in session:
        # not logged in - ask user to login w/ Spotify
        return render_template('login.html')

    # Otherwise, user IS logged in... GAME ON

    # find a random track with "good" lyrics

    loops = 0

    while True:
        
        # keep track of how many tries, abort after 10 tracks
        loops += 1
        
        # set "current track" (a random track) and fetch lyrics
        current_track = game_helper.random_track(session["user_id"])

        # genius lyrics are preferred
        genius_lyrics = game_helper.fetch_lyrics(current_track["track_artist"], current_track["track_name"])
        
        if genius_lyrics:
            # print(genius_lyrics)
            lyric = genius_lyrics
            lyric_source = "genius_lyric"
            break

        elif not genius_lyrics:
            # did not find genius lyrics, try chart lyrics search
            chart_lyrics = game_helper.chart_lyrics_search(current_track["track_artist"], current_track["track_name"])

            if chart_lyrics:
                lyric = chart_lyrics
                lyric_source = "chart_lyric"
                break

        # no lyrics found, keep looping through random tracks up to 10x
        else:
            print(f"No lyrics found on attempt {loops}.  Trying again...")
            if loops > 10:
                # TO DO: return page "sorry, something went wrong... Try again?"
                break

    # get a lyric snip
    if lyric:
        # TO DO: use difficulty setting for number of words
        snip = game_helper.get_word_snip(lyric, 20, current_track["track_name"])

    # current_track has a good lyric, mark it "correct"
    current_track["correct"] = True
    cur_track_detail = spotify_helper.get_track(current_track["track_uri"])

    # setup dict with 1 correct track, plus decoy tracks
    game_tracks = []
    game_tracks.append(current_track)

    # get 3 other decoy tracks 
    # TO DO: number of decoys should be variable based on difficulty level
    while len(game_tracks) < 4:
        random = game_helper.random_track(session["user_id"])

        # check it's not duplicate
        for track in game_tracks:
            if random["track_name"] == track["track_name"]:
                # duplicate. quit loop, get another random track
                break

        game_tracks.append(random)

    # Play the game round
    return render_template('game.html', current_track=current_track, lyric=lyric, lyric_source=lyric_source, game_tracks=game_tracks, snip=snip, detail=cur_track_detail)


@app.route('/logout')
def sign_out():
    # delete tokens from session and return home
    # TO DO: flash a message?
    session.pop("tokens", None)
    session.pop("user_id", None)
    return redirect('/')


@app.route('/login')
def login():

    # because redirect_uri could be guessed
    # generate random state to prevent CSRF
    state = ''.join(secrets.choice(string.ascii_uppercase +
                    string.digits) for _ in range(16))

    # Request user to authorize these scopes
    scope = 'user-read-private user-read-email user-library-read'
    # scope = 'user-read-private user-read-email'     # TO DO: test errors cases with insufficient scopes

    payload = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state,
        'scope': scope,
    }

    response = make_response(redirect(f'{AUTH_URL}/?{urlencode(payload)}'))
    response.set_cookie('spotify_auth_state', state)

    return response


@app.route('/callback')
def callback():
    error = request.args.get('error')
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = request.cookies.get('spotify_auth_state')

    # Check for state tampering
    if state is None or state != stored_state:
        app.logger.error('Error message: %s', repr(error))
        app.logger.error('State mismatch: %s != %s', stored_state, state)
        abort(400)

    # Request tokens using code from callback
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }

    # auth=(CLIENT_ID, SECRET) wraps an 'Authorization' header with value:
    # b'Basic ' + b64encode((CLIENT_ID + ':' + SECRET).encode())
    response = requests.post(TOKEN_URL, auth=(
        CLIENT_ID, CLIENT_SECRET), data=payload)
    response_data = response.json()

    if response_data.get('error') or response.status_code != 200:
        app.logger.error(
            'Failed to receive token: %s',
            response_data.get('error', 'No error information received.'),
        )
        abort(response.status_code)

    # Load Spotify API tokens into session
    session['tokens'] = {
        'access_token': response_data.get('access_token'),
        'refresh_token': response_data.get('refresh_token'),
    }

    # fetch user's spotify profile
    me = spotify_helper.get_me()

    # SET USER (create/update user)
    user_id = db_helper.set_user(me.get("display_name"),
                       me.get("email"),
                       me.get("country"),
                       me.get("uri"),
                       me.get("external_urls").get("spotify")
                       )

    # Refresh user tracks in db
    tracks_count = build_songs_db(user_id)

    if tracks_count < MIN_TRACKS_TO_PLAY:
        # TO DO: redirect to sorry page, not enough tracks to play
        return redirect(url_for('me'))

    # login processing completed, go to game
    return redirect('/')


@app.route('/refresh')
def refresh():
    """ Refresh access token
    """
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': session.get('tokens').get('refresh_token'),
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(TOKEN_URL, auth=(
        CLIENT_ID, CLIENT_SECRET), data=payload, headers=headers)
    response_data = response.json()

    # Load new token into session
    session['tokens']['access_token'] = response_data.get('access_token')

    return json.dumps(session['tokens'])


@app.route('/me')
def me():
    """ Display all current user details """

    # Check tokens
    if "tokens" not in session:
        app.logger.info('No tokens in session. Redirect user to login.')
        return redirect('/')

    # get user's spotify profile
    me = spotify_helper.get_me()

    # get user's liked songs
    tracks = spotify_helper.get_liked_songs()

    # get user's playlists
    playlists = spotify_helper.get_playlists()

    # get tracks from each playlist
    pl_tracks = []
    for pl in playlists:
        # get tracks from each playlist
        temp_tracks = spotify_helper.get_playlist_tracks(pl["playlist_url"])

        for track in temp_tracks:
            # add each track to pl_tracks
            pl_tracks.append(track)

    # remove duplicates from pl_tracks
    unique_pl_tracks = [dict(t) for t in {tuple(d.items()) for d in pl_tracks}]

    # sort unique_pl_tracks dict by track name
    unique_pl_tracks = sorted(unique_pl_tracks, key=lambda d: d['track_name'])

    return render_template('me.html', data=me, tokens=session.get('tokens'), tracks=tracks, playlists=playlists, pl_tracks=pl_tracks)


@app.route('/liked')
def liked():
    ...


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def build_songs_db(user_id):
    """ Build the user's song list in the database """

    tracks_count = 0

    # get user's liked songs
    liked_tracks = spotify_helper.get_liked_songs()

    # delete this user's tracks from db
    deleted_count = db_helper.delete_tracks(user_id)

    # insert liked tracks to database
    for track in liked_tracks:
        db_helper.create_track(user_id, track["track_name"], track["track_artist"], track["track_album"], track["track_uri"])
        tracks_count += 1

    if tracks_count < ENOUGH_TRACKS:
        # not enough tracks yet, get user's playlists
        playlists = spotify_helper.get_playlists()

        # get tracks from each playlist
        pl_tracks = []
        for pl in playlists:
            # get tracks from each playlist
            temp_tracks = spotify_helper.get_playlist_tracks(pl["playlist_url"])

            for track in temp_tracks:
                # add each track to pl_tracks
                pl_tracks.append(track)

        # remove duplicates from pl_tracks
        unique_pl_tracks = [dict(t) for t in {tuple(d.items()) for d in pl_tracks}]

        # sort unique_pl_tracks dict by track name
        unique_pl_tracks = sorted(unique_pl_tracks, key=lambda d: d['track_name'])

        # insert playlist tracks to database
        for track in unique_pl_tracks:
            db_helper.create_track(user_id, track["track_name"], track["track_artist"], track["track_album"], track["track_uri"])
            tracks_count += 1

    # return total count of tracks inserted for the user
    return tracks_count
