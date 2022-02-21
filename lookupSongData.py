import pandas as pd
import spotipy, myKeys
from spotipy.oauth2 import SpotifyClientCredentials
#from urllib.parse import quote

streamingHistory = pd.read_csv('Data\streamingHistory.csv')
#streamingHistory.columns

#uniqueSongs = streamingHistory.sort_values('artistName').drop_duplicates('trackName', keep='last')
#uniqueSongs = uniqueSongs[['artistName', 'trackName']].reset_index(drop=True)
#uniqueSongs.shape
uniqueSongCount = streamingHistory.groupby(["artistName", "trackName"],as_index=False).size()

#uniqueSongs = pd.DataFrame(streamingHistory.groupby('trackName'))
#uniqueSongs = pd.DataFrame(streamingHistory.trackName.unique())

#uniqueSongs['artistName'] = ""
#uniqueSongs = uniqueSongs.rename(columns={0: 'trackName'})
uniqueSongCount = uniqueSongCount.rename(columns={'size': 'count'})

#set Client ID and Secret
cid = myKeys.clientID
secret = myKeys.secret

#spotipy credentials manager
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#features that we decided to gather
#spotify only allows you to gather genre by artist, not each song
spotifyFeatures = ('danceability','energy', 'key', 'loudness','mode', 'speechiness','acousticness', 'instrumentalness', 'liveness',
                'valence', 'tempo', 'duration_ms', 'time_signature')

uniqueSongCount['id'] = ''
for i in spotifyFeatures:
    uniqueSongCount[i] = ''

#for i in range(1):
for i in range(len(uniqueSongCount)):
    artist = uniqueSongCount.loc[i,'trackName']
    track = uniqueSongCount.loc[i, 'artistName']

    searchQuery = track + ' ' + artist
    #print(searchQuery)
    searchResults = sp.search(q=searchQuery, limit = 1)

    #print(searchResults)

    #if nothing is returned in the search query
    if len(searchResults['tracks']['items']) == 0:
        uniqueSongCount.loc[i,'id':] = None
        print(searchQuery + ': *** No longer on Spotify ***')
        continue
    else:
        uniqueSongCount.loc[i, 'id'] = searchResults['tracks']['items'][0]['id']
        features = sp.audio_features(str(searchResults['tracks']['items'][0]['id']))[0]

        #if features dont exist
        if features is None:
            print(searchQuery + ': *** No features ***')
            for j in spotifyFeatures:
                uniqueSongCount.loc[i,j] = None
        else:
            for j in spotifyFeatures:
                uniqueSongCount.loc[i,j] = features[j]

    
uniqueSongCount.to_csv(r'Data\spotifyData.csv', index = False)