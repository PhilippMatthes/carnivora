import subprocess
from django.apps import AppConfig

import instabot.main as instabot


class LureConfig(AppConfig):
    name = 'lure'

    def ready(self):
        subprocess.Popen(['python3', 'instabot/main.py'])
