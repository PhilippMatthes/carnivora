from selenium import webdriver  # For webpage crawling
from time import sleep
import time
from selenium.webdriver.common.keys import Keys  # For input processing
from random import randint
import sys  # For file path processing
import datetime  # For timestamp
import pickle  # For data management
import os

from carnivora.instabot.mailer import Mailer
from carnivora.instabot.config import Config

if Config.headless_is_available:
    from xvfbwrapper import Xvfb


class Driver(object):
    def __init__(self):
        # Set up Telegram Message Client
        self.mailer = Mailer()

        # Set up virtual display
        if Config.headless_is_available:
            self.display = Xvfb()
            self.display.start()

        # Load history
        try:
            with open(Config.bot_path + "log/interacting_users.pickle", "rb") as f:
                self.interacting_users = pickle.load(f)
        except:
            with open(Config.bot_path + "log/interacting_users.pickle", "wb") as f:
                self.interacting_users = []
                pickle.dump([], f)
        try:
            with open(Config.bot_path + "log/hashtags.pickle", "rb") as f:
                self.hashtags = pickle.load(f)
        except:
            with open(Config.bot_path + "log/hashtags.pickle", "wb") as f:
                self.hashtags = {}
                for h in Config.topics:
                    self.hashtags[h] = 2
                pickle.dump(self.hashtags, f)
        try:
            with open(Config.bot_path + "log/actionList.pickle", "rb") as f:
                self.actionList = pickle.load(f)
        except:
            with open(Config.bot_path + "log/actionList.pickle", "wb") as f:
                self.actionList = {}
                pickle.dump({}, f)
        try:
            with open(Config.bot_path + "log/followed_users_all_time.pickle", "rb") as f:
                self.followed_accounts = pickle.load(f)
        except:
            with open(Config.bot_path + "log/followed_users_all_time.pickle", "wb") as f:
                self.followed_accounts = {}
                pickle.dump({}, f)
        try:
            with open(Config.bot_path + "log/followed_users.pickle", "rb") as f:
                self.accounts_to_unfollow = pickle.load(f)
        except:
            with open(Config.bot_path + "log/followed_users.pickle", "wb") as f:
                self.accounts_to_unfollow = []
                pickle.dump([], f)

        try:
            with open(Config.bot_path + "log/instagram_username.pickle", "rb") as f:
                self.username = pickle.load(f)
        except:
            key = input("Please enter your username: ")
            while len(key) == 0:
                key = input("You must enter a username. Please try again: ")
            with open(Config.bot_path + "log/instagram_username.pickle", "wb") as f:
                pickle.dump(key, f)
            self.username = key
        try:
            with open(Config.bot_path + "log/instagram_pass.pickle", "rb") as f:
                self.password = pickle.load(f)
        except:
            key = input("Please enter your password: ")
            while len(key) == 0:
                key = input("You must enter a password. Please try again: ")
            with open(Config.bot_path + "log/instagram_pass.pickle", "wb") as f:
                pickle.dump(key, f)
            self.password = key

        # Final setup
        if Config.headless_is_available:
            # self.browser = webdriver.PhantomJS(desired_capabilities=dcap)
            self.browser = webdriver.PhantomJS()

        else:
            self.browser = webdriver.Chrome(Config.bot_path + "/chromedriver")
        self.browser.set_window_size(1980, 1080)

    # Returns nicely formatted timestamp
    def timestamp(self):
        return time.strftime('%a %H:%M:%S') + " "

    def focus(self, element):
        self.browser.execute_script("arguments[0].focus();", element)

    # Checks if a user was followed already
    def user_followed_already(self, user):
        if user in self.followed_accounts:
            return True
        else:
            return False

    # Logs into Instagram automatically
    def login(self):

        self.mailer.send("Logging in.")
        print("Logging in.")
        self.browser.get(Config.start_url)
        sleep(5)

        if (self.browser.current_url == "https://www.instagram.com/"):
            return
        if (self.mailer.get_current_message() == "Pause"):
            self.mailer.send("Bot paused.")
            raise Exception("Bot paused.")
        if (self.mailer.get_current_message() == "Stop"):
            self.mailer.send("Bot stopped.")
            raise Exception("Bot stopped.")

        try:
            username_field = self.browser.find_element_by_name("username")
            username_field.send_keys(self.username)
            password_field = self.browser.find_element_by_name("password")
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            sleep(10)
            return
        except KeyboardInterrupt:
            return
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.login')
            sleep(1)
            self.login()
            return

    # Comments on a picture
    def comment(self, topic):
        sleep(3)
        query = Config.comments[randint(0, len(Config.comments) - 1)]
        say = query.format(self.author(), Config.smileys[randint(0, len(Config.smileys) - 1)])
        try:
            comment_field = self.browser.find_element_by_xpath(Config.comment_xpath)
            comment_field.send_keys(say)
            comment_field.send_keys(Keys.RETURN)
            self.mailer.send("Commented on " + str(self.author()) + "s picture with: " + say + "\n")
            print("Commented on " + str(self.author()) + "s picture with: " + say)

            if self.author() not in self.actionList.keys():
                value = {"type": "comment", "time": self.timestamp(), "topic": topic}
                self.actionList[self.author()] = [value]
            else:
                value = {"type": "comment", "time": self.timestamp(), "topic": topic}
                authorActions = self.actionList[self.author()]
                authorActions.append(value)
                self.actionList[self.author()] = authorActions
            with open(Config.bot_path + "log/actionList.pickle", "wb") as userfile:
                pickle.dump(self.actionList, userfile)

            sleep(1)
        except KeyboardInterrupt:
            return
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.comment')
            self.mailer.send("Comment field not found.\n")
            print("Comment field not found.")

    # Searches for a certain topic
    def search(self, query):
        self.mailer.send("Searching for " + query + ".")
        print("Searching for " + query + ".")
        self.browser.get("https://www.instagram.com/explore/tags/" + query + "/")

    # Checks for error which occurs when pictures are removed while
    # switching through
    def error(self):
        try:
            error_message = self.browser.find_element_by_xpath(Config.error_xpath)
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Page loading error')
            print("Page loading error.")
            return True
        except KeyboardInterrupt:
            return
        except:
            return False

    # Selects the first picture in a loaded topic screen
    def select_first(self):
        try:
            pictures = self.browser.find_elements_by_xpath(Config.first_ele_xpath)
            print("Found " + str(len(pictures)) + " pictures.")
            first_picture = None
            if len(pictures) > 9:
                first_picture = pictures[9]
            else:
                first_picture = pictures[len(pictures) - 1]
            self.focus(first_picture)
            first_picture.click()
            sleep(1)
            return True
        except KeyboardInterrupt:
            return
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.select_first')
            sleep(5)
            return False

    # Switches to the next picture
    def next_picture(self):
        try:
            sleep(1)
            next_button = self.browser.find_element_by_xpath(Config.next_button_xpath)
            next_button.click()
            return
        except KeyboardInterrupt:
            return
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.next_picture')
            self.browser.execute_script("window.history.go(-1)")
            sleep(5)
            self.select_first()
            sleep(1)

    # Loads the authors name
    def author(self):
        try:
            author = self.browser.find_element_by_xpath(Config.author_xpath)
            return str(author.get_attribute("title"))
        except KeyboardInterrupt:
            return
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.author')
            self.mailer.send("Author xpath not found.\n")
            print("Author xpath not found.")
            return ""

    # Checks if the post is already liked
    def already_liked(self):
        try:
            full = self.browser.find_element_by_xpath(Config.like_button_full_xpath)
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Image was already liked.')
            return True
        except:
            return False

    def on_post_page(self):
        try:
            full = self.browser.find_element_by_xpath(Config.next_button_xpath)
            return False
        except:
            return True

    # Likes a picture
    def like(self, topic):
        count = 0
        while self.already_liked() and count < 10:
            self.mailer.send("Post already liked. Skipping.\n")
            print("Post already liked. Skipping.")
            self.next_picture()
            if self.on_post_page():
                self.browser.save_screenshot(Config.bot_path + 'log/error.png')
                self.mailer.send_image(Config.bot_path + 'log/error.png', 'Accidently swapped to post page.')
                return
            count = count + 1
            sleep(1)
        try:
            self.mailer.send("Liked picture/video by: " + self.author() + ".\n")
            print("Liked picture/video by: " + self.author() + ".")

            if self.author() not in self.actionList.keys():
                value = {"type": "like", "time": self.timestamp(), "topic": topic}
                self.actionList[self.author()] = [value]
            else:
                value = {"type": "like", "time": self.timestamp(), "topic": topic}
                authorActions = self.actionList[self.author()]
                authorActions.append(value)
                self.actionList[self.author()] = authorActions
            with open(Config.bot_path + "log/actionList.pickle", "wb") as userfile:
                pickle.dump(self.actionList, userfile)

            like_button = self.browser.find_element_by_xpath(Config.like_button_xpath)
            like_button.click()
            sneaksleep = randint(0, 10) + Config.delay
            sleep(sneaksleep)
            return
        except KeyboardInterrupt:
            return
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.like')
            sleep(Config.delay)
            self.search(topic)
            self.select_first()
            self.like(topic)
            return

    # Unfollows a user
    def unfollow(self, name):
        self.browser.get("https://www.instagram.com/" + name + "/")
        sleep(3)
        try:
            unfollow_button = self.browser.find_element_by_xpath(Config.unfollow_xpath)
            unfollow_button.click()
            self.mailer.send("Unfollowed: " + name + ".\n")
            print("Unfollowed: " + name)
            sleep(2)
        except KeyboardInterrupt:
            return
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.unfollow')
            self.mailer.send("Unfollow button not found.\n")
            print("Unfollow button not found.")
            sleep(1)

    # Follows a user
    def follow(self, topic):
        sleep(3)
        try:
            follow = self.browser.find_element_by_xpath(Config.follow_xpath)
            follow.click()
            self.mailer.send("Followed: " + self.author() + "\n")
            print("Followed: " + self.author())
            with open(Config.bot_path + "log/followed_users.pickle", "wb") as userfile:
                pickle.dump(self.accounts_to_unfollow, userfile)

            if self.author() not in self.actionList.keys():
                value = {"type": "follow", "time": self.timestamp(), "topic": topic}
                self.actionList[self.author()] = [value]
            else:
                value = {"type": "follow", "time": self.timestamp(), "topic": topic}
                authorActions = self.actionList[self.author()]
                authorActions.append(value)
                self.actionList[self.author()] = authorActions
            with open(Config.bot_path + "log/actionList.pickle", "wb") as userfile:
                pickle.dump(self.actionList, userfile)

            self.accounts_to_unfollow.append(self.author())
            self.followed_accounts.update({self.author(): self.timestamp()})
            with open(Config.bot_path + "log/followed_users_all_time.pickle", "wb") as userfile:
                pickle.dump(self.followed_accounts, userfile)
            sleep(Config.delay + randint(0, 10))
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.follow')
            self.mailer.send("Follow button not found.\n")
            print("Follow button not found.")
            sleep(1)

    def open_unfollow_screen(self):
        self.browser.get(Config.account_url)
        sleep(2)
        heart = self.browser.find_element_by_xpath(Config.following_xpath)
        heart.click()
        sleep(2)

    def check_follows(self):
        try:
            sections = self.browser.find_elements_by_xpath(Config.sections_xpath)
            print(str(len(sections)) + " Sections found.")
        except:
            print("Sections not found.")
            return
        users = []
        for element in sections:
            profile = element.find_element_by_xpath(Config.local_name_xpath)
            name = profile.get_attribute("title")
            users.append(name)
        for user in users:
            if user not in self.interacting_users:
                if user not in self.actionList.keys():
                    self.mailer.send(
                        "New interaction discovered with: " + user + ", but we have no further information.")
                    sleep(1)
                else:
                    actions = self.actionList[user]
                    self.mailer.send(
                        "New interaction discovered with: " + user + ", and we have logged our interactions on him:")
                    sleep(1)
                    string = ""
                    for action in actions:
                        string += "Type: " + action["type"] + ", Time: " + action["time"] + ", Topic: " + action[
                            "topic"] + " ... "
                        self.hashtags[action["topic"]] += 1
                    self.mailer.send(string)
                    sleep(1)
                self.interacting_users.append(user)
                with open(Config.bot_path + "log/interacting_users.pickle", "wb") as userfile:
                    pickle.dump(self.interacting_users, userfile)
        return

    def store_hashtags(self):
        try:
            sections = self.browser.find_elements_by_xpath(Config.hashtags_xpath)
            for section in sections:
                all_hashtags = self.extract_hash_tags(section.text)
                for h in all_hashtags:
                    if h in self.hashtags:
                        self.hashtags[h] = self.hashtags[h] + 0.01
                    else:
                        self.hashtags[h] = 0.01
            with open(Config.bot_path + "log/hashtags.pickle", "wb") as f:
                pickle.dump(self.hashtags, f)
        except:
            self.browser.save_screenshot(Config.bot_path + 'log/error.png')
            self.mailer.send_image(Config.bot_path + 'log/error.png', 'Exception in self.store_hashtags')
            pass

    def extract_hash_tags(self, s):
        return set(part[1:] for part in s.split() if part.startswith('#'))

    # Coordinates every function in an endless loop
    def like_follow_loop(self):
        self.login()
        while True:
            self.open_unfollow_screen()
            self.check_follows()

            top_hashtags = sorted(self.hashtags.keys(), key=lambda k: self.hashtags[k], reverse=True)[:20]
            top_hashtags_values = []
            for hashtag in top_hashtags:
                top_hashtags_values.append(self.hashtags[hashtag])
            self.mailer.send_stats(top_hashtags_values, top_hashtags, caption="Top 20 hashtags")
            low_hashtags = sorted(self.hashtags.keys(), key=lambda k: self.hashtags[k], reverse=True)[-20:]
            low_hashtags_values = []
            for hashtag in low_hashtags:
                low_hashtags_values.append(self.hashtags[hashtag])
            self.mailer.send_stats(low_hashtags_values, low_hashtags, caption="Low 20 hashtags")
            sleep(1)

            for topic_selector in range(len(top_hashtags) - 1):
                if (
                                    self.mailer.get_current_message() == "Exit" or self.mailer.get_current_message() == "Pause" or self.mailer.get_current_message() == "Stop"):
                    raise Exception('Breaking out of inner loop')
                self.search(top_hashtags[topic_selector])
                print("Selecting first picture.")
                self.select_first()
                if topic_selector % 7 == 2:
                    if (
                                        self.mailer.get_current_message() == "Exit" or self.mailer.get_current_message() == "Pause" or self.mailer.get_current_message() == "Stop"):
                        raise Exception('Breaking out of inner loop')
                    if not self.error():
                        self.comment(top_hashtags[topic_selector])
                        self.store_hashtags()
                        self.next_picture()
                for likes in range(3):
                    sleep(1)
                    if (
                                        self.mailer.get_current_message() == "Exit" or self.mailer.get_current_message() == "Pause" or self.mailer.get_current_message() == "Stop"):
                        raise Exception('Breaking out of inner loop')
                    if not self.error():
                        self.like(top_hashtags[topic_selector])
                        self.store_hashtags()
                        self.next_picture()
                for follows in range(3):
                    sleep(1)
                    if not self.error():
                        if (
                                            self.mailer.get_current_message() == "Exit" or self.mailer.get_current_message() == "Pause" or self.mailer.get_current_message() == "Stop"):
                            raise Exception('Breaking out of inner loop')
                        self.next_picture()
                        count = 0
                        sleep(3)
                        while self.user_followed_already(self.author()) and count < 10:
                            if (
                                                self.mailer.get_current_message() == "Exit" or self.mailer.get_current_message() == "Pause" or self.mailer.get_current_message() == "Stop"):
                                raise Exception('Breaking out of inner loop')
                            self.mailer.send(self.author() + " was followed already. Skipping picture.")
                            print(self.author() + " was followed already. Skipping picture.")
                            self.next_picture()
                            count = count + 1
                            sleep(1)
                        self.follow(top_hashtags[topic_selector])
                        self.store_hashtags()
                self.mailer.send("Accounts to unfollow: " + str(len(self.accounts_to_unfollow)))
                print("Accounts to unfollow: " + str(len(self.accounts_to_unfollow)))
                if len(self.accounts_to_unfollow) > 50:
                    for unfollows in range(3):
                        if (
                                            self.mailer.get_current_message() == "Exit" or self.mailer.get_current_message() == "Pause" or self.mailer.get_current_message() == "Stop"):
                            raise Exception('Breaking out of inner loop')
                        this_guy = self.accounts_to_unfollow[0]
                        self.unfollow(this_guy)
                        del self.accounts_to_unfollow[0]
