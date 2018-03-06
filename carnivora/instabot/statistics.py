import operator
import pickle

from carnivora.instabot.config import Config

class Statistics:
    @staticmethod
    def get_hashtags(username, n=40, truncated_name_length=100):
        hashtags = {}
        try:
            with open(Config.bot_path + username + "/log/hashtags.pickle", "rb") as f:
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
            with open(Config.bot_path + username + "/log/followed_users_all_time.pickle", "rb") as f:
                followed_accounts = pickle.load(f)
        except:
            pass
        return len(followed_accounts.values())

    @staticmethod
    def get_amount_of_actions(username):
        action_list = {}
        try:
            with open(Config.bot_path + username + "/log/actionList.pickle", "rb") as f:
                action_list = pickle.load(f)
        except:
            pass
        amount_of_users = 0
        amount_of_interactions = 0
        amount_of_likes = 0
        amount_of_follows = 0
        amount_of_comments = 0
        for k, v in action_list.items():
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




if __name__ == "__main__":
    print(Statistics.get_hashtags())