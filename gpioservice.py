import json
import RPi.GPIO as GPIO
from traintrackingservice import TrackingService
from CommandResultModel import CommandResultModel
from GPIORelaisModel import GPIORelaisModel
from GPIORelaisModel import GPIOStoppingPoint

gpioRelais = []
trackingServices = []

P_Switch1 = 29 # switch 1
P_Switch2 = 31 # switch 2
P_Switch3 = 33 # switch 3
P_Stop1 = 35 # stop 1
P_Stop2 = 37 # stop 2
P_Stop3 = 36 # stop 3
P_Stop4 = 38 # stop 4


def switchPin(relais):        
    if relais.getStatus():
        if isinstance(relais, GPIOStoppingPoint):
            trackingService = next((tracker for tracker in trackingServices if tracker.stoppingPoint.id == relais.id), None)
            if trackingService :
                trackingService.stopTracking()
                trackingServices.remove(trackingService)
        return relais.setStatus(GPIO.LOW)
    else:
        if isinstance(relais, GPIOStoppingPoint) and relais.measurmentpin is not None:
            startTrackingFor(relais)        
        return relais.setStatus(GPIO.HIGH)

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    gpioRelais.append(GPIORelaisModel(29, 29))
    gpioRelais.append(GPIORelaisModel(31, 31))
    gpioRelais.append(GPIORelaisModel(33, 33))
    gpioRelais.append(GPIOStoppingPoint(35, 35, None))
    gpioRelais.append(GPIOStoppingPoint(37, 37, None))
    gpioRelais.append(GPIOStoppingPoint(36, 36, 2))
    gpioRelais.append(GPIOStoppingPoint(38, 38, None))
    setupTrackingDefault()

def setupTrackingDefault():
    for relais in gpioRelais:
        if isinstance(relais, GPIOStoppingPoint) and relais.measurmentpin is not None:
            startTrackingFor(relais)
        
def startTrackingFor(relais):
    trackingService = TrackingService(relais)
    trackingServices.append(trackingService)
    trackingService.startTracking()

def receivedMessage(message):
    print "receivedMessage"
    if is_json(message):
        jsonData = json.loads(message) 
        results = "["
        for commandData in jsonData:
            results = results +  performCommand(commandData) + ","

        results = results[:-1] + "]"
        return results
    # Insert more here
    else:
        return "msg:Not valid json"

def performCommand(command):
    commandType = command["commandType"]
    if commandType == "SET_SWITCH" or commandType == "SET_STOPPING_POINT":
        relais = getRelaisWithID(int(command["id"]))
        if relais is not None:
            return json.dumps(CommandResultModel(commandType, command["id"], switchPin(relais)).__dict__)
        else:
            return "{ \"error\":\"Relais not found\"}"
    elif commandType == "GET_SWITCH" or commandType == "GET_STOPPING_POINT":
        return getValueForPin(int(command["id"]), command["id"], commandType)
    elif commandType == "CONFIG_SWITCH" or commandType == "CONFIG_STOPPING_POINT":
        return getValueForPin(int(command["id"]), command["id"], commandType)
    else:
        return "{ \"error\":\"Command not supported\"}"

def getValueForPin(pin, id, commandType):
    pinValue = GPIO.input(pin)
    return json.dumps(CommandResultModel(commandType, id, str(pinValue)).__dict__)

def getRelaisWithID(id): 
    return next((relais for relais in gpioRelais if relais.id == id), None)

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True