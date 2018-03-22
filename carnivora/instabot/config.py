import pickle

config_store_path = "carnivora/instabot/config.pickle"

standard_config = {
    "bot_path": "carnivora/instabot/",
    "nsfw_hashtags": [
        "#instansfw",
        "#instaadult",
        "#instagirls",
        "#instaamateur",
        "#instaphoto",
        "#instahentai",
        "#instalive",
        "#instachaturbate",
        "#nsfw",
        "#adult",
        "#girls",
        "#amateur",
        "#girl",
        "#photo",
        "#hentai",
        "#live",
        "#chaturbate",
        "#boob",
        "#bath",
        "#bubble",
        "#hotties",
        "#hotty",
        "#nsfwvideo",
        "#cuckold",
        "#account",
        "#purpleport",
        "#stuff",
        "#twitterafterdark",
        "#blowjob",
        "#vip",
        "#access",
        "#movies",
        "#instaporn",
        "#instavideo",
        "#instavideos",
        "#instaxxx",
        "#instawomen",
        "#instaporno",
        "#instaasian",
        "#instaphotos",
        "#asian",
        "#photos",
        "#pornvideos",
        "#freeporn",
        "#tube",
        "#pornvideo",
        "#pictures",
        "#porntube",
        "#pics",
        "#sites",
        "#pornmovies",
        "#men",
        "#vids",
        "#having",
        "#sexscene",
        "#freesex",
        "#com",
        "#analsex",
        "#sexvideos",
        "#naked",
        "#instanaked",
        "#xxx",
        "#instamodel",
        "#model",
        "#instacam",
        "#cam",
        "#instatruth",
        "#instalove",
        "#love",
        "#body",
        "#sleeping",
        "#getnaked",
        "#sweat",
        "#blood",
        "#man",
    ],
    "topics": ["graphics", "render", "cartoon", "daily", "art", "design", "cinema4d", "animation", "cg",
               "illustration", "3d", "corona", "octane", "rendering", "sculpting"],
    "start_url": "https://www.instagram.com/accounts/login/",
    "account_url": "https://www.instagram.com/{}/",
    "sections_xpath": "//*[contains(@class, '_75ljm _3qhgf')]",
    "local_name_xpath": ".//a[@class='_2g7d5 notranslate _nodr2']",
    "hashtags_xpath": "//*[contains(@class, '_ezgzd')]",
    "first_ele_xpath": "//*[contains(@class, '_si7dy')]",
    "following_xpath": "//*[contains(@class, '_ohbcb _gvoze coreSpriteDesktopNavActivity')]",
    "follow_xpath": "//*[contains(@class, '_qv64e _iokts _4tgw8 _njrw0')]",
    "unfollow_xpath": "//*[contains(@class, '_qv64e _t78yp _r9b8f _njrw0')]",
    "comment_xpath": "//*[contains(@class, '_bilrf')]",
    "comment_submit_xpath": "//*[contains(@class, '_8scx2 coreSpriteComment')]",
    "dialog_xpath": "//*[contains(@class, '_pfyik _lz8g1')]",
    "author_xpath": "//*[contains(@class, '_2g7d5 notranslate _iadoq')]",
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
                config = pickle.load(f)
                for key in standard_config.keys():
                    if key not in config.keys():
                        config[key] = standard_config[key]
                        with open(config_store_path, "wb") as f:
                            pickle.dump(config, f)
                        print("Added key ({}) to stored config as it is now needed from new features.".format(key))
                for key in config.copy().keys():
                    if key not in standard_config.keys():
                        del config[key]
                        with open(config_store_path, "wb") as f:
                            pickle.dump(config, f)
                        print("Removed key ({}) from stored config as it is no longer needed.".format(key))
                return config
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

    nsfw_hashtags = config["nsfw_hashtags"]

    bot_path = config["bot_path"]

    topics = config["topics"]
    start_url = config["start_url"]
    account_url = config["account_url"]

    sections_xpath = config["sections_xpath"]
    local_name_xpath = config["local_name_xpath"]

    hashtags_xpath = config["hashtags_xpath"]

    first_ele_xpath = config["first_ele_xpath"]

    following_xpath = config["following_xpath"]
    follow_xpath = config["follow_xpath"]
    unfollow_xpath = config["unfollow_xpath"]
    comment_xpath = config["comment_xpath"]
    comment_submit_xpath = config["comment_submit_xpath"]

    dialog_xpath = config["dialog_xpath"]

    author_xpath = config["author_xpath"]
    like_button_xpath = config["like_button_xpath"]
    like_button_full_xpath = config["like_button_full_xpath"]

    image_div_container_xpath = config["image_div_container_xpath"]

    comments = config["comments"]
    smileys = config["smileys"]