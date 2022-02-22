import pandas as pd
#from bs4 import BeautifulSoup
import requests, json
from urllib.parse import quote_plus
#from urllib.request import urlopen
#import lxml.html
#import time
import os
from lxml import etree

songData = pd.read_csv(r'Data\spotifyData.csv')

if os.path.exists(r'Data\songLyricData.csv'):
    print('Lyric data already exists')

songData['lyrics'] = None #create new column
notFound = [] #empty list for songs that aren't found
#geniusLyrics = []
#geniusFilter = '$'

#finding 'data-lyrics-container='true'' and the text contained within
findLyrics = etree.XPath("//div[@data-lyrics-container='true']/text()|//div[@data-lyrics-container='true']/a/span/text()")

# Use toRemove list to filter out 'problem' words, Genius titles don't always mirror Spotify.
toRemove = (' - Bonus Track', ' Bonus', ' (Demo)')

#for i in range(1):
for i in range(len(songData)):
    artist = songData.loc[i,'artistName']
    track = songData.loc[i, 'trackName']

    for j in toRemove:
        if j in track:
            track = track.replace(j, '')
            #print(track)

    r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
    lyricsJson = json.loads(r.text)

    #if status != 200 then wait
    if len(lyricsJson['response']['sections'][0]['hits']) == 0:
        #print('Status' + str(lyricsJson['response']) +':: ' + artist + ' ' + track, ': *** Not Found ***')
        print(artist + ' ' + track, ': *** Not Found ***')
        notFound.append(str(artist + ' ' + track))
        songData.loc[i, 'lyrics'] = None
        continue
    
    if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path') :
        path = lyricsJson['response']['sections'][0]['hits'][0]['result']['path']

        r = requests.get('https://genius.com'+ path)
        html = etree.HTML(r.text)

        geniusLyrics = findLyrics(html)

        songData.loc[i, 'lyrics'] = ' '.join(geniusLyrics)
    else:
        print(artist + ' ' + track + ': *** No Path ***')
        notFound.append(str(artist + ' ' + track))
        songData.loc[i, 'lyrics'] = None

    #to avoid hitting any traffic limits
    #time.sleep(.1)

songData.to_csv(r'Data\songLyricData.csv', index = False)
pd.DataFrame(notFound).to_csv(r'Data\unfound.csv', index = False)

### Notes ###
# 'Maple Syrup' to 'Maple $yrup'
# 'Pontiac Sunfire' to 'Pontiac $unfire'