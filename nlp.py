import nltk
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import json

stopwords = nltk.corpus.stopwords.words('english')


lyrics = pd.read_csv(r'Data\englishTrack.csv')

lyrics = lyrics[['artistName', 'trackName', 'processedLyrics']]

for i in range(1):
#for i in range(len(lyrics)):
    song = json.loads(lyrics.loc[i, 'processedLyrics'])
    for j in song:
        words = word_tokenize(j)
        print(words)
        words = [j for j in words if j not in stopwords]
        words = [j for j in words if j.isalnum()]
        print(words)
