import threading

import os
from selenium import webdriver  # For webpage crawling
from time import sleep
import time
from selenium.webdriver.common.keys import Keys  # For input processing
from random import randint
import pickle  # For data management

from carnivora.instabot.config import Config
from carnivora.instabot.log import Log

from tf_open_nsfw.classify_nsfw import classify_nsfw

if Config.headless_is_available:
    from xvfbwrapper import Xvfb


class Driver(threading.Thread):
    def __init__(self, username, password):

        self.username = username
        self.password = password

        # Set up virtual display
        if Config.headless_is_available:
            self.display = Xvfb()
            self.display.start()

        log_path = Config.bot_path + "log/" + username

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        self.interacting_users_path = log_path + "/interacting_users.pickle"
        self.hashtags_path = log_path + "/hashtags.pickle"
        self.action_list_path = log_path + "/action_list.pickle"
        self.followed_users_all_time_path = log_path + "/followed_users_all_time.pickle"
        self.accounts_to_unfollow_path = log_path + "/accounts_to_unfollow.pickle"
        self.log_path = log_path + "/log.pickle"
        self.running_path = log_path + "/running.pickle"

        try:
            with open(self.interacting_users_path, "rb") as f:
                self.interacting_users = pickle.load(f)
        except:
            with open(self.interacting_users_path, "wb") as f:
                self.interacting_users = []
                pickle.dump([], f)
        try:
            with open(self.hashtags_path, "rb") as f:
                self.hashtags = pickle.load(f)
        except:
            with open(self.hashtags_path, "wb") as f:
                self.hashtags = {}
                for h in Config.topics:
                    self.hashtags[h] = 2
                pickle.dump(self.hashtags, f)
        try:
            with open(self.action_list_path, "rb") as f:
                self.action_list = pickle.load(f)
        except:
            with open(self.action_list_path, "wb") as f:
                self.action_list = {}
                pickle.dump({}, f)
        try:
            with open(self.followed_users_all_time_path, "rb") as f:
                self.followed_accounts = pickle.load(f)
        except:
            with open(self.followed_users_all_time_path, "wb") as f:
                self.followed_accounts = {}
                pickle.dump({}, f)
        try:
            with open(self.accounts_to_unfollow_path, "rb") as f:
                self.accounts_to_unfollow = pickle.load(f)
        except:
            with open(self.accounts_to_unfollow_path, "wb") as f:
                self.accounts_to_unfollow = []
                pickle.dump([], f)

        # Final setup
        if Config.headless_is_available:
            # self.browser = webdriver.PhantomJS(desired_capabilities=dcap)
            self.browser = webdriver.PhantomJS()

        else:
            self.browser = webdriver.Chrome(Config.bot_path + "/chromedriver")
        self.browser.set_window_size(1980, 1080)

        super(Driver, self).__init__()

    def start(self):
        super(Driver, self).start()

    def running(self):
        try:
            with open(self.running_path, "rb") as f:
                return bool(pickle.load(f))
        except Exception as e:
            print(e)
            return False

    def timestamp(self):
        return time.strftime('%a %H:%M:%S') + " "

    def focus(self, element):
        if self.running():
            self.browser.execute_script("arguments[0].focus();", element)

    def user_followed_already(self, user):
        if self.running():
            if user in self.followed_accounts:
                return True
            else:
                return False

    def login(self):
        if self.running():
            Log.update(logpath=self.log_path, text="Logging in")
            self.browser.get(Config.start_url)
            sleep(5)

            if self.browser.current_url == "https://www.instagram.com/":
                return

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
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.login: ' + str(e))
                sleep(1)
                self.login()
                return

    # Comments on a picture
    def comment(self, topic):
        if self.running():
            sleep(3)
            query = Config.comments[randint(0, len(Config.comments) - 1)]
            say = query.format(self.author(), Config.smileys[randint(0, len(Config.smileys) - 1)])
            try:
                comment_field = self.browser.find_element_by_xpath(Config.comment_xpath)
                comment_field.send_keys(say)
                comment_field.send_keys(Keys.RETURN)
                Log.update(logpath=self.log_path, text="Commented on " + str(self.author()) + "s picture with: " + say + "\n")

                if self.author() not in self.action_list.keys():
                    value = {"type": "comment", "time": self.timestamp(), "topic": topic}
                    self.action_list[self.author()] = [value]
                else:
                    value = {"type": "comment", "time": self.timestamp(), "topic": topic}
                    author_actions = self.action_list[self.author()]
                    author_actions.append(value)
                    self.action_list[self.author()] = author_actions
                with open(self.action_list_path, "wb") as userfile:
                    pickle.dump(self.action_list, userfile)

                sleep(1)
            except KeyboardInterrupt:
                return
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.comment: ' + str(e))

    # Searches for a certain topic
    def search(self, query):
        if self.running():
            Log.update(logpath=self.log_path, text="Searching for " + query + ".")
            self.browser.get("https://www.instagram.com/explore/tags/" + query + "/")

    # Checks for error which occurs when pictures are removed while
    # switching through
    def error(self):
        if self.running():
            sleep(1)
            try:
                error_message = self.browser.find_element_by_xpath(Config.error_xpath)
                Log.update(logpath=self.log_path, text='Page loading error: ' + str(error_message))
                return True
            except KeyboardInterrupt:
                return
            except:
                return False

    # Selects the first picture in a loaded topic screen
    def select_first(self):
        if self.running():
            try:
                pictures = self.browser.find_elements_by_xpath(Config.first_ele_xpath)
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
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.select_first: ' + str(e))
                sleep(5)
                return False

    # Switches to the next picture
    def next_picture(self):
        if self.running():
            try:
                sleep(5)
                next_button = self.browser.find_element_by_xpath(Config.next_button_xpath)
                next_button.click()
                return
            except KeyboardInterrupt:
                return
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.next_picture: ' + str(e))
                self.browser.execute_script("window.history.go(-1)")
                sleep(5)
                self.select_first()
                sleep(1)

    # Loads the authors name
    def author(self):
        if self.running():
            try:
                author = self.browser.find_element_by_xpath(Config.author_xpath)
                return str(author.get_attribute("title"))
            except KeyboardInterrupt:
                return
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.author: ' + str(e))
                return ""

    # Checks if the post is already liked
    def already_liked(self):
        if self.running():
            try:
                _ = self.browser.find_element_by_xpath(Config.like_button_full_xpath)
                Log.update(logpath=self.log_path, text='Image was already liked.')
                return True
            except:
                return False

    def on_post_page(self):
        if self.running():
            try:
                _ = self.browser.find_element_by_xpath(Config.next_button_xpath)
                return False
            except:
                return True

    # Likes a picture
    def like(self, topic):
        if self.running():
            try:
                like_button = self.browser.find_element_by_xpath(Config.like_button_xpath)
                like_button.click()

                src = self.extract_picture_source()

                Log.update(logpath=self.log_path, text="Liked picture/video by: " + self.author() + ".\n", image=src)

                if self.author() not in self.action_list.keys():
                    value = {"type": "like", "time": self.timestamp(), "topic": topic}
                    self.action_list[self.author()] = [value]
                else:
                    value = {"type": "like", "time": self.timestamp(), "topic": topic}
                    author_actions = self.action_list[self.author()]
                    author_actions.append(value)
                    self.action_list[self.author()] = author_actions
                with open(self.action_list_path, "wb") as userfile:
                    pickle.dump(self.action_list, userfile)

                sleep(randint(0, 10) + Config.delay)
                return
            except KeyboardInterrupt:
                return
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.like: ' + str(e))
                sleep(Config.delay)
                self.search(topic)
                self.select_first()
                self.like(topic)
                return

    # Unfollows a user
    def unfollow(self, name):
        if self.running():
            self.browser.get("https://www.instagram.com/" + name + "/")
            sleep(3)
            try:
                unfollow_button = self.browser.find_element_by_xpath(Config.unfollow_xpath)
                unfollow_button.click()
                sleep(2)
            except KeyboardInterrupt:
                return
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.unfollow: ' + str(e))
                sleep(1)

    # Follows a user
    def follow(self, topic):
        if self.running():
            sleep(3)
            try:
                follow = self.browser.find_element_by_xpath(Config.follow_xpath)
                follow.click()
                Log.update(logpath=self.log_path, text="Followed: " + self.author())
                with open(self.accounts_to_unfollow_path, "wb") as userfile:
                    pickle.dump(self.accounts_to_unfollow, userfile)

                if self.author() not in self.action_list.keys():
                    value = {"type": "follow", "time": self.timestamp(), "topic": topic}
                    self.action_list[self.author()] = [value]
                else:
                    value = {"type": "follow", "time": self.timestamp(), "topic": topic}
                    author_actions = self.action_list[self.author()]
                    author_actions.append(value)
                    self.action_list[self.author()] = author_actions
                with open(self.action_list_path, "wb") as userfile:
                    pickle.dump(self.action_list, userfile)

                self.accounts_to_unfollow.append(self.author())
                self.followed_accounts.update({self.author(): self.timestamp()})
                with open(self.followed_users_all_time_path, "wb") as userfile:
                    pickle.dump(self.followed_accounts, userfile)
                sleep(Config.delay + randint(0, 10))
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.follow: ' + str(e))
                sleep(1)

    def open_unfollow_screen(self):
        if self.running():
            self.browser.get(Config.account_url.format(self.username))
            sleep(2)
            heart = self.browser.find_element_by_xpath(Config.following_xpath)
            heart.click()
            sleep(2)

    def check_follows(self):
        if self.running():
            try:
                sections = self.browser.find_elements_by_xpath(Config.sections_xpath)
            except Exception as e:
                Log.update(logpath=self.log_path, text="Exception in check_follows: " + str(e))
                return
            users = []
            for element in sections:
                profile = element.find_element_by_xpath(Config.local_name_xpath)
                name = profile.get_attribute("title")
                users.append(name)
            for user in users:
                if user not in self.interacting_users:
                    if user not in self.action_list.keys():
                        Log.update(logpath=self.log_path,
                            text="New interaction discovered with: " + user + ", but we have no further information.")
                        sleep(1)
                    else:
                        actions = self.action_list[user]
                        Log.update(logpath=self.log_path,
                            text="New interaction discovered with: " + user + ", and we have logged our interactions on him:")
                        sleep(1)
                        string = ""
                        for action in actions:
                            string += "Type: " + action["type"] + ", Time: " + action["time"] + ", Topic: " + action[
                                "topic"] + " ... "
                            self.hashtags[action["topic"]] += 1
                        Log.update(logpath=self.log_path, text=string)
                        sleep(1)
                    self.interacting_users.append(user)
                    with open(self.interacting_users_path, "wb") as userfile:
                        pickle.dump(self.interacting_users, userfile)
            return

    def store_hashtags(self):
        if self.running():
            try:
                sections = self.browser.find_elements_by_xpath(Config.hashtags_xpath)
                for section in sections:
                    all_hashtags = self.extract_hash_tags(section.text)
                    for h in all_hashtags:
                        if h in self.hashtags:
                            self.hashtags[h] = self.hashtags[h] + 0.01
                        else:
                            self.hashtags[h] = 0.01
                with open(self.hashtags_path, "wb") as f:
                    pickle.dump(self.hashtags, f)
            except Exception as e:
                Log.update(logpath=self.log_path, text='Exception in self.store_hashtags: ' + str(e))

    def extract_hash_tags(self, s):
        if self.running():
            return set(part[1:] for part in s.split() if part.startswith('#'))

    def extract_picture_source(self):
        if self.running():
            try:
                sections = self.browser.find_elements_by_xpath(Config.image_div_container_xpath)
                for section in sections:
                    image = section.find_element_by_tag_name("img")
                    return image.get_attribute("src")
            except Exception as e:
                Log.update(logpath=self.log_path, text='Picture could not be extracted: ' + str(e))
            return ""

    def post_is_sfw(self):
        if self.running():
            image_url = self.extract_picture_source()
            if image_url == "" or image_url is None:
                return True
            sfw, nsfw = classify_nsfw(image_url)
            Log.update(logpath=self.log_path, text="Analysis of this post yielded it to be {}% NSFW.".format(int(100 * nsfw)),
                       image=image_url)
            return nsfw < sfw

    def run(self):
        self.login()
        while self.running:
            self.open_unfollow_screen()
            self.check_follows()

            top_hashtags = sorted(self.hashtags.keys(), key=lambda k: self.hashtags[k], reverse=True)[:20]
            top_hashtags_values = []
            for hashtag in top_hashtags:
                top_hashtags_values.append(self.hashtags[hashtag])

            for topic_selector in range(len(top_hashtags) - 1):

                self.search(top_hashtags[topic_selector])
                self.select_first()
                if topic_selector % 7 == 2:
                    if not self.error():
                        if self.post_is_sfw():
                            self.comment(top_hashtags[topic_selector])
                            self.store_hashtags()
                        self.next_picture()
                for likes in range(3):
                    if not self.error():
                        count = 0
                        while self.already_liked() and count < 10:
                            Log.update(logpath=self.log_path, text="Post already liked. Skipping.")
                            self.next_picture()
                            if self.on_post_page():
                                Log.update(logpath=self.log_path, text='Accidently swapped to post page.')
                                return
                            count += 1
                            sleep(1)
                        if self.post_is_sfw():
                            self.like(top_hashtags[topic_selector])
                            self.store_hashtags()
                        self.next_picture()
                for follows in range(3):
                    if not self.error():
                        self.next_picture()
                        count = 0
                        while self.user_followed_already(self.author()) and count < 10:
                            Log.update(logpath=self.log_path, text=self.author() + " was followed already. Skipping picture.")
                            self.next_picture()
                            count += 1
                            sleep(1)
                        if self.post_is_sfw():
                            self.follow(top_hashtags[topic_selector])
                            self.store_hashtags()

                if len(self.accounts_to_unfollow) > 50:
                    for unfollows in range(3):
                        this_guy = self.accounts_to_unfollow[0]
                        self.unfollow(this_guy)
                        del self.accounts_to_unfollow[0]
        super(Driver, self).join()
