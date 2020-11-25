from subprocess import call
import time
from threading import Thread
import os
import sys

def shutdown():
    call("sudo nohup shutdown -h now", shell=True)

class ShutDownTimer(Thread):
    def run(self):
        time.sleep(2)
        shutdown()

def restart():
    call("sudo reboot", shell=True)

class RestartTimer(Thread):
    def run(self):
        time.sleep(2)
        restart()

def __performUpdate():
    call("pip3 install trainmote-module-felix-nievelstein-de -U", shell=True)
    os.execv(sys.argv[0], [sys.argv[0]])

def update():
    timer = UpdateTimer()
    timer.start()

class UpdateTimer(Thread):
    def run(self):
        time.sleep(2)
        __performUpdate()
