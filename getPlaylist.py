import Data.Input.myKeys as myKeys
import util, json
import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# set Client ID and Secret
cid = myKeys.clientID
secret = myKeys.secret

# spotipy credentials manager
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

username = myKeys.userName # username of playlist's user (numeric in this case)
playlist_id = myKeys.playlistId # playlist id (can be pulled from playlist url)

results = sp.user_playlist_tracks(username,playlist_id)['tracks'] # returns json object


tracks = results['items']
while results['next']:
    results = sp.next(results) # next if paginated results
    tracks.extend(results['items']) # extend list

playlistSongs = pd.DataFrame() # create empty dataframe
playlistSongs['artistName'] = None;playlistSongs['trackName'] = None

for i in range(len(tracks)):
    song = tracks[i]
    playlistSongs.loc[i, 'artistName'] = str(song['track']['artists'][0]['name']) # select artist name
    playlistSongs.loc[i, 'trackName'] = str(song['track']['name']) # select track name

playlistSongs.to_csv(r'Data\Input\retrievedPlaylist.csv', index=False) # save to csv