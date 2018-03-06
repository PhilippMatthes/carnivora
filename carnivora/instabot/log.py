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
        truncated_log = reversed(log[-page_size:])
        if search == '' or search is None:
            return truncated_log
        else:
            filtered_log = [t for t in truncated_log if search.lower() in t[1].lower()]
            return filtered_log

