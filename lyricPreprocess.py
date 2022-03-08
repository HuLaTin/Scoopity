import pandas as pd
import json, re
import util

lyricData = pd.read_csv(r'Data\lyricData.csv') # import data

lyricData = lyricData[lyricData['isFound'] == True]
lyricData = lyricData[['artistName','trackName','lyrics']] # setting order of columns
lyricData['processedLyrics'] = None#; lyricData['uniqueWords'] = None # creation of new columns
#lyricData['language'] = None; lyricData['languageScore'] = None

#type(lyricData['lyrics'])
lyricData.reset_index(drop=True, inplace=True) # remove rows with nothing in them

nonlyricPattern = r'\[.*?\]|\(\s*?\)|\*+'
bracketPattern = r'\[.*|\]'
parenthesesPattern = r'\(.*?\)'
spacePattern = r'\s{2,}'
hyphenPattern = r'\-{2,}'
charPattern = r'[^A-zÀ-ÿ0-9\ \']'
dollaPattern = r'\$' #because of course they have to...

#for i in range(5):
for i in range(len(lyricData)):
    lyrics = json.loads(lyricData.loc[i,'lyrics'])
    for j in range(len(lyrics)):
        sent = lyrics[j]
        sent = re.sub(dollaPattern, 's', sent) # to remove $ from lyrics
        
        sent = util.strip_html_tags(sent) # strip html tags, common with webscraping
        sent = util.remove_accented_chars(sent) # swaps accented characters
        sent = util.expand_contractions(sent) # expand contractions

        sent = re.sub(nonlyricPattern, '', sent);sent = re.sub(bracketPattern, '', sent)
        sent = re.sub(parenthesesPattern, '', sent)#;sent = re.sub(hyphenPattern, '-', sent)
        sent = re.sub(charPattern, ' ', sent)
        sent = re.sub(spacePattern, ' ', sent)
        
        lyrics[j] = sent.strip()
    
    while('' in lyrics): # remove empty objects
        lyrics.remove('')

    if len(lyrics) == 0:
        lyricData.loc[i, 'processedLyrics'] = None
        continue

    lyricData.loc[i, 'processedLyrics'] = json.dumps(lyrics)
        
    #sentences = sent_tokenize(lyrics)

    #lyrics = word_tokenize(lyrics.lower()) #tokenize each word/ turn all letters lower case

    #lyrics = [word for word in lyrics if word not in stopwords.words('english')] # filtering out stop words
    #lyricData.loc[i,'tokens'] = [word for word in lyrics if word.isalnum()] # filter out if not alpha-numeric
    #lyricData.loc[i, 'uniqueWords'] = set(lyrics) # store a set of unique words

    # what about numbers?

nan_value = float("NaN"); lyricData.replace("", nan_value, inplace=True) #replace any rows that are empty with 'NaN' values
lyricData.dropna(subset = ["processedLyrics"], inplace=True); lyricData.reset_index(drop=True, inplace=True) # drop the 'NaN' rows and reset index inplace

languageData = lyricData.copy(deep=True)
lyricData.to_csv(r'Data\lyricPreprocess.csv', index = False)

#############################################################

import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector

# build language detector
@Language.factory("language_detector") # decorator
def get_lang_detector(nlp, name):
   return LanguageDetector()

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('language_detector', last=True)
#lyricsData= pd.read_csv(r'Data\lyricPreprocess.csv')
languageData = languageData[['artistName', 'trackName', 'processedLyrics']] # select and order columns
languageData['language'] = None; languageData['languageScore'] = None # new columns

for i in range(len(languageData)):
    text = str(' '.join(json.loads(languageData.loc[i, 'processedLyrics'])))
    doc = nlp(text)
    language = list(doc._.language.values())
    languageData.loc[i, 'language'] = language[0]
    languageData.loc[i, 'languageScore'] = language[1]

languageData = languageData.loc[(languageData['language'] == 'en') & (languageData['languageScore'] >= .7)] # select rows
languageData.to_csv(r'Data\englishTracks.csv', index=False)