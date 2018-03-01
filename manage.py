import os
import sys
import subprocess

if __name__ == "__main__":
    sys.path.append('../')

    print("Running instabot...")
    subprocess.Popen(['python3', 'run_instabot.py'])

    print("Launching server with the following work directories:")
    for path in sys.path:
        print("    "+path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carnivora.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
