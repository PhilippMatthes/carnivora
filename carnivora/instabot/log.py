import datetime
import pickle

from carnivora.instabot.config import Config


class Log:
    @staticmethod
    def update(text="", image=""):
        date = str(datetime.datetime.now())
        log = []
        try:
            with open(Config.bot_path + "log/log.pickle", "rb") as f:
                log = pickle.load(f)
        except:
            pass
        log.append([date, text, image])
        with open(Config.bot_path + "log/log.pickle", "wb") as f:
            pickle.dump(log, f)

    @staticmethod
    def get(n, search=''):
        log = []
        try:
            with open(Config.bot_path + "log/log.pickle", "rb") as f:
                log = pickle.load(f)
        except:
            pass
        truncated_log = reversed(log[-n:])
        if search == '' or search is None:
            return truncated_log
        else:
            filtered_log = [t for t in truncated_log if search.lower() in t[1].lower()]
            return filtered_log

    @staticmethod
    def number_of_pages(page_size):
        try:
            with open(Config.bot_path + "log/log.pickle", "rb") as f:
                log = pickle.load(f)
        except:
            pass
        return int(len(log)/page_size)

