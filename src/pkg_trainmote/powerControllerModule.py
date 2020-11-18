import RPi.GPIO as GPIO
import time
import threading

class PowerThread(threading.Thread):

    def __init__(self, pin: int):
        threading.Thread.__init__(self)
        self.isTurningOff = False
        self.kill = threading.Event()
        self.pin = pin
        GPIO.setup(pin, GPIO.IN)

    def run(self):
        self.trackVoltage()

    def stop(self):
        self.kill.set()

    def trackVoltage(self):
        while not self.isTurningOff and not self.kill.is_set():
            if GPIO.input(self.pin):
                self.isTurningOff = True
                print("Power off")
                from subprocess import call
                call("sudo nohup shutdown -h now", shell=True)
            else:
                time.sleep(0.5)
