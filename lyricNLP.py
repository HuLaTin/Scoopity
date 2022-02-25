import pandas as pd
from fuzzywuzzy import process, fuzz
import re

lyricData = pd.read_csv(r'Data\lyricData.csv')

print(lyricData.shape)
lyricData.dropna(subset = ["lyrics"], inplace=True)
lyricData.reset_index(drop=True, inplace=True)
print(lyricData.shape)

lyricData['artistMatch'] = 0

lyricPattern = r'\[.*?\]'
#lyricPattern = r'\[.*\]'


#for i in range(200):
for i in range(len(lyricData)):
    #print(lyricData.loc[i,'artistName'] + ' ' + str(lyricData.loc[i, 'geniusArtist']))

    # typecast as string? str()
    fuzzMatch = fuzz.partial_ratio(lyricData.loc[i,'artistName'].upper(), lyricData.loc[i, 'geniusArtist'].upper())
    if fuzzMatch < 90:
        print(lyricData.loc[i,'artistName'] + ' & ' + str(lyricData.loc[i, 'geniusArtist']) + ': Do not match')
        lyricData.loc[i, 'aristMatch'] = 1

        lyricData.loc[i, 'lyrics'] = re.sub(lyricPattern, '', lyricData.loc[i, 'lyrics'])

