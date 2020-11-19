import RPi.GPIO as GPIO
import threading
import time

STATE_NOT_CONNECTED = "BLUETOOTH_NOT_CONNECTED"
STATE_CONNECTED = "BLUETOOTH_CONNECTED"
STATE_SHUTDOWN = "SHUTDOWN_IN_PROCESS"

class StateController:

    stateThread = None

    def __init__(self, pin: int):
        GPIO.setup(pin, GPIO.OUT)
        self.statePin = pin

    def setState(self, stateName):
        print("Changing Thread")
        self.stop()
        print("Create New State Thread")
        self.stateThread = StateThread(stateName, self.statePin)
        self.stateThread.start()

    def stop(self):
        if self.stateThread is not None:
            print("Kill Thread")
            self.stateThread.kill.set()
            self.stateThread.turnOff()
            self.stateThread.join()


class StateThread(threading.Thread):

    currentState = ""

    def __init__(self, state, pin: int):
        threading.Thread.__init__(self)
        self.currentState = state
        self.kill = threading.Event()
        self.pin = pin

    def run(self):
        if self.currentState == STATE_NOT_CONNECTED:
            self.blink(1)
        elif self.currentState == STATE_CONNECTED:
            self.turnOn()
        elif self.currentState == STATE_SHUTDOWN:
            self.blink(0.2)
        else:
            self.turnOff()

    def blink(self, blinkTime):
        isOn = False
        while not self.kill.is_set():
            if isOn:
                self.turnOff()
            else:
                self.turnOn()
            isOn = not isOn
            time.sleep(blinkTime)

    def turnOff(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def turnOn(self):
        GPIO.output(self.pin, GPIO.LOW)
