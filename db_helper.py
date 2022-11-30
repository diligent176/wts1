# CS50 library for easy sqlite usage (wraps SQLAlchemy)
from cs50 import SQL
from datetime import datetime
from flask import session

db = SQL("sqlite:///wts.db")


def set_user(display_name, email, country, uri, url):
    """ set_user: Lookup, and create or update user details after login """
    
    # check if user exists in database
    user = get_db_user(uri)

    if user:
        # Returning user
        print(
            f"Returning user ID {user[0]['id']}: {user[0]['email']}  [{uri}]")

        # UPDATE user details and visited_timestamp
        # TO DO: wrap with try/except? what do when it fails?
        result = update_user(display_name,
                             email,
                             country,
                             user[0]['id']
                             )

        # Load user into session
        session["user_id"] = user[0]['id']
        session["last_visit"] = user[0].get("visited_timestamp")

        # return the existing user id
        return user[0]['id']

    else:
        # CREATE new user record
        # TO DO: wrap with try/except? what do when it fails?
        result = create_user(display_name,
                             email,
                             country,
                             uri,
                             url
                             )

        print(
            f"Created new user ID {result}: {email}  [{uri}]")

        # Load user into session
        session["user_id"] = result
        session["last_visit"] = None

        # return the new user id
        return result


def get_db_user(uri):
    """ GET user profile from db """
    result = db.execute("SELECT id, display_name, email, country, spotify_url, visited_timestamp FROM users WHERE spotify_uri = ?",
                        uri
                        )
    return result


def update_user(display_name, email, country, id):
    """ UPDATE EXISTING user in db """
    result = db.execute("UPDATE users SET display_name = ?, email = ?, country = ?, visited_timestamp = ? WHERE id = ?",
                        display_name,
                        email,
                        country,
                        datetime.utcnow(),
                        id
                        )
    return result


def create_user(display_name, email, country, spotify_uri, spotify_url):
    """ INSERT NEW user in db """
    result = db.execute("INSERT INTO users (display_name, email, country, spotify_uri, spotify_url) VALUES (?, ?, ?, ?, ?)",
                        display_name,
                        email,
                        country,
                        spotify_uri,
                        spotify_url,
                        )
    return result


def get_tracks(user_id):
    """ GET user's tracks from db """
    result = db.execute("SELECT id, track_name, track_artist, track_album, track_uri FROM tracks WHERE user_id = ?",
                        user_id
                        )
    return result


def delete_tracks(user_id):
    """ DELETE user's tracks in db 
        After each login, before inserting new tracks
        Refreshing our view of user's song library on each visit
    """
    result = db.execute("DELETE FROM tracks WHERE user_id = ?",
                        user_id
                        )
    return result


def create_track(user_id, track_name, track_artist, track_album, track_uri):
    """ INSERT user's tracks in db 
        Tracks are deleted then inserted one at a time after login
        Refreshing our view of user's song library on each visit
    """
    result = db.execute("INSERT INTO tracks (user_id, track_name, track_artist, track_album, track_uri) VALUES (?, ?, ?, ?, ?)",
                        user_id,
                        track_name,
                        track_artist,
                        track_album,
                        track_uri
                        )
    return result
