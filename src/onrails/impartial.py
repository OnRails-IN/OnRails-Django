import os
import random
import datetime

PARTITION_KEY_DICT = {
    'a':'Amelie', 'b':'Basterds', 'c':'Corleone', 'd':'Django', 'e':'Edgar',
    'f':'Flintstone', 'g':'Gandalf', 'h':'HansLanda', 'i':'Ireland', 'j':'Joker',
    'k':'Kubrick', 'l':'Lebowski', 'm':'Masterpiece', 'n':'Norman', 'o':'Ozymandias',
    'p':'Pikachu', 'q':'Quasimodo', 'r':'Reddit', 's':'Strangelove', 't':'Tambourine',
    'u':'Unicorn', 'v':'Vader', 'w':'Waffles', 'x':'Xenon', 'y':'Yoda', 'z':'Zulu'
}

LOG_PATH = os.path.abspath(\
    os.path.join(\
        os.path.dirname(__file__), '..', '..', 'logs', datetime.date.today().strftime("%b %Y")\
    )\
)
CARD_PATH = os.path.abspath(\
    os.path.join(\
        os.path.dirname(__file__), '..', '..', 'static', 'cards'
    )
)

def LOGGER(message):
	print("{} came into logger".format(message))
	if not os.path.exists(LOG_PATH):
		os.makedirs(LOG_PATH)
	with open(os.path.join(LOG_PATH, "Week " + str(datetime.date.today().isocalendar()[ 1 ]) + ".log"), 'a+') as file:
		file.write(str(datetime.datetime.now()) + "\t" + str(message) + "\n")
		return

def RAND6DIG():
	return str(random.randint(100, 1000)) + str(random.randint(100, 1000))

def FILLER(docs):
	for doc in docs:
		if 'Train_Number' in doc and 'Train_Name' not in doc:
			return