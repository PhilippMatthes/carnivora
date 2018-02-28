import subprocess

from django.apps import AppConfig


class LureConfig(AppConfig):
    name = 'lure'

    def ready(self):
        subprocess.Popen(['python3', 'carnivora/instabot/main.py'])
        pass
