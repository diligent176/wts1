import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="9dcdc500adbd4425b3c37fdcc0945bd8",
                                               client_secret="7d299bf748e64bcfb8191cae79c36164",
                                               redirect_uri="http://localhost:8888",
                                               scope="user-library-read"))

# LIKED SONGS list
results = sp.current_user_saved_tracks()

for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])

# TAYLORS ALBUMS
taylor_uri = 'spotify:artist:06HL4z0CvFAxyc27GXpf02'

results = sp.artist_albums(taylor_uri, album_type='album')
albums = results['items']
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

for album in albums:
    print(album['name'])
