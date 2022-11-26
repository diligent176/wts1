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
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # # User reached route via POST (as by submitting a form via POST)
    # if request.method == "POST":

    #     # Ensure username was submitted
    #     if not request.form.get("username"):
    #         return apology("must provide username", 403)

    #     # Ensure password was submitted
    #     elif not request.form.get("password"):
    #         return apology("must provide password", 403)

    #     # Query database for username
    #     rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

    #     # Ensure username exists and password is correct
    #     if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
    #         return apology("invalid username and/or password", 403)

    #     # Remember which user has logged in
    #     session["user_id"] = rows[0]["id"]

    #     # Redirect user to home page
    #     return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="9dcdc500adbd4425b3c37fdcc0945bd8",
                                                client_secret="7d299bf748e64bcfb8191cae79c36164",
                                                redirect_uri="http://localhost:8888",
                                                scope="user-library-read"))

    # USER
    # user = sp.user('plamere')
    user = sp.current_user()
    print(user)
    
    # LIKED SONGS list
    tracks = []
    results = sp.current_user_saved_tracks()

    for idx, item in enumerate(results['items']):
        track = item['track']
        tracks.append(f"{idx} {track['artists'][0]['name']} - {track['name']}")
        print(idx, track['artists'][0]['name'], " – ", track['name'])

    return render_template("login.html", tracks=tracks, user=user)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
