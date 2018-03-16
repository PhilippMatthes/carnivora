import pickle
import threading
import datetime
from time import sleep

STRUCTURE = {"date_ordinal": None, "like": 0, "follow": 0, "comment": 0, "unfollow": 0}


class Dispatcher:
    def __init__(self, log_path, max_likes=600, max_follows=400, max_comments=200, max_unfollows=400):
        self.log_file = log_path + "/dispatch_file.pickle"
        self.dispatch_log = self.load_log_file()
        self.max_likes = max_likes
        self.max_follows = max_follows
        self.max_comments = max_comments
        self.max_unfollows = max_unfollows

    def load_log_file(self):
        try:
            with open(self.log_file, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            with open(self.log_file, "wb") as f:
                default = STRUCTURE.copy()
                default["date_ordinal"] = datetime.datetime.now().toordinal()
                pickle.dump(default, f)
                return default

    @staticmethod
    def seconds_until_midnight(date):
        return ((24 - date.hour - 1) * 60 * 60) + ((60 - date.minute - 1) * 60) + (60 - date.second)

    def next_action(self):
        self.check_log_file()
        self.dispatch_log = self.load_log_file()

        likes_left = self.max_likes - self.dispatch_log["like"]
        follows_left = self.max_follows - self.dispatch_log["follow"]
        comments_left = self.max_comments - self.dispatch_log["comment"]
        unfollows_left = self.max_unfollows - self.dispatch_log["unfollow"]

        likes_quotient = likes_left / self.max_likes if likes_left != 0 else 0
        follows_quotient = follows_left / self.max_follows if follows_left != 0 else 0
        comments_quotient = comments_left / self.max_comments if comments_left != 0 else 0
        unfollows_quotient = unfollows_left / self.max_unfollows if unfollows_left != 0 else 0

        seconds = Dispatcher.seconds_until_midnight(date=datetime.datetime.now())

        l = [likes_quotient, follows_quotient, comments_quotient, unfollows_quotient]
        if l[0] >= sum(l) / len(l) and l[0] != 0:
            delay, action = seconds / likes_left, "like"
        elif l[1] >= sum(l) / len(l) and l[0] != 0:
            delay, action = seconds / follows_left, "follow"
        elif l[2] >= sum(l) / len(l) and l[0] != 0:
            delay, action = seconds / comments_left, "comment"
        elif l[3] != 0:
            delay, action = seconds / unfollows_left, "unfollow"
        else:
            return "sleep", 0

        return delay, action

    def log_action(self, action):
        self.dispatch_log[action] += 1
        self.store_log_file()

    def check_log_file(self):
        if self.dispatch_log["date_ordinal"] != datetime.datetime.now().toordinal():
            self.dispatch_log = STRUCTURE.copy()
            self.dispatch_log["date_ordinal"] = datetime.datetime.now().toordinal()
            with open(self.log_file, "wb") as f:
                pickle.dump(self.dispatch_log, f)

    def store_log_file(self):
        with open(self.log_file, "wb") as f:
            pickle.dump(self.dispatch_log, f)
