# from flask import redirect, render_template, request, session, abort
# from functools import wraps
# import logging
# # import os
# import requests
# # import urllib.parse
# # import app

from cs50 import SQL
from datetime import datetime

# CS50 library for easy sqlite usage (wraps SQLAlchemy)
db = SQL("sqlite:///wts.db")


def get_user(uri):
    """ GET user profile from db
    """
    result = db.execute("SELECT id, display_name, email, country, spotify_url, visited_timestamp FROM users WHERE spotify_uri = ?",
                        uri
                        )
    return result


def update_user(display_name, email, country, id):
    """ UPDATE EXISTING user in db
    """
    result = db.execute("UPDATE users SET display_name = ?, email = ?, country = ?, visited_timestamp = ? WHERE id = ?",
                        display_name,
                        email,
                        country,
                        datetime.utcnow(),
                        id
                        )
    return result


def create_user(display_name, email, country, spotify_uri, spotify_url):
    """ CREATE NEW user in db
    """
    result = db.execute("INSERT INTO users (display_name, email, country, spotify_uri, spotify_url) VALUES (?, ?, ?, ?, ?)",
                        display_name,
                        email,
                        country,
                        spotify_uri,
                        spotify_url,
                        )
    return result
