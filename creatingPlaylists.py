# import libraries
import pandas as pd
import json,os

#handling spotify data from JSON format
#f = open('my_spotify_data\MyData\Playlist1.json')
#data = json.load(f)
#print(data)
#f.close()

# files were retrieved through Spotify, Spotify will provide private data through request
# load in the desired data
#follow = pd.read_json('my_spotify_data\MyData\Follow.json', typ='series')
#identifiers = pd.read_json('my_spotify_data\MyData\Identifiers.json', typ='series')
#identity = pd.read_json('my_spotify_data\MyData\Identity.json', typ='series')
#inferences = pd.read_json('my_spotify_data\MyData\Inferences.json', typ='series')
#payments = pd.read_json('my_spotify_data\MyData\Payments.json', typ='series')
#playlist1 = pd.read_json('my_spotify_data\MyData\Playlist1.json', typ='series')
#searchqueries = pd.read_json('my_spotify_data\MyData\SearchQueries.json', typ='series')
streamingHistory0 = pd.read_json('my_spotify_data\MyData\StreamingHistory0.json', typ='series')
streamingHistory1 = pd.read_json('my_spotify_data\MyData\StreamingHistory1.json', typ='series')
streamingHistory2 = pd.read_json('my_spotify_data\MyData\StreamingHistory2.json', typ='series')
streamingHistory3 = pd.read_json('my_spotify_data\MyData\StreamingHistory3.json', typ='series')
#userData = pd.read_json('my_spotify_data\MyData\Userdata.json', typ='series')
#myLibrary = pd.read_json('my_spotify_data\MyData\YourLibrary.json', typ='series')

#streamingHistory0 = streamingHistory0.to_frame('count')

# load in data
streamingHistory0 = pd.DataFrame.from_records(streamingHistory0)
streamingHistory1 = pd.DataFrame.from_records(streamingHistory1)
streamingHistory2 = pd.DataFrame.from_records(streamingHistory2)
streamingHistory3 = pd.DataFrame.from_records(streamingHistory3)

# append dataframes together
masterHistory = streamingHistory0.append([streamingHistory1, streamingHistory2, streamingHistory3], ignore_index=False)
print(masterHistory.shape)
#df = df1.append([df2, df3])

# save to CSV
masterHistory.to_csv('Data\streamingHistory.csv', index = False)