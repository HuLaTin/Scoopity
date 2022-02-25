import pandas as pd
#from bs4 import BeautifulSoup
import requests, json, time
from urllib.parse import quote_plus
#from urllib.request import urlopen
#import lxml.html
#import time
#import os
from lxml import etree
from fuzzywuzzy import fuzz
import re

songData = pd.read_csv(r'Data\featureData.csv')
songData = songData[['artistName','trackName']]

songData['tags'] = None # create new column for tags/genres
songData['lyrics'] = None # create new column for lyrics
songData['geniusArtist'] = None # column for artist field returned from genius

notFound = [] # empty list for songs that aren't found

# finding 'data-lyrics-container='true'' and the text contained within
findLyrics = etree.XPath("//div[@data-lyrics-container='true']/text()|//div[@data-lyrics-container='true']/a/span/text()")
findTags = etree.XPath("//a[starts-with(@class, 'SongTags')]/text()")

# regex pattern to remove version/remix substrings while searching
trackPattern = r'\(.*?\)|\-.*?$'

#for i in range(2):
for i in range(len(songData)):
    artist = songData.loc[i,'artistName']
    track = songData.loc[i, 'trackName']

    # search genius for artist + track
    r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
    lyricsJson = json.loads(r.text)

    #if status != 200 then wait ??
    if lyricsJson['meta']['status'] != 200:
        while True:
            time.sleep(60)

            r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
            lyricsJson = json.loads(r.text)

            if lyricsJson['meta']['status'] == 200:
                break

    # if nothing is found print to screen and append to list
    if len(lyricsJson['response']['sections'][0]['hits']) == 0:
        #continue
        track = re.sub(trackPattern, '', track).strip()
        #print(track)
        time.sleep(2)

        r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
        lyricsJson = json.loads(r.text)

        if len(lyricsJson['response']['sections'][0]['hits']) == 0:
            print(artist + ' ' + track, ': *** Not Found ***')
            notFound.append(str(artist + ' ' + track))
            continue
   
    # if a path exists, request page and scrape data
    if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path'):

        time.sleep(2)

        r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
        
        html = etree.HTML(r.text)

        fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']).upper())

        if fuzzMatch < 80:
            track = re.sub(trackPattern, '', track).strip()

            time.sleep(2)

            r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
            lyricsJson = json.loads(r.text)
            r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
            html = etree.HTML(r.text)

            fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']).upper())

            if fuzzMatch < 80:
                print(artist + ' ' + track, ': *** Not Found ***')
                notFound.append(str(artist + ' ' + track))
                continue

        # if the page/song is tagged as 'Non-Music' print to screen and break to next iteration
        # some music is incorrectly tagged, and some searches find the wrong results
        if 'Non-Music' in findTags(html) or 'Literature' in findTags(html):

            fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']).upper())

            if fuzzMatch < 80:
                track = re.sub(trackPattern, '', track).strip()

                time.sleep(2)

                r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
                lyricsJson = json.loads(r.text)
                r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
                html = etree.HTML(r.text)

                if 'Non-Music' in findTags(html) or 'Literature' in findTags(html):
                    print(artist + ' ' + track + ' ' + str(findTags(html)))
                    songData.loc[i, 'tags'] = ', '.join(findTags(html))
                    #continue
        
        # store artist name to confirm if lyrics are correct
        songData.loc[i, 'geniusArtist'] = str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']) # with fuzz.partial_ratio this may not be needed anymore

        # store lyrics and tags
        songData.loc[i, 'lyrics'] = ' '.join(findLyrics(html))
        songData.loc[i, 'tags'] = ', '.join(findTags(html))
    else:
        print(artist + ' ' + track + ': *** No Path ***')
        notFound.append(str(artist + ' ' + track))

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