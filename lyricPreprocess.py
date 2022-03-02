import pandas as pd
from pyparsing import Regex
#from bs4 import BeautifulSoup
import spacy, json, re
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

#type(lyricData['lyrics'])

lyricData.dropna(subset = ["lyrics"], inplace=True); lyricData.reset_index(drop=True, inplace=True) # remove rows with nothing in them

nonlyricPattern = r'\[.*?\]|\(\s*?\)|\*+|\"'
parenthesesPattern = r'\(.*?\)'
spacePattern = r'\s{2,}'
charPattern = r'[^A-zÀ-ÿ0-9\ \']'
dollaPattern = r'\$' #because of course they have to...

#for i in range(5):
for i in range(len(lyricData)):
    lyrics = json.loads(lyricData.loc[i,'lyrics'])
    print(lyrics)
    for j in range(len(lyrics)):
        sent = lyrics[j]
        
        sent = util.strip_html_tags(sent) # strip html tags, common with webscraping
        sent = util.remove_accented_chars(sent) # swaps accented characters
        sent = util.expand_contractions(sent) # expand contractions

        lyrics[j] = re.sub(nonlyricPattern, '', lyrics[j])
        lyrics[j] = re.sub(parenthesesPattern, '', lyrics[j])
        lyrics[j] = re.sub(charPattern, ' ', lyrics[j])
        lyrics[j] = re.sub(spacePattern, ' ', lyrics[j])
        lyrics[j] = re.sub(dollaPattern, 's', lyrics[j]) # to remove $ from lyrics
        lyrics[j] = lyrics[j].strip()
    
    while('' in lyrics): # remove empty objects
        lyrics.remove('')

    
    print(lyrics)

        
    #sentences = sent_tokenize(lyrics)

    #lyrics = word_tokenize(lyrics.lower()) #tokenize each word/ turn all letters lower case

    lyrics = [word for word in lyrics if word not in stopwords.words('english')] # filtering out stop words
    lyricData.loc[i,'tokens'] = [word for word in lyrics if word.isalnum()] # filter out if not alpha-numeric
    lyricData.loc[i, 'uniqueWords'] = set(lyrics) # store a set of unique words

    # what about numbers?

nan_value = float("NaN"); lyricData.replace("", nan_value, inplace=True) #replace any rows that are empty with 'NaN' values
lyricData.dropna(subset = ["lyrics"], inplace=True); lyricData.reset_index(drop=True, inplace=True) # drop the 'NaN' rows and reset index inplace

lyricData.to_csv(r'Data\lyricPreprocess.csv', index = False)

