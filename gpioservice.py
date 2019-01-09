import json
import RPi.GPIO as GPIO


P_Switch1 = 29 # switch 1
P_Switch2 = 31 # switch 2
P_Switch3 = 33 # switch 3
P_Stop1 = 35 # stop 1
P_Stop2 = 37 # stop 2
P_Stop3 = 36 # stop 3
P_Stop4 = 38 # stop 3


def switchPin(pin):        
    if GPIO.input(pin):
        GPIO.output(pin, GPIO.LOW)
    else:
        GPIO.output(pin, GPIO.HIGH)

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(P_Switch1, GPIO.OUT)
    GPIO.setup(P_Switch2, GPIO.OUT)
    GPIO.setup(P_Switch3, GPIO.OUT)
    GPIO.setup(P_Stop1, GPIO.OUT)
    GPIO.setup(P_Stop2, GPIO.OUT)
    GPIO.setup(P_Stop3, GPIO.OUT)
    GPIO.setup(P_Stop4, GPIO.OUT)


def receivedMessage(message):
    print "receivedMessage"
    if is_json(message):
        jsonData = json.loads(message)                                
        print jsonData["type"]
        if jsonData["type"] == "SET_SWITCH" or jsonData["type"] == "SET_STOPPING_POINT":
            switchPin(int(jsonData["id"]))
            return "msg:Setting GPIO"
        elif jsonData["type"] == "GET_SWITCH" or jsonData["type"] == "GET_STOPPING_POINT":
            return getValueForPin(int(jsonData["id"]))
        else:
            return "msg:Not supported"
    # Insert more here
    else:
        return "msg:Not supported"

def getValueForPin(pin): 
    pinValue = GPIO.input(pin)
    return "msg: Switch" + pinValue

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True