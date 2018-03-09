import threading

import os
from selenium import webdriver  # For webpage crawling
from time import sleep
import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # For input processing
from random import randint, shuffle
import pickle  # For data management

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from carnivora.instabot.config import Config
from carnivora.instabot.log import Log

from tf_open_nsfw.classify_nsfw import classify_nsfw

if Config.headless_is_available:
    from xvfbwrapper import Xvfb


class Driver(threading.Thread):
    def __init__(
            self,
            username,
            password,
            window_width=1920,
            window_height=1080,
            headless_is_available=Config.headless_is_available,
    ):

        self.username = username
        self.password = password

        # Set up virtual display
        if headless_is_available:
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
        except FileNotFoundError:
            with open(self.interacting_users_path, "wb") as f:
                self.interacting_users = []
                pickle.dump([], f)
        try:
            with open(self.hashtags_path, "rb") as f:
                self.hashtags = pickle.load(f)
        except FileNotFoundError:
            with open(self.hashtags_path, "wb") as f:
                self.hashtags = {}
                for h in Config.topics:
                    self.hashtags[h] = 2
                pickle.dump(self.hashtags, f)
        try:
            with open(self.action_list_path, "rb") as f:
                self.action_list = pickle.load(f)
        except FileNotFoundError:
            with open(self.action_list_path, "wb") as f:
                self.action_list = {}
                pickle.dump({}, f)
        try:
            with open(self.followed_users_all_time_path, "rb") as f:
                self.followed_accounts = pickle.load(f)
        except FileNotFoundError:
            with open(self.followed_users_all_time_path, "wb") as f:
                self.followed_accounts = {}
                pickle.dump({}, f)
        try:
            with open(self.accounts_to_unfollow_path, "rb") as f:
                self.accounts_to_unfollow = pickle.load(f)
        except FileNotFoundError:
            with open(self.accounts_to_unfollow_path, "wb") as f:
                self.accounts_to_unfollow = []
                pickle.dump([], f)

        if Config.headless_is_available:
            self.browser = webdriver.PhantomJS()
        else:
            self.browser = webdriver.Chrome(Config.bot_path + "/chromedriver")
        self.browser.set_window_size(window_width, window_height)

        super(Driver, self).__init__()

    def start(self):
        super(Driver, self).start()

    def running(self):
        try:
            with open(self.running_path, "rb") as f:
                return bool(pickle.load(f))
        except FileNotFoundError:
            return False

    @staticmethod
    def timestamp():
        return time.strftime('%a %H:%M:%S') + " "

    def focus(self, element, browser):
        if self.running():
            browser.execute_script("arguments[0].focus();", element)

    def user_followed_already(self, user):
        if self.running():
            return user in self.followed_accounts

    def login(self, username, password, browser, log_path, timeout=100):
        if self.running():
            Log.update(log_path=log_path, text="Logging in")
            browser.get(Config.start_url)
            try:
                username_field = WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                pass_field = WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
            except TimeoutException as e:
                Log.update(log_path=log_path, text='Exception in self.login: ' + str(e))
                raise e
            username_field.send_keys(username)
            pass_field.send_keys(password)
            pass_field.send_keys(Keys.RETURN)

            Log.update(log_path=log_path, text="Logged in")

    def update_action_list(self, author, action_type, topic):
        if author not in self.action_list.keys():
            value = {"type": action_type, "time": Driver.timestamp(), "topic": topic}
            self.action_list[author] = [value]
        else:
            value = {"type": action_type, "time": Driver.timestamp(), "topic": topic}
            author_actions = self.action_list[author]
            author_actions.append(value)
            self.action_list[author] = author_actions

        with open(self.action_list_path, "wb") as f:
            pickle.dump(self.action_list, f)

    def comment(self, topic, browser, log_path, timeout=100):
        if self.running():
            author = self.author(browser=browser, log_path=log_path)
            query = Config.comments[randint(0, len(Config.comments) - 1)]
            say = query.format(author, Config.smileys[randint(0, len(Config.smileys) - 1)])
            try:
                comment_field = WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.comment_xpath))
                )
            except TimeoutException as e:
                Log.update(log_path=log_path, text='Exception in self.comment: ' + str(e))
                raise e
            comment_field.send_keys(say)
            comment_field.send_keys(Keys.RETURN)
            Log.update(log_path=log_path, text="Commented on "+str(author)+"s picture with: "+say)
            self.update_action_list(author=author, action_type="comment", topic=topic)

    def search(self, browser, log_path, query):
        if self.running():
            browser.get("https://www.instagram.com/explore/tags/" + query + "/")
            Log.update(log_path=log_path, text="Searching for " + query + ".")

    def error(self, browser, log_path, error_timeout=1):
        if self.running():
            try:
                error_message = WebDriverWait(browser, error_timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.error_xpath))
                )
                Log.update(log_path=log_path, text='Page loading error: ' + str(error_message))
                return True
            except TimeoutException:
                return False

    # Selects the first picture in a loaded topic screen
    def select_first(self, browser, log_path, timeout=100):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.first_ele_xpath))
                )
                pictures = browser.find_elements_by_xpath(Config.first_ele_xpath)
            except (TimeoutException, NoSuchElementException) as e:
                Log.update(log_path=log_path, text='Exception in self.select_first: ' + str(e))
                raise e
            if len(pictures) > 9:
                first_picture = pictures[9]
            else:
                first_picture = pictures[len(pictures) - 1]
            self.focus(first_picture, browser=browser)
            first_picture.click()

    def next_picture(self, browser, log_path, timeout=100):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.next_button_xpath))
                )
                next_button = WebDriverWait(browser, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, Config.next_button_xpath))
                )
            except TimeoutException as e:
                Log.update(log_path=log_path, text='Exception in self.next_picture: ' + str(e))
                raise e
            next_button.click()

    def author(self, browser, log_path, timeout=100):
        if self.running():
            try:
                author_element = WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.author_xpath))
                )
            except TimeoutException as e:
                Log.update(log_path=log_path, text='Exception in self.author: ' + str(e))
                raise e
            return str(author_element.get_attribute("title"))

    # Checks if the post is already liked
    def already_liked(self, browser, log_path, error_timeout=5):
        if self.running():
            try:
                WebDriverWait(browser, error_timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.like_button_full_xpath))
                )
            except TimeoutException:
                return False
            Log.update(log_path=log_path, text='Image was already liked.')
            return True

    # Likes a picture
    def like(self, browser, log_path, topic, timeout=100):
        if self.running():
            author = self.author(browser=browser, log_path=log_path)
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.like_button_xpath))
                )
                like_button = WebDriverWait(browser, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, Config.like_button_xpath))
                )
            except TimeoutException as e:
                Log.update(log_path=log_path, text='Exception in self.like: ' + str(e))
                raise e
            like_button.click()
            src = self.extract_picture_source(browser=browser, log_path=log_path)
            Log.update(log_path=log_path, text="Liked picture/video by: "+author, image=src)
            self.update_action_list(author=author, action_type="like", topic=topic)

    # Unfollows a user
    def unfollow(self, browser, log_path, name, timeout=100):
        if self.running():
            browser.get("https://www.instagram.com/" + name + "/")
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.unfollow_xpath))
                )
                unfollow_button = WebDriverWait(browser, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, Config.unfollow_xpath))
                )
            except TimeoutException as e:
                Log.update(log_path=log_path, text='Exception in self.like: ' + str(e))
                raise e
            unfollow_button.click()

    def update_accounts_to_unfollow(self, author):
        self.accounts_to_unfollow.append(author)
        with open(self.accounts_to_unfollow_path, "wb") as f:
            pickle.dump(self.accounts_to_unfollow, f)

    def update_followed_accounts(self, author):
        self.followed_accounts.update({author: Driver.timestamp()})
        with open(self.followed_users_all_time_path, "wb") as userfile:
            pickle.dump(self.followed_accounts, userfile)

    # Follows a user
    def follow(self, browser, log_path, topic, timeout=100):
        if self.running():
            author = self.author(browser=browser, log_path=log_path)
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.follow_xpath))
                )
                follow_button = WebDriverWait(browser, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, Config.follow_xpath))
                )
            except TimeoutException as e:
                Log.update(log_path=log_path, text='Exception in self.like: ' + str(e))
                raise e
            follow_button.click()
            Log.update(log_path=self.log_path, text="Followed: " + author)
            self.update_action_list(author=author, action_type="follow", topic=topic)
            self.update_accounts_to_unfollow(author=author)
            self.update_followed_accounts(author=author)

    def open_unfollow_screen(self, browser, log_path, timeout=100):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.following_xpath))
                )
                heart = WebDriverWait(browser, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, Config.following_xpath))
                )
            except TimeoutException as e:
                Log.update(log_path=log_path, text='Exception in self.open_unfollow_screen: ' + str(e))
                raise e
            heart.click()

    def update_interacting_users(self, user):
        self.interacting_users.append(user)
        with open(self.interacting_users_path, "wb") as f:
            pickle.dump(self.interacting_users, f)

    def check_follows(self, browser, log_path, timeout=100):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.sections_xpath))
                )
                sections = browser.find_elements_by_xpath(Config.sections_xpath)
            except (TimeoutException, NoSuchElementException) as e:
                Log.update(log_path=log_path, text='Exception in self.check_follows: ' + str(e))
                raise e

            users = []

            for element in sections:
                try:
                    profile = element.find_element_by_xpath(Config.local_name_xpath)
                except NoSuchElementException as e:
                    Log.update(log_path=log_path, text='Exception in self.check_follows: ' + str(e))
                    raise e
                name = profile.get_attribute("title")
                users.append(name)

            for user in users:
                if user not in self.interacting_users:
                    if user in self.action_list.keys():
                        actions = self.action_list[user]
                        for action in actions:
                            self.hashtags[action["topic"]] += 1
                        self.update_interacting_users(user=user)

    def update_hashtags(self, hashtag, boost=0.1):
        if hashtag in self.hashtags:
            self.hashtags[hashtag] += boost
        else:
            self.hashtags[hashtag] = boost
        with open(self.hashtags_path, "wb") as f:
            pickle.dump(self.hashtags, f)

    def store_hashtags(self, browser, log_path, timeout=100):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.hashtags_xpath))
                )
                sections = browser.find_elements_by_xpath(Config.hashtags_xpath)
            except (TimeoutException, NoSuchElementException) as e:
                Log.update(log_path=log_path, text='Exception in self.store_hashtags: ' + str(e))
                raise e
            for section in sections:
                all_hashtags = self.extract_hash_tags(section.text)
                for hashtag in all_hashtags:
                    self.update_hashtags(hashtag=hashtag)

    def extract_hash_tags(self, s):
        if self.running():
            return set(part[1:] for part in s.split() if part.startswith('#'))

    def extract_picture_source(self, browser, log_path, timeout=100):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, Config.image_div_container_xpath))
                )
                sections = browser.find_elements_by_xpath(Config.image_div_container_xpath)
            except (TimeoutException, NoSuchElementException) as e:
                Log.update(log_path=log_path, text='Exception in self.extract_picture_source: ' + str(e))
                raise e
            for section in sections:
                try:
                    image = section.find_element_by_tag_name("img")
                except NoSuchElementException as e:
                    Log.update(log_path=log_path, text='Exception in self.extract_picture_source: ' + str(e))
                    raise e
                return image.get_attribute("src")

    def post_is_sfw(self, browser, log_path):
        if self.running():
            image_url = self.extract_picture_source(browser=browser, log_path=log_path)
            if image_url == "" or image_url is None:
                return True
            sfw, nsfw = classify_nsfw(image_url)
            Log.update(
                log_path=self.log_path,
                text="Analysis of this post yielded it to be {}% NSFW.".format(int(100 * nsfw)),
                image=image_url
            )
            return nsfw < sfw

    def run(self):
        self.login(browser=self.browser, log_path=self.log_path, password=self.password, username=self.username)
        while self.running:
            self.open_unfollow_screen(browser=self.browser, log_path=self.log_path)
            self.check_follows(browser=self.browser, log_path=self.log_path)

            top_hashtags = shuffle(sorted(self.hashtags.keys(), key=lambda k: self.hashtags[k], reverse=True)[:20])

            for topic_selector in range(len(top_hashtags) - 1):

                self.search(query=top_hashtags[topic_selector], browser=self.browser, log_path=self.log_path)
                self.select_first(browser=self.browser, log_path=self.log_path)
                for comments in range(1):
                    if not self.error(browser=self.browser, log_path=self.log_path):
                        if self.post_is_sfw(browser=self.browser, log_path=self.log_path):
                            self.comment(
                                topic=top_hashtags[topic_selector],
                                browser=self.browser,
                                log_path=self.log_path
                            )
                            self.store_hashtags(browser=self.browser, log_path=self.log_path)
                            sleep(Config.delay)
                        self.next_picture(browser=self.browser, log_path=self.log_path)
                for likes in range(3):
                    if not self.error(browser=self.browser, log_path=self.log_path):
                        while self.already_liked(browser=self.browser, log_path=self.log_path):
                            Log.update(log_path=self.log_path, text="Post already liked. Skipping.")
                            self.next_picture(browser=self.browser, log_path=self.log_path)

                        if self.post_is_sfw(browser=self.browser, log_path=self.log_path):
                            self.like(topic=top_hashtags[topic_selector], browser=self.browser, log_path=self.log_path)
                            sleep(Config.delay)
                            self.store_hashtags(browser=self.browser, log_path=self.log_path)

                        self.next_picture(browser=self.browser, log_path=self.log_path)
                for follows in range(2):
                    if not self.error(browser=self.browser, log_path=self.log_path):
                        self.next_picture(browser=self.browser, log_path=self.log_path)
                        while self.user_followed_already(self.author(browser=self.browser, log_path=self.log_path)):
                            Log.update(
                                log_path=self.log_path,
                                text=self.author(
                                    browser=self.browser,
                                    log_path=self.log_path
                                ) + " was followed already. Skipping picture."
                            )
                            self.next_picture(browser=self.browser, log_path=self.log_path)
                        if self.post_is_sfw(browser=self.browser, log_path=self.log_path):
                            self.follow(
                                topic=top_hashtags[topic_selector],
                                browser=self.browser,
                                log_path=self.log_path
                            )
                            sleep(Config.delay)
                            self.store_hashtags(browser=self.browser, log_path=self.log_path)
                if len(self.accounts_to_unfollow) > 50:
                    for unfollows in range(2):
                        this_guy = self.accounts_to_unfollow[0]
                        self.unfollow(name=this_guy, browser=self.browser, log_path=self.log_path)
                        del self.accounts_to_unfollow[0]
        super(Driver, self).join()
