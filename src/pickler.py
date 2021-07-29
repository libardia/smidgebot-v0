import pickle

DATAFILE = 'data.p'

def save(data):
    with open(DATAFILE, 'wb') as pic:
        pickle.dump(data, pic)

def load():
    try:
        with open(DATAFILE, 'rb') as pic:
            return pickle.load(pic)
    except:
        return None
