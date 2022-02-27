import pandas as pd
#from bs4 import BeautifulSoup
import spacy
#import unidecode
#from word2number import w2n
#import contractions
#from fuzzywuzzy import process, fuzz
#import re
import util
#import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords


# load spacy model, or "en_core_web_sm"
nlp = spacy.load('en_core_web_md')

lyricData = pd.read_csv(r'Data\lyricData.csv') # import data
lyricData = lyricData[['artistName','trackName','tags','lyrics']] # setting order of columns
lyricData['tokens'] = None; lyricData['uniqueWords'] = None # creation of new columns

lyricData.dropna(subset = ["lyrics"], inplace=True); lyricData.reset_index(drop=True, inplace=True) # remove rows with nothing in them


nonlyricPattern = r'\[.*?\]|\(\s*?\)|\*+|\"'
parenthesesPattern = r'\(.*?\)'
spacePattern = r'\s{2,}'
charPattern = r'[^A-zÀ-ÿ0-9\ \']'
sboysPattern = r'\$' #because of course they have to...

lyricData['lyrics'].replace(to_replace=nonlyricPattern, value='', inplace=True, regex=True); lyricData['lyrics'].replace(to_replace=parenthesesPattern, value='', inplace=True, regex=True)
lyricData['lyrics'].replace(to_replace=charPattern, value=' ', inplace=True, regex=True);lyricData['lyrics'].replace(to_replace=spacePattern, value=' ', inplace=True, regex=True)
lyricData['lyrics'].replace(to_replace=sboysPattern, value='s', inplace=True, regex=True) #sboys like their dollar signs
lyricData['lyrics'] = lyricData['lyrics'].str.strip()

for i in range(len(lyricData)):
    lyrics = lyricData.loc[i,'lyrics'] 
    lyrics = util.strip_html_tags(lyrics) # strip html tags, common with webscraping
    lyrics = util.remove_accented_chars(lyrics) # swaps accented characters
    lyrics = util.expand_contractions(lyrics) # expand contractions
    #sentences = sent_tokenize(lyrics)

    lyrics = word_tokenize(lyrics.lower()) #tokenize each word/ turn all letters lower case

    lyrics = [word for word in lyrics if word not in stopwords.words('english')] # filtering out stop words
    lyricData.loc[i,'tokens'] = [word for word in lyrics if word.isalnum()] # filter out if not alpha-numeric
    lyricData.loc[i, 'uniqueWords'] = set(lyrics) # store a set of unique words

    # what about numbers?

nan_value = float("NaN"); lyricData.replace("", nan_value, inplace=True) #replace any rows that are empty with 'NaN' values
lyricData.dropna(subset = ["lyrics"], inplace=True); lyricData.reset_index(drop=True, inplace=True) # drop the 'NaN' rows and reset index inplace

lyricData.to_csv(r'Data\lyricPreprocess.csv', index = False)

