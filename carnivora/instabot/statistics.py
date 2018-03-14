import operator
import pickle
from datetime import date
from itertools import chain
from enum import Enum

from carnivora.instabot.config import Config


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
    def get_timelines(username):
        actions = Statistics.get_actions(username)
        actions_flattened = list(chain.from_iterable([values for _, values in actions.items()]))

        likes = [item["time"] for item in actions_flattened if item["type"] == "like"]
        comments = [item["time"] for item in actions_flattened if item["type"] == "comment"]
        follows = [item["time"] for item in actions_flattened if item["type"] == "follow"]

        days_likes = {}
        days_comments = {}
        days_follows = {}

        for dt in likes:
            days_likes.setdefault(dt.toordinal(), []).append(dt)
        for dt in comments:
            days_comments.setdefault(dt.toordinal(), []).append(dt)
        for dt in follows:
            days_follows.setdefault(dt.toordinal(), []).append(dt)

        likes_grouped = [days_likes.get(day, []) for day in range(min(days_likes), max(days_likes) + 1)]
        comments_grouped = [days_comments.get(day, []) for day in range(min(days_comments), max(days_comments) + 1)]
        follows_grouped = [days_follows.get(day, []) for day in range(min(days_follows), max(days_follows) + 1)]

        likes_dates_strings = [date.fromordinal(day).strftime("%Y-%m-%d")
                               for day in range(min(days_likes), max(days_likes) + 1)]
        comments_dates_strings = [date.fromordinal(day).strftime("%Y-%m-%d")
                                  for day in range(min(days_comments), max(days_comments) + 1)]
        follows_dates_strings = [date.fromordinal(day).strftime("%Y-%m-%d")
                                 for day in range(min(days_follows), max(days_follows) + 1)]

        likes_quantities = [len(l) for l in likes_grouped]
        comments_quantities = [len(l) for l in comments_grouped]
        follows_quantities = [len(l) for l in follows_grouped]

        return \
            likes_dates_strings, likes_quantities,\
            comments_dates_strings, comments_quantities,\
            follows_dates_strings, follows_quantities
