# import required libraries
import pandas as pd
import spotipy, myKeys
from spotipy.oauth2 import SpotifyClientCredentials
import requests, json
from urllib.parse import quote_plus
from lxml import etree
import util

# set Client ID and Secret
cid = myKeys.clientID
secret = myKeys.secret

# spotipy credentials manager
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# load streaming history
streamingHistory = pd.read_csv(r'Data\streamingHistory.csv')

# get unique songs and the number of listens
uniqueSongCount = streamingHistory.groupby(["artistName", "trackName"],as_index=False).size()
uniqueSongCount = uniqueSongCount.rename(columns={'size': 'count'})

# create copy for lyric data
trackLyrics = uniqueSongCount.copy(deep=True)
trackLyrics = trackLyrics.drop(columns=['count']); trackLyrics['lyrics'] = None; trackLyrics['tags'] = None; trackLyrics['geniusArtist'] = None

# get unique artist
uniqueArtist = pd.DataFrame(streamingHistory.artistName.unique())
uniqueArtist['id'] = None; uniqueArtist['genres'] = None # create new columns
uniqueArtist = uniqueArtist.rename(columns={0: 'artistName'})

# set list of desired spotify features (check documentation for full list)
spotifyFeatures = ('danceability','energy', 'key', 'loudness','mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                'valence', 'tempo', 'duration_ms', 'time_signature')

uniqueSongCount['id'] = None
for i in spotifyFeatures:
    uniqueSongCount[i] = None

# retrieve genre from spotify
print('Retrieving genre data from Spotify')
#for i in range(5):
for i in range(len(uniqueArtist)):
    artist = uniqueArtist.loc[i, 'artistName']

    # call getGenre, get spotify id and genres
    dictArt = util.getGenre(sp, artist)

    uniqueArtist.loc[i, 'id'] = dictArt['id']
    uniqueArtist.loc[i, 'genres'] = dictArt['genres']

print('Genre data collected')
uniqueArtist.to_csv(r'Data\genreData.csv', index = False)

# collect Spotify features for specific tracks
print('Retrieving track features from Spotify')
#for i in range(5):
for i in range(len(uniqueSongCount)):
    artist = uniqueSongCount.loc[i, 'artistName']
    track = uniqueSongCount.loc[i, 'trackName']

    dictFeat = util.getFeatures(sp, artist, track, spotifyFeatures)

    for j in dictFeat:
        #print(j)
        uniqueSongCount.loc[i,j] = dictFeat[j]

print('Feature data collected')
uniqueSongCount.to_csv(r'Data\featureData.csv', index = False)

# collect lyrics for tracks by scraping Genius

# path for containers that hold lyrics as text on Genius' website
lyricPath = etree.XPath("//div[@data-lyrics-container='true']/text()|//div[@data-lyrics-container='true']/a/span/text()")
tagPath = etree.XPath("//a[starts-with(@class, 'SongTags')]/text()")

# Use toRemove list to filter out 'problem' words, Genius titles don't always mirror Spotify.
# trial and error
toRemove = (' - Bonus Track', ' Bonus', ' (Demo)', ' (Acoustic)', ' - Remastered', ' - Original Mix', '- Live', ' Live', ' - Demo Version',' - Demo', ' - Single Version', ' - Single', ' - Radio Edit')

print("Collecting Lyrics from Genius")
#for i in range(200):
for i in range(len(trackLyrics)):
    artist = trackLyrics.loc[i,'artistName']
    track = trackLyrics.loc[i, 'trackName']

    for j in toRemove:
        if j in track:
            track = track.replace(j, '')

    lyrics, tags, artist = util.getLyrics(artist, track, lyricPath, tagPath, requests, quote_plus, json, etree)
    trackLyrics.loc[i,'lyrics'] = lyrics
    trackLyrics.loc[i, 'tags'] = tags
    trackLyrics.loc[i, 'geniusArtist '] = artist
    #print(lyrics)

print('Lyric data collected')
trackLyrics.to_csv(r'Data\lyricData.csv', index = False)