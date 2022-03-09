from bs4 import BeautifulSoup
import unidecode
import contractions
#import re
from nltk.stem import WordNetLemmatizer

# is this the right way?
wordnet_lemmatizer = WordNetLemmatizer()
def lemmatizer(text):
    lemm_text = [wordnet_lemmatizer.lemmatize(word) for word in text]
    return lemm_text

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
    """expand shortened words, e.g. don't to do not"""
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

def getLyrics(artistName, trackName, lyricPath, tagPath,  requests, quote_plus, json, etree):

    r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artistName + ' ' + trackName))
    lyricsJson = json.loads(r.text)

    #if status != 200 then wait
    if len(lyricsJson['response']['sections'][0]['hits']) == 0:
        #print('Status' + str(lyricsJson['response']) +':: ' + artist + ' ' + track, ': *** Not Found ***')
        #print(artistName + ' ' + track, ': *** Not Found ***')
        #notFound.append(str(artist + ' ' + track))
        lyrics = None
        tags = None
        artist = None
        #continue
    else:
        if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path') :
            #path = lyricsJson['response']['sections'][0]['hits'][0]['result']['path']
            #r = requests.get('https://genius.com'+ path)

            r = requests.get('https://genius.com'+ lyricsJson['response']['sections'][0]['hits'][0]['result']['path'])

            html = etree.HTML(r.text)

            if 'Non-Music' in tagPath(html) or 'Literature' in tagPath(html):
                #print(artistName + ' ' + trackName + ' ' + str(tagPath(html)))
                #songData.loc[i, 'lyrics'] = None
                tags = ', '.join(tagPath(html))
                #continue

            #geniusLyrics = lyricPath(html)

            # may have to handle some characters here
            #lyrics = ' '.join(geniusLyrics)
            lyrics = ' '.join(lyricPath(html))
            tags = ', '.join(tagPath(html))
            artist = str(lyricsJson['response']['sections'][0]['hits'][0]['result']['artist_names'])
        else:
            #print(artist + ' ' + track + ': *** No Path ***')
            #notFound.append(str(artist + ' ' + track))
            lyrics = None
            tags = None
            artist = None
            
    return lyrics, tags, artist
