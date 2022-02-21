import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote, quote_plus
from urllib.request import urlopen
import lxml.html
from lxml import etree
import json
import time

songData = pd.read_csv(r'Data\spotifyData.csv')

songData['lyrics'] = None
notFound = []
geniusLyrics = []
#geniusFilter = '$'

findLyrics = etree.XPath("//div[@data-lyrics-container='true']/text()|//div[@data-lyrics-container='true']/a/span/text()")
#findLyrics = etree.XPath("//div[@id='song_body-lyrics']/div/text()")

#toRemove = ("[Intro]", "[Interlude]", "[Outro]")
toRemove = (' - Bonus Track', ' Bonus')

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

    if len(lyricsJson['response']['sections'][0]['hits']) == 0:
        print(artist + ' ' + track)
        notFound = notFound.append(str(artist + ' ' + track))
        continue

    path = lyricsJson['response']['sections'][0]['hits'][0]['result']['path']

    r = requests.get('https://genius.com'+ path)
    html = etree.HTML(r.text)

    geniusLyrics = findLyrics(html)

    songData.loc[i, 'lyrics'] = ' '.join(geniusLyrics)

    #to avoid hitting any traffic limits
    #time.sleep(.1)

songData.to_csv(r'Data\songLyricData.csv', index = False)

# for i in range(10):
# #for i in range(len(songData)):
#     artist = songData.loc[i,'artistName']
#     track = songData.loc[i, 'trackName']
#     searchQuery = str(artist) + '-' + str(track) + '-lyrics'
#     searchQuery = searchQuery.replace(' ', '-'); searchQuery = searchQuery.replace('$', '').replace('#', '').replace('.', '').replace(',', '')
#     #searchQuery = searchQuery.lower()
#     print(searchQuery)

#     r = requests.get('https://genius.com/'+ searchQuery)
#     html = etree.HTML(r.text)

#     lyrics = findLyrics(html)
#     print(lyrics)

    #page = requests.get('https://genius.com/'+ searchQuery)
    #html = BeautifulSoup(page.text)

    #lyrics1 = html.find("div", class_='Lyrics').get_text()
    # lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")

    # if lyrics1:
    #     lyrics = lyrics1.get_text()
    # elif lyrics2:
    #     lyrics = lyrics2.get_text()
    # elif lyrics1 == lyrics2 == None:
    #     print(str(searchQuery) + ": returned no lyrics.")
    #     lyrics = None
    #     notFound = notFound.append(str(searchQuery))
 