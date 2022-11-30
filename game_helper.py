import db_helper
from random import randrange


def random_track(user_id):
    """ Pick a random track from user's library 
        Returns a dict with track details
    """

    # select track id's belonging to this user
    tracks = db_helper.get_tracks(user_id)

    # pick a randoml index (id), between 0 and # of tracks
    random_index = randrange(0, len(tracks))

    random_track = {
        "track_name": tracks[random_index].get("track_name"),
        "track_artist": tracks[random_index].get("track_artist"),
        "track_album": tracks[random_index].get("track_album"),
        "track_uri": tracks[random_index].get("track_uri"),
    }

    return random_track


def fetch_lyrics():
    """ Get Song Lyrics from Genius.com """
    ...
