import os
import pickle

from django.apps import AppConfig

from carnivora.instabot.config import Config


class LureConfig(AppConfig):
    name = 'lure'

    def ready(self):
        # print("Logging out all users...")
        # from django.contrib.sessions.models import Session
        # Session.objects.all().delete()

        print("Resetting all flags...")
        log_directory = Config.bot_path + "log/"
        if os.path.exists(log_directory):
            subdirs = [x[0] for x in os.walk(log_directory)]
            for subdir in subdirs:
                if subdir == log_directory:
                    continue
                with open(subdir + "/running.pickle", "wb") as f:
                    pickle.dump(False, f)
