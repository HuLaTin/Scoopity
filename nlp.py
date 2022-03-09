import nltk
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import json

stopwords = nltk.corpus.stopwords.words('english')
wordnet_lemmatizer = WordNetLemmatizer()

lyrics = pd.read_csv(r'Data\englishTracks.csv')

lyrics = lyrics[['artistName', 'trackName', 'processedLyrics']]
lyrics['tokens'] = None; lyrics['lemmatizedSong'] = None

#for i in range(1):
for i in range(len(lyrics)):
    song = json.loads(lyrics.loc[i, 'processedLyrics'])
    lemmSong = song.copy()
    for j in range(len(song)):
        words = word_tokenize(song[j].lower())
        #print(words)
        words = [j for j in words if j not in stopwords]
        words = [j for j in words if j.isalnum()]
        #print(words)
        song[j] = words
    lyrics.loc[i, 'tokens'] = json.dumps(song)
    for j in range(len(song)):
        lemmWords = [wordnet_lemmatizer.lemmatize(word) for word in song[j]] #using lemmatizer instead of stemming
        lemmSong[j] = lemmWords
    lyrics.loc[i,'lemmatizedSong'] = json.dumps(lemmSong)

lyrics.to_csv(r'Data\lemmatizedSongs.csv', index=False)