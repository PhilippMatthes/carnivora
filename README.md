# carnivora

![Showcase](MOCKUP.jpg?raw=true "DragTimer App")

## Dependencies

This Project uses [tensorflow-open_nsfw](https://github.com/mdietrichstein/tensorflow-open_nsfw) by Marc Dietrichstein
for image classification.

Carnivora uses the following libraries:
- skimage
- TensorFlow
- Selenium Webdriver
- urllib
- urllib3
- telepot

## Creating a superuser
Before you can use the server, you must create a superuser. Type in `python manage.py createsuperuser` and follow the instructions.

### Controlling the bot via Telegram

```
Start - Starts the bot in the initial phase
Stop - Terminates the bot. It will not be able to run again!
Pause - Pauses the bot.
Continue - Continues after pausing the bot.
```
