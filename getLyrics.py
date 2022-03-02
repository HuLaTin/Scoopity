import pandas as pd
import requests, json, time, re
from urllib.parse import quote_plus
from lxml import etree
from fuzzywuzzy import fuzz

songData = pd.read_csv(r'Data\featureData.csv')
songData = songData[['artistName','trackName']]

songData['tags'] = None # create new column for tags/genres
songData['lyrics'] = None # create new column for lyrics
songData['geniusArtist'] = None # column for artist field returned from Genius
songData['releaseDate'] = None # column for release date scraped from Genius

notFound = [] # empty list for songs that aren't found

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
    if len(lyricsJson['response']['sections'][0]['hits']) == 0:
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

        if len(lyricsJson['response']['sections'][0]['hits']) == 0:
            print(artist + ' ' + track, ': *** Not Found ***')
            notFound.append(str(artist + ' ' + track))
            continue
   
    # if a path exists, request page and scrape data
    if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path'):

        #time.sleep(.5)

        r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])

        if r.status_code != 200:
            while True:
                print(str(r))
                time.sleep(15)
                r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
                if r.status_code == 200:
                    break

        html = etree.HTML(r.text)

        #calculates levenshtein similarity ratio with fuzzy string matching
        fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']).upper())

        if fuzzMatch <= 70:
            # use regex to remove selected portions of string
            track = re.sub(trackPattern, '', track).strip()

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

            r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])

            if r.status_code != 200:
                while True:
                    print(str(r))
                    time.sleep(15)
                    r = requests.get('https://genius.com' + lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])
                    if r.status_code == 200:
                        break
            
            html = etree.HTML(r.text)

            fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']).upper())

            if fuzzMatch <= 70:
                print(artist + ' ' + track, ': *** Not Found ***')
                notFound.append(str(artist + ' ' + track))
                continue

        # if the page/song is tagged as 'Non-Music' print to screen and break to next iteration
        # some music is incorrectly tagged, and some searches find the wrong results
        if 'Non-Music' in findTags(html) or 'Literature' in findTags(html):

            fuzzMatch = fuzz.partial_ratio(songData.loc[i,'artistName'].upper(), str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names']).upper())

            if fuzzMatch <= 70:
                track = re.sub(trackPattern, '', track).strip()

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
        
        # store artist name to confirm if lyrics are correct
        songData.loc[i, 'geniusArtist'] = str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names'])

        # if value is passed, returns True
        # json.dumps() allows us to store object as a string in this dataframe
        # use json.loads() to load it back as an object
        if bool(findLyrics(html)):
            songData.loc[i,'lyrics'] = json.dumps(findLyrics(html))
        else:
            pass

        if bool(findTags(html)):
            songData.loc[i,'tags'] = json.dumps(findTags(html))
        else:
            pass

        if bool(findReleaseDate(html)):
            songData.loc[i,'releaseDate'] = json.dumps(findReleaseDate(html))
            #songData.loc[i,'releaseDate'] = max(findReleaseDate(html))

        else:
            pass
    
    else:
        print(artist + ' ' + track + ': *** No Path ***')
        notFound.append(str(artist + ' ' + track))

# for i in range(len(songData)):
#     date = songData.loc[i, 'releaseDate']
#     if bool(date):
#         date = json.loads(date)
#         songData.loc[i, 'releaseDate'] = max(date, key=len)
#     else:
#         pass

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