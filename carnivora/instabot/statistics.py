import operator
import pickle

from config import Config


class Statistics:
    @staticmethod
    def get_hashtags():
        hashtags = {}
        try:
            with open(Config.bot_path + "log/hashtags.pickle", "rb") as f:
                hashtags = pickle.load(f)
        except:
            for h in Config.topics:
                hashtags[h] = 2
        return sorted(hashtags.items(), key=operator.itemgetter(1), reverse=True)


if __name__ == "__main__":
    print(Statistics.get_hashtags())