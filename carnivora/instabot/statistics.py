import operator
import pickle
from datetime import date, datetime, timedelta
from itertools import chain
from enum import Enum

import pandas as pd

from carnivora.instabot.config import Config
from carnivora.instabot.log import Log


class Statistics:
    @staticmethod
    def get_hashtags(username, n=40, truncated_name_length=100):
        hashtags = {}
        try:
            log_path = Config.bot_path + "log/" + username
            with open(log_path + "/hashtags.pickle", "rb") as f:
                hashtags = pickle.load(f)
        except:
            for h in Config.topics:
                hashtags[h] = 2
        tuples = sorted(hashtags.items(), key=operator.itemgetter(1), reverse=True)
        hashtag_names = []
        hashtag_scores = []
        for hashtag_name, hashtag_score in tuples[:n]:
            hashtag_names.append(hashtag_name[:truncated_name_length])
            hashtag_scores.append(hashtag_score)
        return hashtag_names, hashtag_scores

    @staticmethod
    def get_amount_of_followed_accounts(username):
        followed_accounts = {}
        try:
            log_path = Config.bot_path + "log/" + username
            with open(log_path + "/followed_users_all_time.pickle", "rb") as f:
                followed_accounts = pickle.load(f)
        except FileNotFoundError:
            pass
        return len(followed_accounts.values())

    @staticmethod
    def get_actions(username):
        try:
            log_path = Config.bot_path + "log/" + username
            with open(log_path + "/action_list.pickle", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}

    @staticmethod
    def get_amount_of_actions(username):
        actions = Statistics.get_actions(username)
        amount_of_users = 0
        amount_of_interactions = 0
        amount_of_likes = 0
        amount_of_follows = 0
        amount_of_comments = 0
        for k, v in actions.items():
            amount_of_users += 1
            for d in v:
                amount_of_interactions += 1
                if d["type"] == "like":
                    amount_of_likes += 1
                if d["type"] == "follow":
                    amount_of_follows += 1
                if d["type"] == "comment":
                    amount_of_comments += 1
        return amount_of_users, amount_of_interactions, amount_of_likes, amount_of_follows, amount_of_comments

    @staticmethod
    def extract(actions_flattened, action_type, dateformat="%Y-%m-%d %H:%M:%S"):
        lst = [item["time"] for item in actions_flattened if item["type"] == action_type]
        if not lst:
            return [], []

        for i in range(100):
            lst.append(datetime.now() - timedelta(minutes=i))

        df = pd.DataFrame({'time': lst, 'action_type': action_type})
        df = df.set_index(pd.DatetimeIndex(df['time']))

        grouped = df.groupby(pd.TimeGrouper(freq='30Min')).size().to_frame()

        dates_strings = [d.strftime(dateformat) for d in grouped.index.tolist()]
        quantities = grouped.values.tolist()
        quantities_flat = [item for sublist in quantities for item in sublist]
        return dates_strings, quantities_flat

    @staticmethod
    def get_timelines(username):
        actions = Statistics.get_actions(username)
        actions_flattened = list(chain.from_iterable([values for _, values in actions.items()]))

        likes_dates_strings, likes_quantities = Statistics.extract(actions_flattened, action_type="like")
        comments_dates_strings, comments_quantities = Statistics.extract(actions_flattened, action_type="comment")
        follows_dates_strings, follows_quantities = Statistics.extract(actions_flattened, action_type="follow")

        likes_data = [{'x': x, 'y': y} for x, y in list(zip(likes_dates_strings, likes_quantities))]
        comments_data = [{'x': x, 'y': y} for x, y in list(zip(comments_dates_strings, comments_quantities))]
        follows_data = [{'x': x, 'y': y} for x, y in list(zip(follows_dates_strings, follows_quantities))]

        index = list(likes_dates_strings)
        index.extend(x for x in comments_dates_strings if x not in index)
        index.extend(x for x in follows_dates_strings if x not in index)

        return index, likes_data, comments_data, follows_data
