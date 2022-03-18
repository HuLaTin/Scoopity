# import libraries
import pandas as pd
import spotipy, Data.Input.myKeys as myKeys
from spotipy.oauth2 import SpotifyClientCredentials

# load in data
streamingHistory = pd.read_csv(r'Data\Input\streamingHistory.csv')

# get unique entries for artist column
uniqueArtist = pd.DataFrame(streamingHistory.artistName.unique())

# create new columns to hold data
uniqueArtist['id'] = None
uniqueArtist['genres'] = None

# rename column
uniqueArtist = uniqueArtist.rename(columns={0: 'artistName'})

# keys to spotify api
cid = myKeys.clientID
secret = myKeys.secret

#spotipy credentials manager
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
genreList = []

# for each row in dataframe select artist
#for i in range(5):
for i in range(len(uniqueArtist)):
    artist = uniqueArtist.loc[i, 'artistName']
    #print(searchQuery)
    searchResults = sp.search(q=artist, type='artist', limit = 1)
    
    # if doesn't exist = None
    if len(searchResults['artists']['items']) == 0:
        uniqueArtist.loc[i,'id':] = None
        uniqueArtist.loc[i,'genres'] = None
        print(artist + ': *** Not found on Spotify ***')
        continue
    # else enter desired fields into dataframe
    else:
        uniqueArtist.loc[i, 'id'] = searchResults['artists']['items'][0]['id']
        genreList.extend(searchResults['artists']['items'][0]['genres'])
        uniqueArtist.loc[i, 'genres'] = searchResults['artists']['items'][0]['genres']

genreList = list(set(genreList))
uniqueArtist = uniqueArtist.explode('genres') # explode lists, (similar to melt?)
uniqueArtist.to_csv(r'Data\artistData.csv', index = False)# save to CSV