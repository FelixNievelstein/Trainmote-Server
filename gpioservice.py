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
    return GPIO.input(pin)

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(P_Switch1, GPIO.OUT)
    GPIO.setup(P_Switch2, GPIO.OUT)
    GPIO.setup(P_Switch3, GPIO.OUT)    
    GPIO.setup(P_Stop1, GPIO.OUT)
    setPinDefault(P_Stop1)
    GPIO.setup(P_Stop2, GPIO.OUT)
    setPinDefault(P_Stop2)
    GPIO.setup(P_Stop3, GPIO.OUT)
    setPinDefault(P_Stop3)
    GPIO.setup(P_Stop4, GPIO.OUT)
    setPinDefault(P_Stop4)


def receivedMessage(message):
    print "receivedMessage"
    if is_json(message):
        jsonData = json.loads(message) 
        results = "["
        for commandData in jsonData:
            results = results +  performCommand(commandData) + ","

        results = results + "]"
        return results
    # Insert more here
    else:
        return "msg:Not valid json"

def performCommand(command):
    commandType = command["commandType"]
    if commandType == "SET_SWITCH" or commandType == "SET_STOPPING_POINT":        
        return json.dumps(CommandResultModel(commandType, command["id"], switchPin(int(command["id"]))).__dict__)
    elif commandType == "GET_SWITCH" or commandType == "GET_STOPPING_POINT":
        return getValueForPin(int(command["id"]), command["id"], commandType)
    elif commandType == "CONFIG_SWITCH" or commandType == "CONFIG_STOPPING_POINT":
        return getValueForPin(int(command["id"]), command["id"], commandType)
    else:
        return "{ \"error\":\"Command not supported\"}"

def getValueForPin(pin, id, commandType):
    pinValue = GPIO.input(pin)
    return json.dumps(CommandResultModel(commandType, id, str(pinValue)).__dict__)

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

def setPinDefault(pin):
    GPIO.output(pin, GPIO.LOW)