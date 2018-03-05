import datetime
import pickle

from carnivora.instabot.config import Config


class Log:

    def __init__(self):
        pass

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
    def get(n, offset=0):
        log = []
        try:
            with open(Config.bot_path + "log/log.pickle", "rb") as f:
                log = pickle.load(f)
        except:
            pass
        return reversed(log[-n:-offset])

    @staticmethod
    def number_of_pages(page_size):
        try:
            with open(Config.bot_path + "log/log.pickle", "rb") as f:
                log = pickle.load(f)
        except:
            pass
        return int(len(log)/page_size)

