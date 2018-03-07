import datetime
import pickle

from carnivora.instabot.config import Config


class Log:
    @staticmethod
    def update(logpath, text="", image=""):
        date = str(datetime.datetime.now())
        log = []
        try:
            with open(logpath, "rb") as f:
                log = pickle.load(f)
        except:
            pass
        log.append([date, text, image])
        with open(logpath, "wb") as f:
            pickle.dump(log, f)

    @staticmethod
    def get(logpath, page_size, search=''):
        log = []
        try:
            with open(logpath, "rb") as f:
                log = pickle.load(f)
        except:
            pass
        if search == '' or search is None:
            return reversed(log[-page_size:])
        else:
            filtered_log = [t for t in log if search.lower() in t[1].lower()]
            return reversed(filtered_log[-page_size:])

