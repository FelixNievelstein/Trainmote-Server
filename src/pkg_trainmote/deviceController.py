from subprocess import call
import time
from threading import Thread


def shutdown():
    print("Power off")
    call("sudo nohup shutdown -h now", shell=True)

class ShutDownTimer(Thread):
    def run(self):
        time.sleep(2)
        shutdown()

def restart():
    print("Reboot")
    call("sudo reboot", shell=True)

class RestartTimer(Thread):
    def run(self):
        time.sleep(2)
        restart()
