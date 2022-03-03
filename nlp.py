import pandas as pd
import json

import scispacy
import spacy
#import en_core_sci_lg
from spacy_langdetect import LanguageDetector

from spacy.language import Language

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('language_detector', last=True)

lyricsData= pd.read_csv(r'Data\lyricPreprocess.csv')
lyricsData['language'] = None; lyricsData['languageScore'] = None

for i in range(len(lyricsData)):
    text = str(' '.join(json.loads(lyricsData.loc[i, 'processedLyrics'])))
    doc = nlp(text)
    language = list(doc._.language.values())
    lyricsData.loc[i, 'language'] = language[0]
    lyricsData.loc[i, 'languageScore'] = language[1]

lyricsData.to_csv(r'Data\language.csv', index=False)