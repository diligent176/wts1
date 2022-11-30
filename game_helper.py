import db_helper
import requests
from random import randrange
from bs4 import BeautifulSoup

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


def fetch_lyrics(track_artist, track_name):
    """ Get Song Lyrics from Genius.com """

    artistname2 = str(track_artist.replace(' ','-')) if ' ' in track_artist else str(track_artist)
    songname2 = str(track_name.replace(' ','-')) if ' ' in track_name else str(track_name)
    
    # url = 'https://genius.com/'+ artistname2 + '-' + songname2 + '-' + 'lyrics'
    url = f"https://genius.com/{artistname2}-{songname2}-lyrics".replace('...','-')
    page = requests.get(url)

    html = BeautifulSoup(page.text, 'html.parser')
    lyrics1 = html.find("div", class_="lyrics")
    
    # lyrics1 = html.find(id="lyrics")
    # lyrics1 = html.find("div", {"class": "Lyrics__Container-sc-1ynbvzw-6 YYrds"})
    # lyrics1 = html.class("Lyrics__Container-sc-1ynbvzw-6 YYrds")
    # soup.find("span", {"class": "real number", "data-value": True})['data-value']

    lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")

    if lyrics1:
        lyrics = lyrics1.get_text()
    elif lyrics2:
        # lyrics2.replace('<br>','\r\n')
        # lyrics = lyrics2.get_text()
        lyrics = lyrics2.get_text(separator='\r\n')
        # lyrics = lyrics2.replace('<br>','\r\n').get_text()
    elif lyrics1 == lyrics2 == None:
        lyrics = None
    return lyrics
