#from numpy import True_
from operator import le
import pandas as pd
import requests, json, time, re
from urllib.parse import quote_plus
from lxml import etree
from fuzzywuzzy import fuzz
from torch import t
from util import remove_accented_chars


songData = pd.read_csv(r'Data\featureData.csv')
songData = songData[['artistName','trackName']]

songData['tags'] = None # create new column for tags/genres
songData['lyrics'] = None # create new column for lyrics
songData['geniusArtist'] = None # column for artist field returned from Genius
songData['releaseDate'] = None # column for release date scraped from Genius
songData['isFound'] = None # column stores bool variable if found or not

# navigate xml documents, these paths navigate to the desired data
findLyrics = etree.XPath("//div[@data-lyrics-container='true']/text()|//div[@data-lyrics-container='true']/a/span/text()")
findReleaseDate = etree.XPath("//div[starts-with(@class, 'HeaderMetadata')]/text()")
findTags = etree.XPath("//a[starts-with(@class, 'SongTags')]/text()")

# regex pattern to remove version/remix substrings while searching
trackPattern = r'\(.*?\)|\-.*?$'

#for i in range(25):
for i in range(len(songData)):
    artist = songData.loc[i,'artistName']
    track = songData.loc[i, 'trackName']

    # search genius for artist + track
    r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
    
    # this if statement checks status of request
    if r.status_code != 200:
        while True:
            print(str(r))
            time.sleep(15)
            r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
            if r.status_code == 200:
                break

    lyricsJson = json.loads(r.text)
    
    # if nothing is found print to screen and append to list
    if bool(lyricsJson['response']['sections'][0]['hits']) == False:
        #continue
        track = re.sub(trackPattern, '', track).strip()
        #print(track)
        #time.sleep(.5)

        r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))

        if r.status_code != 200:
            while True:
                print(str(r))
                time.sleep(15)
                r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
                if r.status_code == 200:
                    break

        lyricsJson = json.loads(r.text)

        if bool(lyricsJson['response']['sections'][0]['hits']) == False:
            print(artist + ' ' + track, ': No Hits')
            songData.loc[i,'isFound'] = False
            continue
   
    # if a path exists, request page and scrape data
    if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path'):

        r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])

        if r.status_code != 200:
            while True:
                print(str(r))
                time.sleep(15)
                r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
                if r.status_code == 200:
                    break

        html = etree.HTML(r.text)

        if bool(lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('artist_names')):
            foundArtist = remove_accented_chars(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']).strip()
        else:
            foundArtist = None

        #calculates levenshtein similarity ratio with fuzzy string matching
        fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), foundArtist.upper())

        if fuzzMatch <= 70:
            # use regex to remove selected portions of string
            track = re.sub(trackPattern, '', track).strip()

            r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))

            if r.status_code != 200:
                while True:
                    print(str(r))
                    time.sleep(15)
                    r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
                    if r.status_code == 200:
                        break

            lyricsJson = json.loads(r.text)

            if bool(lyricsJson['response']['sections'][0]['hits']) != False:

                if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path'):

                    r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])

                    if r.status_code != 200:
                        while True:
                            print(str(r))
                            time.sleep(15)
                            r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
                            if r.status_code == 200:
                                break
                
                    html = etree.HTML(r.text)

                    if bool(lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('artist_names')):
                        foundArtist = remove_accented_chars(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']).strip()
                    else:
                        foundArtist = None

                    fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), foundArtist.upper())

                    if fuzzMatch <= 70:
                        print(artist + ' ' + foundArtist, ': Bad Match')
                        songData.loc[i,'isFound'] = False
                        continue
                
                else:
                    print(artist + ' ' + track + ': No Path')
                    songData.loc[i,'isFound'] = False

            else:
                print(artist + ' ' + track + ': No hits')
                songData.loc[i, 'isFound'] = False

        # if the page/song is tagged as 'Non-Music' print to screen and break to next iteration
        # some music is incorrectly tagged, and some searches find the wrong results
        if 'Non-Music' in findTags(html) or 'Literature' in findTags(html):

            fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), foundArtist)

            if fuzzMatch <= 70:
                track = re.sub(trackPattern, '', track).strip()

                r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))

                if r.status_code != 200:
                    while True:
                        print(str(r))
                        time.sleep(15)
                        r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artist + ' ' + track))
                        if r.status_code == 200:
                            break

                lyricsJson = json.loads(r.text)

                if bool(lyricsJson['response']['sections'][0]['hits']) == True:

                    if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path'):
                    
                        r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])

                        if r.status_code != 200:
                            while True:
                                print(str(r))
                                time.sleep(15)
                                r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
                                if r.status_code == 200:
                                    break

                        html = etree.HTML(r.text)

                        if 'Non-Music' in findTags(html) or 'Literature' in findTags(html):
                            print(artist + ' ' + track + ' ' + str(findTags(html)))
                            songData.loc[i, 'tags'] = ', '.join(findTags(html))
                            #continue

                    else:
                        print(artist + ' ' + track + ': No Path')
                        songData.loc[i,'isFound'] = False

                else:
                    print(artist + ' ' + track, ': No Hits')
                    songData.loc[i,'isFound'] = False
                    continue

        # store artist name to confirm if lyrics are correct
        songData.loc[i, 'geniusArtist'] = foundArtist

        # if value is passed, returns True
        # json.dumps() allows us to store object as a string in this dataframe
        # use json.loads() to load it back as an object
        if bool(findLyrics(html)):
            songData.loc[i,'lyrics'] = json.dumps(findLyrics(html))
            songData.loc[i,'isFound'] = True
        else:
            songData.loc[i,'isFound'] = False
            pass

        if bool(findTags(html)):
            songData.loc[i,'tags'] = json.dumps(findTags(html))
        else:
            pass

        if bool(findReleaseDate(html)):
            songData.loc[i,'releaseDate'] = max(findReleaseDate(html))

        else:
            pass
    
    else:
        print(artist + ' ' + track + ': No Path')
        songData.loc[i,'isFound'] = False


#############
# I think im misunderstanding my data types
# goal is to 'explode' column for use in data analysis

trackTags = songData[['artistName', 'trackName', 'tags']].copy()
trackTags = trackTags.dropna()
trackTags['uniqueTags'] = None # new column, empty
trackTags = trackTags.reset_index(drop=True) # reset column, drop original

for i in range(len(trackTags)):
    tags = trackTags.loc[i, 'tags']
    tags = tags.strip('][').split(', ') # split string and remove brackets
    trackTags.at[i, 'uniqueTags'] = tags

trackTags.drop(columns = 'tags', inplace=True) # drop column
trackTags = trackTags.explode('uniqueTags') # explode on 'uniqueTags' column
trackTags = trackTags.reset_index(drop=True) # reset index and drop original column

for i in range(len(trackTags)):
    tags = trackTags.loc[i, 'uniqueTags']
    trackTags.loc[i, 'uniqueTags'] = tags.replace('"', "") # remove double quotes

#############

songData.to_csv(r'Data\lyricData.csv', index = False)
#songData.to_csv(r'Data\testing.csv', index = False)
trackTags.to_csv(r'Data\trackTags.csv', index = False)
