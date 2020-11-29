from subprocess import call
import time
from threading import Thread
import os
import sys
from . import userHelper

def shutdownAfter(seconds: int):
    if userHelper.is_root() is True:
        timer = ShutDownTimer(seconds)
        timer.start()
    else:
        raise PermissionError("No root permission")

def shutdown():
    call("sudo nohup shutdown -h now", shell=True)

class ShutDownTimer(Thread):

    def __init__(self, time: int):
        Thread.__init__(self)
        self.time = time

    def run(self):
        time.sleep(self.time)
        shutdown()

def restartAfter(seconds: int):
    if userHelper.is_root() is True:
        timer = RestartTimer(seconds)
        timer.start()
    else:
        raise PermissionError("No root permission")


def restart():
    call("sudo reboot", shell=True)

class RestartTimer(Thread):
    def __init__(self, time: int):
        Thread.__init__(self)
        self.time = time

    def run(self):
        time.sleep(self.time)
        restart()

def performUpdate():
    if userHelper.is_root() is True:
        call("sudo pip3 install trainmote-module-felix-nievelstein-de -U", shell=True)
    else:
        call("pip3 install trainmote-module-felix-nievelstein-de -U", shell=True)
    os.execv(sys.argv[0], [sys.argv[0]])

def update():
    timer = UpdateTimer()
    timer.start()

class UpdateTimer(Thread):
    def run(self):
        time.sleep(2)
        performUpdate()
