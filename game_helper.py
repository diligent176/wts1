import db_helper
import requests
from random import randrange
from bs4 import BeautifulSoup
import urllib.parse
import xmltodict
import logging


from pprint import pprint

CHART_LYRICS_API_SEARCH_URL = "http://api.chartlyrics.com/apiv1.asmx/SearchLyric"
CHART_LYRICS_API_GETLYRIC_URL = "http://api.chartlyrics.com/apiv1.asmx/GetLyric"


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

    # artistname2 = str(track_artist.replace(' ','-')) if ' ' in track_artist else str(track_artist)
    # songname2 = str(track_name.replace(' ','-')) if ' ' in track_name else str(track_name)

    artistname = fix_name(track_artist)
    songname = fix_name(track_name)

    # url = 'https://genius.com/'+ artistname + '-' + songname + '-' + 'lyrics'
    url = f"https://genius.com/{artistname}-{songname}-lyrics".replace(
        '...', '-').replace('-/-', '-')
    page = requests.get(url)

    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")
    if lyrics:
        lyrics = lyrics.get_text(separator='\r\n')
        # lyrics = lyrics2.replace('<br>','\r\n').get_text()

    return lyrics


def chart_lyrics_search(artist, song):
    """ Search for song lyrics on http://www.chartlyrics.com/api.aspx 
        Input: artist name + song name
        Returns: list of matches ranked by relevance
            GET: http://api.chartlyrics.com/apiv1.asmx/SearchLyric?artist=lynyrd%20skynyrd&song=sweet%20home%20alabama
            GET: http://api.chartlyrics.com/apiv1.asmx/SearchLyric?artist=incubus&song=anna%20molly
    """

    # TO DO: some character stripping and replacement in artist/song for better search result
    artist = artist.replace('/', ' ')
    song = song.replace('/', ' ')
    ...

    # url encode spaces and other characters in names
    # some pre-cleansing will be done beforehand by the calling routine
    get_params = urllib.parse.urlencode({"artist": artist, "song": song})

    # CHART_LYRICS_API_SEARCH_URL
    url = f"{CHART_LYRICS_API_SEARCH_URL}?{get_params}"

    # is there a better request library for XML?
    print(f"\n\n GETTING: {url} \n\n")
    response = requests.get(url)

    # check HTTP result code first
    if response.status_code != 200:
        logging.error(
            f"HTTP error {response.status_code} from Chart Lyrics API [SearchLyric]")
        return None

    # https://github.com/martinblech/xmltodict
    # parse XML response
    response_dict = xmltodict.parse(response.content, process_namespaces=False)
    results_dict = response_dict.get("ArrayOfSearchLyricResult")

    # pprint(results_dict["SearchLyricResult"])
    # print(
    #     f"\n\nLENGTH OF results_dict: {len(results_dict['SearchLyricResult'])}\n\n")

    if results_dict:
        # if SearchLyricResult was present in the XML
        # check if they have required LyricChecksum and LyricId
        search_hits = []

        for idx, item in enumerate(results_dict["SearchLyricResult"]):

            try:
                # confirm each result in dict has these fields
                lyric_checksum = item.get("LyricChecksum")
                lyric_id = int(item.get("LyricId"))

            except (AttributeError, TypeError):
                # empty result may not be a dict
                # carry on...
                continue

            if lyric_checksum and lyric_id > 0:
                # viable search result
                search_hits.append(
                    {
                        "LyricId": lyric_id,
                        "LyricChecksum": lyric_checksum,
                        "Artist": item.get("Artist"),
                        "Song": item.get("Song"),
                        "ResultNumber": idx,
                        "LyricURL": f"{CHART_LYRICS_API_GETLYRIC_URL}?lyricId={lyric_id}&lyricCheckSum={lyric_checksum}",
                    }
                )

        # pprint(search_hits)
        # print(f"\n\nLENGTH OF search_hits: {len(search_hits)}\n\n")

    # If no good result, try cutting words from song or artist...

    # pick the best result and call chart_lyrics_get_lyric()
    # for hit in search_hits:
        # confirm artist and track name are a close match
        # are a match for the specified artist and song

    # return ONE best lyric from Chart Lyrics
    if not search_hits:
        return None
    else:
        the_lyric = chart_lyrics_get_lyric(search_hits[0]["LyricId"],
                                           search_hits[0]["LyricChecksum"]
                                           )

    return the_lyric


def chart_lyrics_get_lyric(lyric_id, checksum):
    """ Get lyric text for specific song from http://www.chartlyrics.com/api.aspx 
        Input: lyricId & lyricCheckSum found by chart_lyrics_search()
            GET: http://api.chartlyrics.com/apiv1.asmx/GetLyric?lyricId=20913&lyricCheckSum=9a51548af65e464b2343b70d7aa96f3c
    """

    lyric_url = f"{CHART_LYRICS_API_GETLYRIC_URL}?lyricId={lyric_id}&lyricCheckSum={checksum}"
    response = requests.get(lyric_url)

    # check HTTP result code
    if response.status_code != 200:
        logging.error(
            f"HTTP error {response.status_code} from Chart Lyrics API [GetLyric]")
        return None

    # parse lyric text from the response
    response_dict = xmltodict.parse(response.content, process_namespaces=False)

    # pprint(response_dict) # response_dict["GetLyricResult"]["Lyric"]
    # pprint(response_dict["GetLyricResult"]["Lyric"])

    lyrics = response_dict.get("GetLyricResult").get("Lyric")

    if lyrics:
        return lyrics
    else:
        return None


def fix_name(name):
    """ Strip/replace extra chars before making Genius URL """
    return name.replace(' ', '-')


# def fix_line_breaks(lyric):
#     """ Convert \r\n to html br"""
#     lyric = lyric.replace('"','')
#     return lyric.replace('\r\n','<br />')
