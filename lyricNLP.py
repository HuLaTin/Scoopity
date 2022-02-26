import pandas as pd
from bs4 import BeautifulSoup
import spacy
#import unidecode
from word2number import w2n
#import contractions
#from fuzzywuzzy import process, fuzz
#import re
import util
#import string

# load spacy model, or "en_core_web_sm"
nlp = spacy.load('en_core_web_md')

lyricData = pd.read_csv(r'Data\lyricData.csv')
lyricData = lyricData[['artistName','trackName','tags','lyrics']]

lyricData.dropna(subset = ["lyrics"], inplace=True); lyricData.reset_index(drop=True, inplace=True)

for i in range(len(lyricData)):
    lyrics = lyricData.loc[i,'lyrics'] 
    lyrics = util.strip_html_tags(lyrics) # strip html tags, common with webscraping
    lyrics = util.remove_accented_chars(lyrics) # swaps accented characters
    lyrics = util.expand_contractions(lyrics) # expand contractions
    lyricData.loc[i,'lyrics'] = lyrics

#check = util.strip_html_tags(lyricData.loc[0,'lyrics'])

lyricPattern = r'\[.*?\]|\(\s*?\)|\*+|\"'
parenthesesPattern = r'\(.*?\)'
spacePattern = r'\s{2,}'
charPattern = r'[^A-zÀ-ÿ0-9\.\?\,\!\-\ \']'
sboysPattern = r'\$' #because of course they have to...


#lyricData['lyrics'] = lyricData['lyrics'].str.lower()
#lyricData['lyrics'] = lyricData['lyrics'].str.encode("ascii", "ignore").str.decode('utf-8')

lyricData['lyrics'].replace(to_replace=lyricPattern, value='', inplace=True, regex=True); lyricData['lyrics'].replace(to_replace=parenthesesPattern, value='', inplace=True, regex=True)
lyricData['lyrics'].replace(to_replace=charPattern, value=' ', inplace=True, regex=True);lyricData['lyrics'].replace(to_replace=spacePattern, value=' ', inplace=True, regex=True)
lyricData['lyrics'].replace(to_replace=sboysPattern, value='s', inplace=True, regex=True) #sboys like their dollar signs
#lyricData['lyrics'] = lyricData['lyrics'].str.strip()

nan_value = float("NaN")
lyricData.replace("", nan_value, inplace=True)

lyricData.dropna(subset = ["lyrics"], inplace=True); lyricData.reset_index(drop=True, inplace=True)

lyricData.to_csv(r'Data\lyricPreprocess.csv', index = False)
