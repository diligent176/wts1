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
from flask_session import Session
from urllib.parse import urlencode
from cs50 import SQL
import json
import logging
import os
import requests
import secrets
import string
import spotify


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

# environmental constants
CLIENT_ID = os.environ.get("WTS_CLIENT_ID")
CLIENT_SECRET = os.environ.get("WTS_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("WTS_REDIRECT_URI")

# Spotify API endpoints
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'


# set flask app
app = Flask(__name__)
# TO DO: why app.secret_key for flask - signed cookie?
# Session breaks without this...  <SecureCookieSession {}>
app.secret_key = os.urandom(16)

# set flask templates auto-reload
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///wts.db")

# check ENVT VARS are set
if not CLIENT_ID:
    raise RuntimeError("CLIENT_ID not set")
if not CLIENT_SECRET:
    raise RuntimeError("CLIENT_SECRET not set")
if not REDIRECT_URI:
    raise RuntimeError("REDIRECT_URI not set")
else:
    print(f"********* ENVIRONMENT ************")
    print(f"CLIENT_ID IS: {CLIENT_ID}")
    print(f"CLIENT_SECRET IS: {CLIENT_SECRET}")
    print(f"REDIRECT_URI IS: {REDIRECT_URI}")
    print(f"********* END ENVIRONMENT ************")


@app.after_request
def after_request(response):
    # to disable browser caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def index():
    # Welcome and info page
    # ask user to login to Spotify
    return render_template('login.html')


@app.route('/logout')
def sign_out():
    # delete tokens from session and return home
    # TO DO: flash a message?
    session.pop("tokens", None)
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

    # Check state
    if state is None or state != stored_state:
        app.logger.error('Error message: %s', repr(error))
        app.logger.error('State mismatch: %s != %s', stored_state, state)
        abort(400)

    # Request tokens with code we obtained
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

    # Load tokens into session
    session['tokens'] = {
        'access_token': response_data.get('access_token'),
        'refresh_token': response_data.get('refresh_token'),
    }

    return redirect(url_for('me'))


@app.route('/refresh')
def refresh():
    '''Refresh access token.'''

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': session.get('tokens').get('refresh_token'),
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(
        TOKEN_URL, auth=(
            CLIENT_ID, CLIENT_SECRET), data=payload, headers=headers
    )
    response_data = response.json()

    # Load new token into session
    session['tokens']['access_token'] = response_data.get('access_token')

    return json.dumps(session['tokens'])


@app.route('/me')
def me():
    """ Display all current user details """

    # Check tokens
    if 'tokens' not in session:
        app.logger.info('No tokens in session. Redirect user to login.')
        return redirect('/')

    # get user's spotify profile
    me_data = spotify.get_me()
    
    # get user's liked songs
    tracks = spotify.get_liked_songs()

    # get user's playlists
    playlists = spotify.get_playlists()

    # get tracks from each playlist
    pl_tracks = []
    for pl in playlists:
        # get tracks from each playlist
        temp_tracks = spotify.get_playlist_tracks(pl["playlist_url"])

        for track in temp_tracks:
            # add each track to pl_tracks
            pl_tracks.append(track)

    # sort pl_tracks dictionary by track name
    pl_tracks = sorted(pl_tracks, key=lambda d: d['track_name'])
    
    return render_template('me.html', data=me_data, tokens=session.get('tokens'), tracks=tracks, playlists=playlists, pl_tracks=pl_tracks)


@app.route('/liked')
def liked():
    ...


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
