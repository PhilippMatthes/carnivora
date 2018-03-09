import datetime
import pickle

from carnivora.instabot.config import Config


class Log:
    @staticmethod
    def update(screenshot_path, browser, log_path, text="", image=""):
        browser.save_screenshot(screenshot_path)

        date = str(datetime.datetime.now())
        log = []
        try:
            with open(log_path, "rb") as f:
                log = pickle.load(f)
        except:
            pass
        log.append([date, text, image])
        with open(log_path, "wb") as f:
            pickle.dump(log, f)

    @staticmethod
    def get(log_path, page_size, search=''):
        log = []
        try:
            with open(log_path, "rb") as f:
                log = pickle.load(f)
        except FileNotFoundError:
            pass
        if search == '' or search is None:
            return reversed(log[-page_size:])
        else:
            filtered_log = [t for t in log if search.lower() in t[1].lower()]
            return reversed(filtered_log[-page_size:])

