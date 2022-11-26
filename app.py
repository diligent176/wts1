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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    # to disable browser caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():

    return render_template("hello.html")


@app.route("/play")
def play():
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="9dcdc500adbd4425b3c37fdcc0945bd8",
                                                client_secret="7d299bf748e64bcfb8191cae79c36164",
                                                redirect_uri="http://127.0.0.1:9899",
                                                scope="user-library-read"))

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
