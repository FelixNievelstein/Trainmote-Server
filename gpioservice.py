import json
import RPi.GPIO as GPIO
from CommandResultModel import CommandResultModel


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
        command = jsonData["type"]
        if command == "SET_SWITCH" or command == "SET_STOPPING_POINT":
            switchPin(int(jsonData["id"]))
            return "msg:Setting GPIO"
        elif command == "GET_SWITCH" or command == "GET_STOPPING_POINT":
            return getValueForPin(int(jsonData["id"]), jsonData["id"], command)
        else:
            return "msg:Not supported"
    # Insert more here
    else:
        return "msg:Not supported"

def getValueForPin(pin, id, commandType):
    pinValue = GPIO.input(pin)
    commandResult = CommandResultModel(commandType, id, str(pinValue))
    return json.dumps(commandResult.__dict__)

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True