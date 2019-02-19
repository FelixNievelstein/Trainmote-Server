import RPi.GPIO as GPIO
import time
import threading

class PowerThread(threading.Thread):    

    def __init__(self):
        threading.Thread.__init__(self)
        self.isTurningOff = False
        self.kill = threading.Event()
        GPIO.setup(18, GPIO.IN)
    
    def run (self):
        self.trackVoltage()

    def trackVoltage(self):
        while not self.isTurningOff and not self.kill.is_set():
            if GPIO.input(18):
                self.isTurningOff = True
                print "Power off"
                # from subprocess import call
                # call("sudo nohup shutdown -h now", shell=True)
            time.sleep(0.5)        
                