import datetime

import telepot
import telepot.api
import urllib3
import pickle
import matplotlib.pyplot as plt

from carnivora.instabot.config import Config
from carnivora.instabot.log import Log

telepot.api._pools = {
    'default': urllib3.PoolManager(num_pools=3, maxsize=10, retries=10, timeout=240),
}


class Mailer:
    def __init__(self):
        try:
            with open(Config.bot_path + "log/telepot_api_key.pickle", "rb") as f:
                self.key = pickle.load(f)
        except:
            key = input("Telepot api key was not discovered. Please enter your Key: ")
            while len(key) != 45:
                key = input("The key you entered is no valid Telegram API key. Please try again: ")
            with open(Config.bot_path + "log/telepot_api_key.pickle", "wb") as f:
                pickle.dump(key, f)
            self.key = key

        try:
            with open(Config.bot_path + "log/telepot_user_number.pickle", "rb") as f:
                self.telepot_user_number = pickle.load(f)
        except:
            telepot_user_number = input("User key was not discovered. Please enter your Key: ")
            while len(telepot_user_number) != 9:
                telepot_user_number = input("The key you entered is no valid user key. Please try again: ")
            with open(Config.bot_path + "log/telepot_user_number.pickle", "wb") as f:
                pickle.dump(telepot_user_number, f)
            self.telepot_user_number = telepot_user_number

        self.bot = telepot.Bot(self.key)

    def send(self, text):
        self.bot.sendMessage(self.telepot_user_number, text)

    def send_image(self, image, caption):
        with open(image, 'rb') as f:
            self.bot.sendPhoto(self.telepot_user_number, f, caption)

    def send_stats(self, numbers, hashtags, caption):
        if len(numbers) != len(hashtags):
            raise Exception("Number length doesnt equal hashtags length")
        fig = plt.figure()
        x = range(0, len(hashtags))
        y = numbers
        labels = hashtags
        plt.plot(x, y, 'r')
        plt.xticks(x, labels, rotation='vertical')
        plt.margins(0.2)
        image = Config.bot_path + "log/stats.png"
        fig.savefig(image)
        self.send_image(image, caption)

    def get_current_message(self):
        try:
            updates = self.bot.getUpdates()
            if len(updates) == 0:
                return ""
            else:
                message_offset = updates[len(updates) - 1]["update_id"]
                current_message = self.bot.getUpdates(offset=message_offset)
                return current_message[0]["message"]["text"]
        except:
            return ""
