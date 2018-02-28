class Config:
    bot_path = "carnivora/instabot/"

    topics = ["graphics",
              "render",
              "cartoon",
              "daily",
              "art",
              "design",
              "cinema4d",
              "animation",
              "cg",
              "illustration",
              "3d",
              "corona",
              "octane",
              "rendering",
              "sculpting"]
    delay = 35
    start_url = "https://www.instagram.com/accounts/login/"
    following_link = "https://www.instagram.com/snrmtths/following/"
    account_url = "https://www.instagram.com/snrmtths/"
    headless_is_available = True

    # The following (xpath) classes need to be refreshed every now and then.
    # they define, where elements are located on Instagram.

    sections_xpath = "//*[contains(@class, '_75ljm _3qhgf')]"
    local_name_xpath = ".//a[@class='_2g7d5 notranslate _nodr2']"
    local_follow_xpath = "//a[@class='_ov9ai']"

    hashtags_xpath = "//*[contains(@class, '_ezgzd')]"
    # local_button_xpath = ".//*[@class='_ah57t _6y2ah _i46jh _rmr7s']"

    first_ele_xpath = "//*[contains(@class, '_si7dy')]"

    following_xpath = "//*[contains(@class, '_ohbcb _gvoze coreSpriteDesktopNavActivity')]"
    follow_xpath = "//*[contains(@class, '_qv64e _iokts _4tgw8 _njrw0')]"
    unfollow_xpath = "//*[contains(@class, '_qv64e _t78yp _r9b8f _njrw0')]"
    comment_xpath = "//*[contains(@class, '_bilrf')]"
    error_xpath = "//*[contains(@class, 'error-container -cx-PRIVATE-ErrorPage__errorContainer')]"

    author_xpath = "//*[contains(@class, '_2g7d5 notranslate _iadoq')]"
    next_button_xpath = "//*[contains(@class, '_3a693 coreSpriteRightPaginationArrow')]"
    like_button_xpath = "//*[contains(@class, '_8scx2 coreSpriteHeartOpen')]"
    like_button_full_xpath = "//*[contains(@class, '_8scx2 coreSpriteHeartFull')]"

    # Available comments: the first {} is replaced with the username
    # the second is replaced with a smiley. Note that UTF-8 smileys are only
    # supported by Firefox driver which may corrupt some timed functionalities.
    comments = ["Nice @{} {}", "@{} cool {} ", "Great style @{} {}", "Amazing @{} {}",
                "Awesome @{} {}", "Fantastic @{} {}", "@{} {}", "Brilliant one @{} {}",
                "Pretty nice @{} {}", "Awesome feed @{} {}", "I like your feed @{} {}",
                "Top @{} {}", "Really cool works @{}! {}", "@{} Rad!!! {}",
                "This is cool @{} {}", "Love this @{} {}", "Great @{}! {}", "Yeah @{} {}"]
    smileys = [":)", ":D", "=D", "=)", ";)", ":)", ":)", ";D"]
