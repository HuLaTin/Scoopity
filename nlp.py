import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, SnowballStemmer
#from num2words import num2words
import json

stopwords = nltk.corpus.stopwords.words('english')
wordnet_lemmatizer = WordNetLemmatizer()
stemmer = SnowballStemmer('english')

lyrics = pd.read_csv(r'Data\englishTracks.csv')

lyrics = lyrics[['artistName', 'trackName', 'processedLyrics']]
lyrics['tokens'] = None; lyrics['lemmatizedSong'] = None; lyrics['stemSong'] = None

#for i in range(5):
for i in range(len(lyrics)):
    song = json.loads(lyrics.loc[i, 'processedLyrics'])
    for j in range(len(song)):
        words = word_tokenize(song[j].lower())
        words = [k for k in words if k not in stopwords]
        words = [k for k in words if k.isalnum()]
        song[j] = words
    lemmSong = song.copy()
    lyrics.loc[i, 'tokens'] = json.dumps(song)
    for j in range(len(lemmSong)):
        lemmWords = [wordnet_lemmatizer.lemmatize(word) for word in lemmSong[j]] #using lemmatizer, brings words to root
        lemmSong[j] = lemmWords
    stemSong = lemmSong.copy()
    lyrics.loc[i,'lemmatizedSong'] = json.dumps(lemmSong)
    for j in range(len(stemSong)):
        stemWords = [stemmer.stem(word) for word in stemSong[j]] #using stemmer, breaks down words further to stems
        stemSong[j] = stemWords
    lyrics.loc[i,'stemSong'] = json.dumps(stemSong)

lyrics.to_csv(r'Data\lemmstemSongs.csv', index=False)