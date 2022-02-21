import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
from urllib.request import urlopen
import lxml.html
from lxml import etree


songData = pd.read_csv(r'Data\spotifyData.csv')

songData['lyrics'] = None
notFound = []
#geniusFilter = '$'

findLyrics = etree.XPath("//div[@data-lyrics-container='true']/text()|//div[@data-lyrics-container='true']/a/span/text()")
#findLyrics = etree.XPath("//div[@id='song_body-lyrics']/div/text()")

for i in range(10):
#for i in range(len(songData)):
    artist = songData.loc[i,'artistName']
    track = songData.loc[i, 'trackName']
    searchQuery = str(artist) + '-' + str(track) + '-lyrics'
    searchQuery = searchQuery.replace(' ', '-'); searchQuery = searchQuery.replace('$', '').replace('#', '').replace('.', '').replace(',', '')
    #searchQuery = searchQuery.lower()
    print(searchQuery)

    r = requests.get('https://genius.com/'+ searchQuery)
    html = etree.HTML(r.text)

    lyrics = findLyrics(html)
    print(lyrics)

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
 