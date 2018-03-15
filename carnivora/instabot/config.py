import pickle

config_store_path = "carnivora/instabot/config.pickle"

standard_config = {
    "bot_path": "carnivora/instabot/",
    "topics": ["graphics", "render", "cartoon", "daily", "art", "design", "cinema4d", "animation", "cg",
               "illustration", "3d", "corona", "octane", "rendering", "sculpting"],
    "start_url": "https://www.instagram.com/accounts/login/",
    "following_link": "https://www.instagram.com/{}/following/",
    "account_url": "https://www.instagram.com/{}/",
    "sections_xpath": "//*[contains(@class, '_75ljm _3qhgf')]",
    "local_name_xpath": ".//a[@class='_2g7d5 notranslate _nodr2']",
    "local_follow_xpath": "//a[@class='_ov9ai']",
    "hashtags_xpath": "//*[contains(@class, '_ezgzd')]",
    "first_ele_xpath": "//*[contains(@class, '_si7dy')]",
    "following_xpath": "//*[contains(@class, '_ohbcb _gvoze coreSpriteDesktopNavActivity')]",
    "follow_xpath": "//*[contains(@class, '_qv64e _iokts _4tgw8 _njrw0')]",
    "unfollow_xpath": "//*[contains(@class, '_qv64e _t78yp _r9b8f _njrw0')]",
    "comment_xpath": "//*[contains(@class, '_bilrf')]",
    "comment_submit_xpath": "//*[contains(@class, '_8scx2 coreSpriteComment')]",
    "error_xpath": "//*[contains(@class, 'error-container -cx-PRIVATE-ErrorPage__errorContainer')]",
    "dialog_xpath": "//*[contains(@class, '_pfyik _lz8g1')]",
    "author_xpath": "//*[contains(@class, '_2g7d5 notranslate _iadoq')]",
    "next_button_xpath": "//*[contains(@class, '_3a693 coreSpriteRightPaginationArrow')]",
    "like_button_xpath": "//*[contains(@class, '_8scx2 coreSpriteHeartOpen')]",
    "like_button_full_xpath": "//*[contains(@class, '_8scx2 coreSpriteHeartFull')]",
    "image_div_container_xpath": "//div[contains(@class,'_sxolz')]",
    "comments": ["Nice @{} {}", "@{} cool {} ", "Great style @{} {}", "Amazing @{} {}",
                 "Awesome @{} {}", "Fantastic @{} {}", "@{} {}", "Brilliant one @{} {}",
                 "Pretty nice @{} {}", "Awesome feed @{} {}", "I like your feed @{} {}",
                 "Top @{} {}", "Really cool works @{}! {}", "@{} Rad!!! {}",
                 "This is cool @{} {}", "Love this @{} {}", "Great @{}! {}", "Yeah @{} {}"
                 "I like your unique style @{} {}", "@{} take my like {}", "@{}"],
    "smileys": [smiley for smiley in [
        "🙂", "☺", "😎", "😋", "😊", "😉", "😄", "😃", "😁",
        "😀", "😜", "😝", "😲", "😇", "🤓", "😺", "😸",
        "💪", "✌", "👌", "👍", "👏", "🙌", "🐣", "🌎"
    ]],
}


class ConfigLoader:
    @staticmethod
    def load():
        try:
            with open(config_store_path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            with open(config_store_path, "wb") as f:
                pickle.dump(standard_config, f)
                return standard_config

    @staticmethod
    def store(key, new_value):
        config = ConfigLoader.load()
        config[key] = new_value
        with open(config_store_path, "wb") as f:
            pickle.dump(config, f)
            return config


class Config:
    config = ConfigLoader.load()

    bot_path = config["bot_path"]

    topics = config["topics"]
    start_url = config["start_url"]
    following_link = config["following_link"]
    account_url = config["account_url"]

    sections_xpath = config["sections_xpath"]
    local_name_xpath = config["local_name_xpath"]
    local_follow_xpath = config["local_follow_xpath"]

    hashtags_xpath = config["hashtags_xpath"]

    first_ele_xpath = config["first_ele_xpath"]

    following_xpath = config["following_xpath"]
    follow_xpath = config["follow_xpath"]
    unfollow_xpath = config["unfollow_xpath"]
    comment_xpath = config["comment_xpath"]
    comment_submit_xpath = config["comment_submit_xpath"]
    error_xpath = config["error_xpath"]

    dialog_xpath = config["dialog_xpath"]

    author_xpath = config["author_xpath"]
    next_button_xpath = config["next_button_xpath"]
    like_button_xpath = config["like_button_xpath"]
    like_button_full_xpath = config["like_button_full_xpath"]

    image_div_container_xpath = config["image_div_container_xpath"]

    comments = config["comments"]
    smileys = config["smileys"]