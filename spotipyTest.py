import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import myKeys

print(myKeys.appName)

cid = myKeys.clientID
secret = myKeys.secret

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#create empty lists to store the results
artist_name = []
track_name = []
popularity = []
track_id = []

#search for 2022 songs
for i in range(0, 1000, 50):
    track_results = sp.search(q = 'year:2022', type = 'track', limit = 50, offset=i)
    for i, t in enumerate(track_results['tracks']['items']):
        artist_name.append(t['artists'][0]['name'])
        track_name.append(t['name'])
        track_id.append(t['id'])
        popularity.append(t['popularity'])