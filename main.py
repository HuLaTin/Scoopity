# import required libraries
import pandas as pd
import spotipy, Data.Input.myKeys as myKeys
from spotipy.oauth2 import SpotifyClientCredentials
import util

# set Client ID and Secret
cid = myKeys.clientID
secret = myKeys.secret

# spotipy credentials manager
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# load streaming history
streamingHistory = pd.read_csv(r'Data\Input\slowdancePlaylist.csv')

# get unique songs and the number of listens
uniqueSongCount = streamingHistory.groupby(["artistName", "trackName"],as_index=False).size()
uniqueSongCount = uniqueSongCount.rename(columns={'size': 'count'})

trackLyrics = uniqueSongCount.copy(deep=True) # create copy for lyric data
trackLyrics = trackLyrics[['artistName','trackName']]
trackLyrics['tags'] = None # create new column for tags/genres
trackLyrics['lyrics'] = None # create new column for lyrics
trackLyrics['geniusArtist'] = None # column for artist field returned from Genius
trackLyrics['releaseDate'] = None # column for release date scraped from Genius
trackLyrics['isFound'] = False # column stores bool variable if found or not

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

# retrieve genres from spotify
print('Retrieving genre data from Spotify')
for i in range(len(uniqueArtist)):
    artist = uniqueArtist.loc[i, 'artistName']
    dictArt = util.getGenre(sp, artist) # call getGenre, get spotify id and genres
    uniqueArtist.loc[i, 'id'] = dictArt['id']
    uniqueArtist.loc[i, 'genres'] = dictArt['genres']

print('Genre data collected')
uniqueArtist.to_csv(r'Data\main\genreData.csv', index = False)

# collect Spotify features for specific tracks
print('Retrieving track features from Spotify')
for i in range(len(uniqueSongCount)):
    artist = uniqueSongCount.loc[i, 'artistName']
    track = uniqueSongCount.loc[i, 'trackName']

    dictFeat = util.getFeatures(sp, artist, track, spotifyFeatures)

    for j in dictFeat:
        #print(j)
        uniqueSongCount.loc[i,j] = dictFeat[j]

print('Feature data collected')
uniqueSongCount.to_csv(r'Data\main\featureData.csv', index = False)

print("Collecting Lyrics from Genius")
for i in range(len(trackLyrics)):
    artist = trackLyrics.loc[i,'artistName']
    track = trackLyrics.loc[i, 'trackName']

    lyricsDict = util.getLyrics(artist, track)
    if bool(lyricsDict) == True:
        trackLyrics.loc[i, 'tags'] = lyricsDict['tags']
        trackLyrics.loc[i, 'lyrics'] = lyricsDict['lyrics']
        trackLyrics.loc[i, 'geniusArtist'] = lyricsDict['geniusArtist']
        trackLyrics.loc[i, 'releaseDate'] = lyricsDict['releaseDate']
        trackLyrics.loc[i, 'isFound'] = lyricsDict['isFound']
    
print('Lyric data collected')
trackLyrics.to_csv(r'Data\main\lyricData.csv', index = False)