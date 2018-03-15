import datetime
import threading

import os
from traceback import format_exc

from selenium import webdriver  # For webpage crawling
from time import sleep

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # For input processing
from random import randint
import pickle  # For data management

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from carnivora.instabot.config import Config
from carnivora.instabot.log import Log

from tf_open_nsfw.classify_nsfw import classify_nsfw


class Driver(threading.Thread):
    def __init__(
            self,
            username,
            password,
            screenshot_path,
            window_width=1920,
            window_height=1080,
    ):

        self.username = username
        self.password = password

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

        try:
            from xvfbwrapper import Xvfb
            try:
                self.vdisplay = Xvfb()
                self.vdisplay.start()
            except EnvironmentError:
                print("Selenium Webdriver will run without Xvfb. There was an error starting Xvfb.")
        except ImportError:
            print("Selenium Webdriver will run without Xvfb. Install Xvfb to run Selenium Webdriver inside Xvfb.")

        self.browser = webdriver.PhantomJS()
        self.browser.set_window_size(window_width, window_height)
        self.screenshot_path = screenshot_path

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
    def now():
        return datetime.datetime.now()

    def focus(self, element, browser):
        if self.running():
            browser.execute_script("arguments[0].focus();", element)

    def user_followed_already(self, user):
        if self.running():
            return user in self.followed_accounts

    def login(self, username, password, browser, log_path, timeout=5):
        if self.running():
            Log.update(self.screenshot_path, self.browser, log_path, "Logging in")
            browser.get(Config.start_url)
            try:
                username_field = WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.NAME, "username"))
                )
                pass_field = WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.NAME, "password"))
                )
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in login')
                return
            username_field.send_keys(username)
            pass_field.send_keys(password)
            pass_field.send_keys(Keys.RETURN)

            Log.update(self.screenshot_path, self.browser, log_path, "Logged in")

    def update_action_list(self, author, action_type, topic):
        if author not in self.action_list.keys():
            value = {"type": action_type, "time": Driver.now(), "topic": topic}
            self.action_list[author] = [value]
        else:
            value = {"type": action_type, "time": Driver.now(), "topic": topic}
            author_actions = self.action_list[author]
            author_actions.append(value)
            self.action_list[author] = author_actions

        with open(self.action_list_path, "wb") as f:
            pickle.dump(self.action_list, f)

    def on_dialog_page(self, browser, log_path, check_timeout=1):
        if self.running():
            try:
                WebDriverWait(browser, check_timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.dialog_xpath))
                )
            except (TimeoutException, NoSuchElementException):
                Log.update(self.screenshot_path, self.browser, log_path, 'No longer on dialog page.')
                return False
            else:
                return True

    def comment(self, topic, browser, log_path, timeout=5):
        if self.running():
            author = self.author(browser=browser, log_path=log_path)
            query = Config.comments[randint(0, len(Config.comments) - 1)]
            say = query.format(author, Config.smileys[randint(0, len(Config.smileys) - 1)])
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.comment_xpath))
                )
                comment_field = WebDriverWait(browser, timeout).until(
                    ec.element_to_be_clickable((By.XPATH, Config.comment_xpath))
                )
                comment_button = WebDriverWait(browser, timeout).until(
                    ec.element_to_be_clickable((By.XPATH, Config.comment_submit_xpath))
                )
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in comment')
                return
            comment_field.click()
            actions = ActionChains(browser)
            actions.send_keys(say)
            actions.perform()
            comment_button.click()
            Log.update(self.screenshot_path, self.browser, log_path, "Commented on "+str(author)+"s picture with: "+say)
            self.update_action_list(author=author, action_type="comment", topic=topic)

    def search(self, browser, log_path, query):
        if self.running():
            browser.get("https://www.instagram.com/explore/tags/" + query + "/")
            Log.update(self.screenshot_path, self.browser, log_path, "Searching for " + query + ".")

    # Selects the first picture in a loaded topic screen
    def select_first(self, browser, log_path, timeout=5):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.first_ele_xpath))
                )
                pictures = browser.find_elements_by_xpath(Config.first_ele_xpath)
            except NoSuchElementException:
                Log.update(self.screenshot_path, self.browser, log_path,
                           'NoSuchElementException in select_first: ' + str(format_exc()))
                return
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in select_first')
                return
            if len(pictures) > 9:
                first_picture = pictures[9]
            else:
                first_picture = pictures[len(pictures) - 1]
            self.focus(first_picture, browser=browser)
            first_picture.click()

    def next_picture(self, browser):
        if self.running():
            actions = ActionChains(browser)
            actions.send_keys(Keys.ARROW_RIGHT)
            actions.perform()

    def author(self, browser, log_path, timeout=5):
        if self.running():
            try:
                author_element = WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.author_xpath))
                )
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in author')
                return
            return str(author_element.get_attribute("title"))

    def already_liked(self, browser, log_path, error_timeout=5):
        if self.running():
            try:
                WebDriverWait(browser, error_timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.like_button_full_xpath))
                )
            except TimeoutException:
                return False
            Log.update(self.screenshot_path, self.browser, log_path, 'Post was already liked.')
            return True

    # Likes a picture
    def like(self, browser, log_path, topic, timeout=5):
        if self.running():
            author = self.author(browser=browser, log_path=log_path)
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.like_button_xpath))
                )
                like_button = WebDriverWait(browser, timeout).until(
                    ec.element_to_be_clickable((By.XPATH, Config.like_button_xpath))
                )
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in like')
                return
            like_button.click()
            src = self.extract_picture_source(browser=browser, log_path=log_path)
            Log.update(self.screenshot_path, self.browser, log_path, "Liked picture/video by: "+author, image=src)
            self.update_action_list(author=author, action_type="like", topic=topic)

    # Unfollows a user
    def unfollow(self, browser, log_path, name, timeout=5):
        if self.running():
            browser.get("https://www.instagram.com/" + name + "/")
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.unfollow_xpath))
                )
                unfollow_button = WebDriverWait(browser, timeout).until(
                    ec.element_to_be_clickable((By.XPATH, Config.unfollow_xpath))
                )
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in unfollow')
                return
            unfollow_button.click()

    def update_accounts_to_unfollow(self, author):
        self.accounts_to_unfollow.append(author)
        with open(self.accounts_to_unfollow_path, "wb") as f:
            pickle.dump(self.accounts_to_unfollow, f)

    def update_followed_accounts(self, author):
        self.followed_accounts.update({author: Driver.now()})
        with open(self.followed_users_all_time_path, "wb") as userfile:
            pickle.dump(self.followed_accounts, userfile)

    # Follows a user
    def follow(self, browser, log_path, topic, timeout=5):
        if self.running():
            author = self.author(browser=browser, log_path=log_path)
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.follow_xpath))
                )
                follow_button = WebDriverWait(browser, timeout).until(
                    ec.element_to_be_clickable((By.XPATH, Config.follow_xpath))
                )
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in follow')
                return
            follow_button.click()
            Log.update(self.screenshot_path, browser=self.browser, log_path=self.log_path, text="Followed: " + author)
            self.update_action_list(author=author, action_type="follow", topic=topic)
            self.update_accounts_to_unfollow(author=author)
            self.update_followed_accounts(author=author)

    def open_unfollow_screen(self, browser, log_path, timeout=15):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.following_xpath))
                )
                heart = WebDriverWait(browser, timeout).until(
                    ec.element_to_be_clickable((By.XPATH, Config.following_xpath))
                )
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in open_unfollow_screen')
                return
            heart.click()

    def update_interacting_users(self, user):
        self.interacting_users.append(user)
        with open(self.interacting_users_path, "wb") as f:
            pickle.dump(self.interacting_users, f)

    def check_follows(self, browser, log_path, timeout=15):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.sections_xpath))
                )
                sections = browser.find_elements_by_xpath(Config.sections_xpath)
            except NoSuchElementException:
                Log.update(self.screenshot_path, self.browser, log_path,
                           'NoSuchElementException in check_follows: ' + str(format_exc()))
                return
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in check_follows')
                return

            users = []

            for element in sections:
                try:
                    profile = element.find_element_by_xpath(Config.local_name_xpath)
                except NoSuchElementException:
                    Log.update(self.screenshot_path, self.browser, log_path,
                               'NoSuchElementException in check_follows: ' + str(format_exc()))
                    return
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

    def store_hashtags(self, browser, log_path, timeout=5):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.hashtags_xpath))
                )
                sections = browser.find_elements_by_xpath(Config.hashtags_xpath)
            except NoSuchElementException:
                Log.update(self.screenshot_path, self.browser, log_path,
                           'Exception in store_hashtags: ' + str(format_exc()))
                return
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in store_hashtags')
                return
            for section in sections:
                all_hashtags = self.extract_hash_tags(section.text)
                for hashtag in all_hashtags:
                    self.update_hashtags(hashtag=hashtag)

    def extract_hash_tags(self, s):
        if self.running():
            return set(part[1:] for part in s.split() if part.startswith('#'))

    def extract_picture_source(self, browser, log_path, timeout=5):
        if self.running():
            try:
                WebDriverWait(browser, timeout).until(
                    ec.presence_of_element_located((By.XPATH, Config.image_div_container_xpath))
                )
                sections = browser.find_elements_by_xpath(Config.image_div_container_xpath)
            except NoSuchElementException:
                Log.update(self.screenshot_path, self.browser, log_path,
                           'Exception in extract_picture_source: ' + str(format_exc()))
                return
            except TimeoutException:
                Log.update(self.screenshot_path, self.browser, log_path, 'Timeout in extract_picture_source')
                return
            for section in sections:
                try:
                    image = section.find_element_by_tag_name("img")
                except NoSuchElementException:
                    Log.update(self.screenshot_path, self.browser, log_path,
                               'Exception in extract_picture_source: ' + str(format_exc()))
                    return
                return image.get_attribute("src")

    def post_is_sfw(self, browser, log_path):
        if self.running():
            image_url = self.extract_picture_source(browser=browser, log_path=log_path)
            if not image_url:
                return True
            sfw, nsfw = classify_nsfw(image_url)
            Log.update(
                screenshot_path=self.screenshot_path,
                browser=self.browser,
                log_path=self.log_path,
                text="Analysis of this post yielded it to be {}% NSFW.".format(int(100 * nsfw)),
                image=image_url
            )
            return nsfw < sfw

    def run(self):
        self.login(browser=self.browser, log_path=self.log_path, password=self.password, username=self.username)
        while self.running():
            try:
                self.open_unfollow_screen(browser=self.browser, log_path=self.log_path)
                self.check_follows(browser=self.browser, log_path=self.log_path)

                top_hashtags = sorted(self.hashtags.keys(), key=lambda k: self.hashtags[k], reverse=True)[:20]

                for i, topic in enumerate(top_hashtags):

                    self.search(query=topic, browser=self.browser, log_path=self.log_path)
                    self.select_first(browser=self.browser, log_path=self.log_path)
                    for comments in range(1):
                        if self.post_is_sfw(browser=self.browser, log_path=self.log_path):
                            self.comment(
                                topic=topic,
                                browser=self.browser,
                                log_path=self.log_path
                            )
                            self.store_hashtags(browser=self.browser, log_path=self.log_path)
                            sleep(Config.delay)
                        self.next_picture(browser=self.browser, log_path=self.log_path)
                    for likes in range(3):
                        count = 0
                        while self.already_liked(browser=self.browser, log_path=self.log_path):
                            if not self.on_dialog_page(self.browser, self.log_path):
                                break
                            if count > 10:
                                break
                            self.next_picture(browser=self.browser, log_path=self.log_path)
                            count += 1
                        if self.on_dialog_page(self.browser, self.log_path):
                            if self.post_is_sfw(browser=self.browser, log_path=self.log_path):
                                self.like(topic=topic, browser=self.browser,
                                          log_path=self.log_path)
                                sleep(Config.delay)
                                self.store_hashtags(browser=self.browser, log_path=self.log_path)

                                self.next_picture(browser=self.browser, log_path=self.log_path)
                    for follows in range(2):
                        self.next_picture(browser=self.browser, log_path=self.log_path)
                        count = 0
                        while self.user_followed_already(self.author(browser=self.browser, log_path=self.log_path)):
                            if not self.on_dialog_page(self.browser, self.log_path):
                                break
                            if count > 10:
                                break
                            self.next_picture(browser=self.browser, log_path=self.log_path)
                            count += 1
                        if self.on_dialog_page(self.browser, self.log_path):
                            if self.post_is_sfw(browser=self.browser, log_path=self.log_path):
                                self.follow(
                                    topic=topic,
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
            except Exception:
                Log.update(self.screenshot_path, self.browser, self.log_path,
                           text='General Exception: ' + str(format_exc()))
        Log.update(self.screenshot_path, self.browser, self.log_path, text='Stopped bot')
        if self.vdisplay:
            self.vdisplay.stop()
        super(Driver, self).join()
