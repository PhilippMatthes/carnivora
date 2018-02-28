from driver import Driver
from mailer import Mailer
from time import sleep
import traceback
import sys
import os
import errno
from socket import error as socket_error


def loop():
    session = Driver()
    mailer = Mailer()
    while True:
        message = mailer.get_current_message()
        if message == "Start" or message == "Continue":
            try:
                session.like_follow_loop()

            except KeyboardInterrupt:
                mailer.send("Keyboard Interrupt. Bot will exit now.")
                print("Exiting...")
                break
            except socket_error as err:
                raise err
            except Exception as err:
                for frame in traceback.extract_tb(sys.exc_info()[2]):
                    fname, lineno, fn, text = frame
                error = "Error in " + str(fname) + " on line " + str(lineno) + ": " + str(err)
                print(error)
                mailer.send(error)
                pass
        else:
            if message == "Stop" or message == "Exit":
                mailer.send("Instagram Bot will exit now.")
                raise Exception("Instagram Bot will exit now.")
            sleep(1)


def run():
    session = Driver()
    mailer = Mailer()
    while True:
        try:
            mailer.send("Instagram Bot started. Please send >>Start<< to start")
            loop()
        except socket_error as err:
            if err.errno != errno.ECONNREFUSED:
                raise err
            else:
                session = Driver()
                mailer = Mailer()


if __name__ == "__main__":
    run()
