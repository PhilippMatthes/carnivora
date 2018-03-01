import pickle

from carnivora.instabot.config import Config


class Log:

    def __init__(self):
        pass

    @staticmethod
    def update(date, text, image):
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
    def get():
        log = []
        try:
            with open(Config.bot_path + "log/log.pickle", "rb") as f:
                log = pickle.load(f)
        except:
            pass
        with open(Config.bot_path + "log/log.pickle", "wb") as f:
            pickle.dump([], f)
        return log

