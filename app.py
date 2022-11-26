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

    print(f"RENDERING HELLO.HTML: {API_KEY}")
    
    return render_template("hello.html", API_KEY=API_KEY)


@app.route("/play")
def play():
    
    print(f"************* BEFORE SpotifyOAuth *************")
    
    # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="9dcdc500adbd4425b3c37fdcc0945bd8",
    #                                             client_secret="7d299bf748e64bcfb8191cae79c36164",
    #                                             redirect_uri="http://127.0.0.1:9899",
    #                                             scope="user-library-read"))

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read"))

    print(f"************* GET CURRENT USER *************")
    # CURRENT USER
    user = sp.current_user()
    print(user)
    
    # LIKED SONGS list
    tracks = []
    results = sp.current_user_saved_tracks()

    for idx, item in enumerate(results['items']):
        track = item['track']
        tracks.append(f"{idx} {track['artists'][0]['name']} - {track['name']}")
        print(idx, track['artists'][0]['name'], " – ", track['name'])

    return render_template("game.html", tracks=tracks, user=user)


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="9dcdc500adbd4425b3c37fdcc0945bd8",
#                                                 client_secret="7d299bf748e64bcfb8191cae79c36164",
#                                                 redirect_uri="http://localhost:8888",
#                                                 scope="user-library-read"))

#     # USER
#     # user = sp.user('plamere')
#     user = sp.current_user()
#     print(user)
    
#     # LIKED SONGS list
#     tracks = []
#     results = sp.current_user_saved_tracks()

#     for idx, item in enumerate(results['items']):
#         track = item['track']
#         tracks.append(f"{idx} {track['artists'][0]['name']} - {track['name']}")
#         print(idx, track['artists'][0]['name'], " – ", track['name'])

#     return render_template("login.html", tracks=tracks, user=user)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
