# What's That Song !?!

My final project for Harvard's [CS50x - Intro to Computer Science](https://cs50.harvard.edu/x/2022/).


- VIDEO LINK TBD...


## Game Description

This game tests a player's lyric knowledge, with songs in their own Spotify library. Here's how it works:

1. A player logs in to the game via [Spotify's OAuth 2.0](https://developer.spotify.com/documentation/general/guides/authorization/) authorization framework
2. Their **Liked Songs** and **Playlists** are scanned for favorites
3. Each game round: a song is chosen **randomly**, and a section of lyrics shown
4. The player guesses which song it is (multiple choice)
5. Full lyrics are then revealed, and a mini-player to hear the song

![Main screen](static/screen01.png)

![Main screen](static/screen02.png)


### Technical achievements so far

- Authenticated players via Spotify [Authorization Code flow](https://developer.spotify.com/documentation/general/guides/authorization/code-flow/)
- Called several Spotify APIs to retrieve player details and song data
- A SQLite database holds player details, high scores, and transient track data (reduces repeated calls to Spotify)
- Song lyrics retrieved from [genius.com](https://genius.com/) and [Chartlyrics API](http://www.chartlyrics.com/api.aspx)
- Implemented helper libraries for spotify, database, and game play functions - such as selecting random songs and choosing random lyric snippets.
- Used some basic Bootstrap styling


### Future improvements

This is an early beta. The basic plumbing is there for gameplay, however:
- score keeping is not implemented
- the UI is very basic
- lyric accuracy not guaranteed, as they're from external sources (not Spotify)


### Program Structure

The program is a flask web application, written in Python with a touch of JavaScript:

| File                  | Description |
| --------------------- | ----------- |
| **app.py**            | the main flask app |
| **db_helper.py**      | sqlite database functions |
| **game_helper.py**    | gameplay functions e.g. get random songs and lyrics |
| **spotify_helper.py** | spotify API helpers |
