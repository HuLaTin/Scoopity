import pandas as pd
#from bs4 import BeautifulSoup
import requests, json
from urllib.parse import quote_plus
#from urllib.request import urlopen
#import lxml.html
#import time
import os
from lxml import etree

songData = pd.read_csv(r'Data\featureData.csv')
songData = songData[['artistName','trackName']]

songData['tags'] = None #create new column for tags/genres
songData['lyrics'] = None #create new column for lyrics
songData['geniusArtist'] = None

notFound = [] #empty list for songs that aren't found

#finding 'data-lyrics-container='true'' and the text contained within
findLyrics = etree.XPath("//div[@data-lyrics-container='true']/text()|//div[@data-lyrics-container='true']/a/span/text()")
findTags = etree.XPath("//a[starts-with(@class, 'SongTags')]/text()")
# this path may not be great
#findArtist = etree.XPath("//a/text()")
#findTrack = None

# Use toRemove list to filter out 'problem' words, Genius titles don't always mirror Spotify.
toRemove = (' - Bonus Track', ' Bonus', ' (Demo)', ' (Acoustic)', ' - Remastered', ' - Original Mix', '- Live', ' Live', ' - Demo Version',' - Demo', ' - Single Version', ' - Single')

for i in range(25):
#for i in range(len(songData)):
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
        #songData.loc[i, 'lyrics'] = None
        continue
    
    if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path') :
        #path = lyricsJson['response']['sections'][0]['hits'][0]['result']['path']

        r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
        html = etree.HTML(r.text)

        if 'Non-Music' in findTags(html) or 'Literature' in findTags(html):
            print(artist + ' ' + track + ' ' + str(findTags(html)))
            #songData.loc[i, 'lyrics'] = None
            songData.loc[i, 'tags'] = ', '.join(findTags(html))
            continue
        
        #geniusLyrics = findLyrics(html)
        songData.loc[i, 'geniusArtist'] = str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names'])

        songData.loc[i, 'lyrics'] = ' '.join(findLyrics(html))
        songData.loc[i, 'tags'] = ', '.join(findTags(html))
    else:
        print(artist + ' ' + track + ': *** No Path ***')
        notFound.append(str(artist + ' ' + track))
        #songData.loc[i, 'lyrics'] = None

    #to avoid hitting any traffic limits
    #time.sleep(.1)

songData.to_csv(r'Data\lyricData.csv', index = False)
pd.DataFrame(notFound).to_csv(r'Data\unfound.csv', index = False)

### Notes ###
# 'Maple Syrup' to 'Maple $yrup'
# 'Pontiac Sunfire' to 'Pontiac $unfire'
# 'Bags' to 'Bag$'
# '100 Blunts' to '100 Blunt$'
# 'Grey Boys' to 'Grey Boy$'
# 'Lemon Slime' to 'Lemon $lime'
# 'Saturn Sunrise' to '$aturn $unrise'

# wrong lyrics
# Abandoned Toys 'The Witch's Gardern (prelude)'
# Ark Patrol 'Pleasantries'
# Ark Patrol 'Sorrow Doesnt Ressurect'