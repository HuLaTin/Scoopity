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

def getLyrics(artistName, trackName, lyricPath, requests, quote_plus, json, etree):

    r = requests.get('https://genius.com/api/search/multi?per_page=5&q='+ quote_plus(artistName + ' ' + trackName))
    lyricsJson = json.loads(r.text)

    #if status != 200 then wait
    if len(lyricsJson['response']['sections'][0]['hits']) == 0:
        #print('Status' + str(lyricsJson['response']) +':: ' + artist + ' ' + track, ': *** Not Found ***')
        #print(artistName + ' ' + track, ': *** Not Found ***')
        #notFound.append(str(artist + ' ' + track))
        lyrics = None
        #continue
    
    if lyricsJson['response']['sections'][0]['hits'][0]['result'].__contains__('path') :
        path = lyricsJson['response']['sections'][0]['hits'][0]['result']['path']

        r = requests.get('https://genius.com'+ path)
        html = etree.HTML(r.text)

        geniusLyrics = lyricPath(html)

        # may have to handle some characters here
        lyrics = ' '.join(geniusLyrics)
    else:
        #print(artist + ' ' + track + ': *** No Path ***')
        #notFound.append(str(artist + ' ' + track))
        lyrics = None

    return lyrics