import random
import time

random.seed(time.time())


text = open(r"journey2.txt", "r")
journey = text.read()
text.close()

journey = journey.split(', ')

i = random.randrange(0, len(journey))
print(journey[i])