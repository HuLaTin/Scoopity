import pandas as pd
import re
import util

charPattern = r'[^A-z\ ]|\[|\]'

text = open(r"Data\journey.txt", "r")
journey = text.read()
text.close()

journey = journey.split('\n\n')

for i in range(len(journey)):
#for i in range(5):
    sent = journey[i]
    sent = util.remove_accented_chars(sent)
    sent = re.sub(charPattern, '', sent)
    journey[i]  = sent.strip()
    #print(len(sent))

journey = list(filter(lambda i: len(i) >= 50, journey))
len(journey)
journey = ', '.join(journey)

with open('journey2.txt', 'w') as journey2:
    journey2.write(journey)

