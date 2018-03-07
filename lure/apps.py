from django.apps import AppConfig


class LureConfig(AppConfig):
    name = 'lure'

    def ready(self):
        print("Logging out all users...")
        from django.contrib.sessions.models import Session
        Session.objects.all().delete()

        print("Resetting all flags...")

