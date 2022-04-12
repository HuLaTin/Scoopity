#from tokenize import Token
#from aitextgen.tokenizers import train_tokenizer
#from aitextgen.TokenDataset import TokenDataset
#from aitextgen.utils import GPT2ConfigCPU
#from aitextgen import aitextgen

import pandas as pd
import json
import util
import re

import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector

# build language detector
@Language.factory("language_detector") # decorator
def get_lang_detector(nlp, name):
   return LanguageDetector()

nonlyricPattern = r'\[.*?\]|\(\s*?\)|\*+'
bracketPattern = r'\[.*|\]'
parenthesesPattern = r'\(.*?\)'
spacePattern = r'\s{2,}'
hyphenPattern = r'\-{2,}'
charPattern = r'[^A-zÀ-ÿ0-9\ \'\,\.\!\?]'

lyricData = pd.read_csv(r'aiTextGen\Data\largelyricData.csv')
lyricData.dropna(inplace=True)
lyricData.reset_index(drop=True, inplace=True)
lyricData = lyricData[['trackName', 'lyrics']]
lyricData['processedLyrics'] = None

for i in range(len(lyricData)):
    lyrics = json.loads(lyricData.loc[i,'lyrics'])
    for j in range(len(lyrics)):
        sent = lyrics[j]

        sent = util.strip_html_tags(sent) # strip html tags, common with webscraping
        sent = util.remove_accented_chars(sent) # swaps accented characters

        sent = re.sub(nonlyricPattern, '', sent);sent = re.sub(bracketPattern, '', sent)
        sent = re.sub(parenthesesPattern, '', sent);sent = re.sub(hyphenPattern, '-', sent)
        sent = re.sub(charPattern, ' ', sent)
        sent = re.sub(spacePattern, ' ', sent)
        
        lyrics[j] = sent.strip()
        #print(lyrics)

    lyrics = list(set(lyrics))
    
    while('' in lyrics): # remove empty objects
        lyrics.remove('')

    lyricData.loc[i, 'processedLyrics'] = '. '.join(lyrics)

lyricData= lyricData[['processedLyrics']]
#lyricData.to_csv(r'Data\lyricList.csv', index=False, header=False)

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('language_detector', last=True)

#lyricList = pd.DataFrame(lyricList)
lyricData['language'] = None

for i in range(len(lyricData)):
    text = lyricData.loc[i, 'processedLyrics']
    doc = nlp(text)
    language = list(doc._.language.values())
    lyricData.loc[i, 'language'] = language[0]

lyricData = lyricData.loc[(lyricData['language'] == 'en')]
lyricData = lyricData[['processedLyrics']]
lyricData = lyricData.drop_duplicates()

lyricData.to_csv(r'aiTextGen\Data\lyricList.csv', index=False, header=False)
