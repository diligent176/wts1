import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wts.db")

# check if API_KEY and SPOTIPY VARS are set
API_KEY = os.environ.get("API_KEY")
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")
if not API_KEY:
    raise RuntimeError("API_KEY not set")
if not SPOTIPY_CLIENT_ID:
    raise RuntimeError("SPOTIPY_CLIENT_ID not set")
if not SPOTIPY_CLIENT_SECRET:
    raise RuntimeError("SPOTIPY_CLIENT_SECRET not set")
if not SPOTIPY_REDIRECT_URI:
    raise RuntimeError("SPOTIPY_REDIRECT_URI not set")
else:
    print(f"********* ENVIRONMENT ************")
    print(f"API_KEY IS: {API_KEY}")
    print(f"SPOTIPY_CLIENT_ID IS: {SPOTIPY_CLIENT_ID}")
    print(f"SPOTIPY_CLIENT_SECRET IS: {SPOTIPY_CLIENT_SECRET}")
    print(f"SPOTIPY_REDIRECT_URI IS: {SPOTIPY_REDIRECT_URI}")
    print(f"********* END ENVIRONMENT ************")


@app.after_request
def after_request(response):
    # to disable browser caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():


    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-library-read user-read-email user-read-private',
                                               cache_handler=cache_handler,
                                               show_dialog=True)

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        print(f"************* STEP 2 SpotifyOAuth *************")
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        print(f"************* STEP 1 SpotifyOAuth *************")
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 3. Signed in, display data
    print(f"************* STEP 3 SpotifyOAuth SIGNED IN *************")
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # return f'<h2>Hi {spotify.me()["display_name"]}, ' \
    #        f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
    #        f'<a href="/playlists">my playlists</a> | ' \
    #        f'<a href="/currently_playing">currently playing</a> | ' \
    #     f'<a href="/current_user">me</a>' \

    print(f"************* GET CURRENT USER *************")
    # CURRENT USER
    user = spotify.current_user()
    print(user)
    
    # LIKED SONGS list
    tracks = []
    results = spotify.current_user_saved_tracks()

    for idx, item in enumerate(results['items']):
        track = item['track']
        tracks.append(f"{idx} {track['artists'][0]['name']} - {track['name']}")
        print(idx, track['artists'][0]['name'], " – ", track['name'])

    return render_template("game.html", tracks=tracks, user=user)



@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')


@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()

