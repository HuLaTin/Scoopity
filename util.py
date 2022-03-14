from platform import release
from bs4 import BeautifulSoup
import unidecode
import contractions
from nltk.stem import WordNetLemmatizer
from num2words import num2words
import requests, json, re
from urllib.parse import quote_plus
from lxml import etree
from fuzzywuzzy import fuzz
import time

# is this the right way?
wordnet_lemmatizer = WordNetLemmatizer()
def lemmatizer(text):
    lemm_text = [wordnet_lemmatizer.lemmatize(word) for word in text]
    return lemm_text

def convertNums(text):
    convNums = [num2words(word) for word in text if word.isdigit()]
    return convNums

def strip_html_tags(text):
    """remove html tags from text"""
    soup = BeautifulSoup(text, 'html.parser')
    stripped_text = soup.get_text(separator=" ")
    return stripped_text

def remove_accented_chars(text):
    """remove accented characters from text, e.g. café, unicode decode removes non utf-8 characters"""
    text = unidecode.unidecode(text)
    return text

def expand_contractions(text):
    """expand shortened words, e.g. don't = do not"""
    text = contractions.fix(text)
    return text

def getGenre(sp, artistName):
    searchResults = sp.search(q=artistName, type='artist', limit = 1)
    
    # if doesn't exist = None
    if len(searchResults['artists']['items']) == 0:
        dictArt = {'id':None, 'genres':None}

    # else enter desired fields into dataframe
    else:
        dictArt = {'id':searchResults['artists']['items'][0]['id'], 'genres':', '.join(searchResults['artists']['items'][0]['genres'])}
    return dictArt

def getFeatures(sp, artistName, trackName, spotifyFeatures):
    searchResults = sp.search(q=artistName + ' ' + trackName, limit = 1)

    if len(searchResults['tracks']['items']) == 0:
        dictFeat = {'id': None }
    else:
        dictFeat = {'id':searchResults['tracks']['items'][0]['id']}
        features = sp.audio_features(str(searchResults['tracks']['items'][0]['id']))[0]

        #if features dont exist
        if features is None:
            for j in spotifyFeatures:
                dictFeat[j] = None
        else:
            for j in spotifyFeatures:
                dictFeat[j] = features[j]

    return dictFeat


findLyrics = etree.XPath("//div[@data-lyrics-container='true']/text()|//div[@data-lyrics-container='true']/a/span/text()")
findReleaseDate = etree.XPath("//div[starts-with(@class, 'HeaderMetadata')]/text()")
findTags = etree.XPath("//a[starts-with(@class, 'SongTags')]/text()")
trackPattern = r'\(.*?\)|\-.*?$'
def getLyrics(artist, track):
    tags = None;lyrics = None;geniusArtist=None;releaseDate=None;isFound=False
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
            isFound = False
            return
   
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
        fuzzMatch = fuzz.partial_ratio(artist.upper(), foundArtist.upper())

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

                    fuzzMatch = fuzz.partial_ratio(artist.upper(), foundArtist.upper())

                    if fuzzMatch <= 70:
                        print(artist + ' ' + foundArtist, ': Bad Match')
                        isFound = False
                
                else:
                    print(artist + ' ' + track + ': No Path')
                    isFound = False

            else:
                print(artist + ' ' + track + ': No hits')
                isFound = False

        # if the page/song is tagged as 'Non-Music' print to screen and break to next iteration
        # some music is incorrectly tagged, and some searches find the wrong results
        if 'Non-Music' in findTags(html) or 'Literature' in findTags(html):

            fuzzMatch = fuzz.partial_ratio(artist.upper(), foundArtist)

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
                            tags = ', '.join(findTags(html))
                            return

                    else:
                        print(artist + ' ' + track + ': No Path')
                        isFound = False

                else:
                    print(artist + ' ' + track, ': No Hits')
                    isFound = False
                    

        # store artist name to confirm if lyrics are correct
        geniusArtist = foundArtist

        # if value is passed, returns True
        # json.dumps() allows us to store object as a string in this dataframe
        # use json.loads() to load it back as an object
        if bool(findLyrics(html)):
            lyrics = json.dumps(findLyrics(html))
            isFound = True
        else:
            isFound = False
            
        if bool(findTags(html)):
            tags = json.dumps(findTags(html))
        else:
            pass

        if bool(findReleaseDate(html)):
            releaseDate = max(findReleaseDate(html))

        else:
            pass
    
    else:
        print(artist + ' ' + track + ': No Path')
        isFound = False
    
    lyricsDict = {'tags': tags, 'lyrics': lyrics, 'geniusArtist':geniusArtist, 'releaseDate':releaseDate, 'isFound': isFound}
    return lyricsDict
