import operator
import pickle
from datetime import date, datetime, timedelta
from itertools import chain
from enum import Enum

import pandas as pd

from carnivora.instabot.config import Config
from carnivora.instabot.log import Log


frequencies = {
    "Business day frequency": "B",
    "Custom business day frequency": "C",
    "Calendar day frequency": "D",
    "Weekly frequency": "W",
    "Month end frequency": "M",
    "Semi-month end frequency (15th and end of month)": "SM",
    "Business month end frequency": "BM",
    "Custom business month end frequency": "CBM",
    "Month start frequency": "MS",
    "Semi-month start frequency (1st and 15th)": "SMS",
    "Business month start frequency": "BMS",
    "Custom business month start frequency": "CBMS",
    "Quarter end frequency": "Q",
    "Business quarter end frequency": "BQ",
    "Quarter start frequency": "QS",
    "Business quarter start frequency": "BQS",
    "Year end frequency": "Y",
    "Business year end frequency": "BA",
    "Year start frequency": "YS",
    "Business year start frequency": "BYS",
    "Business hour frequency": "BH",
    "Hourly frequency": "H",
    "Minutely frequency": "T",
    "Secondly frequency": "S",
    "Milliseconds": "L",
    "Microseconds": "U",
    "Nanoseconds": "N",
}

timeranges = {
    "Last month": 43800,
    "Last day": 1440,
    "Last hour": 60,
    "Last minute": 1,
    "Last 90 days": 129600,
    "Last year": 525600,
    "None": None,
}


class Statistics:
    @staticmethod
    def get_hashtags(username, n=40, truncated_name_length=100):
        hashtags = {}
        try:
            log_path = Config.bot_path + "log/" + username
            with open(log_path + "/hashtags.pickle", "rb") as f:
                hashtags = pickle.load(f)
        except FileNotFoundError:
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
    def extract(actions_flattened, action_type, timerange, freq="Calendar day frequency"):
        lst = [item["time"] for item in actions_flattened if item["type"] == action_type]
        if not lst:
            return [], []

        df = pd.DataFrame({'time': lst, 'action_type': action_type})
        df = df.set_index(pd.DatetimeIndex(df['time']))

        if timerange and timerange != "None":
            df = df[(df['time'] > datetime.now() - timedelta(minutes=timeranges[timerange]))]

        grouped = df.groupby(pd.Grouper(freq=frequencies[freq])).size().to_frame()

        dates = grouped.index.tolist()
        quantities = grouped.values.tolist()
        quantities_flat = [item for sublist in quantities for item in sublist]
        return dates, quantities_flat

    @staticmethod
    def get_timelines(username, freq="Calendar day frequency", timerange=None, dateformat="%Y-%m-%d %H:%M:%S"):
        actions = Statistics.get_actions(username)
        actions_flattened = list(chain.from_iterable([values for _, values in actions.items()]))

        likes_dates, likes_quantities = Statistics.extract(actions_flattened, action_type="like",
                                                           timerange=timerange, freq=freq)
        comments_dates, comments_quantities = Statistics.extract(actions_flattened, action_type="comment",
                                                                 timerange=timerange, freq=freq)
        follows_dates, follows_quantities = Statistics.extract(actions_flattened, action_type="follow",
                                                               timerange=timerange, freq=freq)

        likes_data = [{'x': x.strftime(dateformat), 'y': y}
                      for x, y in list(zip(likes_dates, likes_quantities))]
        comments_data = [{'x': x.strftime(dateformat), 'y': y}
                         for x, y in list(zip(comments_dates, comments_quantities))]
        follows_data = [{'x': x.strftime(dateformat), 'y': y}
                        for x, y in list(zip(follows_dates, follows_quantities))]

        index_dates = list(likes_dates)
        index_dates.extend(x for x in comments_dates if x not in index_dates)
        index_dates.extend(x for x in follows_dates if x not in index_dates)
        index = [x.strftime(dateformat) for x in sorted(index_dates)]

        return index, likes_data, comments_data, follows_data
