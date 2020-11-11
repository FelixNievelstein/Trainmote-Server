import json
import RPi.GPIO as GPIO
from pkg_trainmote.models.ConfigModel import ConfigModel
from .traintrackingservice import TrackingService
from .models.CommandResultModel import CommandResultModel
from .models.GPIORelaisModel import GPIORelaisModel, GPIOSwitchHelper
from .models.GPIORelaisModel import GPIOStoppingPoint
from .models.GPIORelaisModel import GPIOSwitchPoint
from .databaseControllerModule import DatabaseController
from typing import Optional

gpioRelais = []
trackingServices = []
validGpios = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

# Inital Loading and Setup


def setup():
    print("GPIOService setup")
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(True)
    except Exception as identifier:
        print(identifier)
    loadInitialData()
    setupTrackingDefault()


def loadInitialData():
    config = DatabaseController().getConfig()
    switchPowerRelais: Optional[GPIORelaisModel] = None
    if config is not None:
        if config.switchPowerRelais is not None:
            # Initialise GPIO for switch power relais
            switchPowerRelais = GPIORelaisModel(config.switchPowerRelais, config.switchPowerRelais)            
            GPIO.setup(switchPowerRelais.pin, GPIO.OUT, initial=GPIO.HIGH)

    switchModels = DatabaseController().getAllSwichtModels()
    for model in switchModels:
        if model.needsPowerOn and switchPowerRelais is not None:
            model.setPowerRelais(switchPowerRelais)
        addRelais(model)
    stopModels = DatabaseController().getAllStopModels()
    for stop in stopModels:
        addRelais(stop)


def addRelais(relais: GPIORelaisModel):
    try:
        GPIO.setup(relais.pin, GPIO.OUT, initial=relais.defaultValue)
        gpioRelais.append(relais)
    except Exception as e:
        print(e)


def setupTrackingDefault():
    for relais in gpioRelais:
        if isinstance(relais, GPIOStoppingPoint) and relais.measurmentpin is not None:
            startTrackingFor(relais)


def startTrackingFor(relais):
    trackingService = TrackingService(relais)
    trackingServices.append(trackingService)
    trackingService.startTracking()


def resetData():
    DatabaseController().removeAll()
    del gpioRelais[:]
    del trackingServices[:]

def clean():
    print("Clean GPIOs")
    GPIO.cleanup()

def createSwitch(id: int, default: int, switchType: str) -> Optional[GPIOSwitchPoint]:
    if (isValidRaspberryPiGPIO(id)):
        databaseController = DatabaseController()
        result = databaseController.insertSwitchModel(id, switchType, default)
        if (result is not None):
            switch = databaseController.getSwitch(result)
            if (switch is not None):
                switch.setDefaultValue(default)
                addRelais(switch)
                return switch
    return None


def createStop(id: int, measurmentid: Optional[int]) -> Optional[GPIOStoppingPoint]:
    if (isValidRaspberryPiGPIO(id)):
        databaseController = DatabaseController()
        result = databaseController.insertStopModel(id, measurmentid)
        if (result is not None):
            stop = databaseController.getStop(result)
            if (stop is not None):
                addRelais(stop)
                return stop
    return None


def getValueForPin(pin):
    return GPIO.input(pin)


def getRelaisWithID(id):
    for relais in gpioRelais:
        if relais.uid == id:
            return relais
    return None


# Relais Actions


def switchPin(relais):
    if relais.getStatus():
        if isinstance(relais, GPIOStoppingPoint):
            trackingService = next((tracker for tracker in trackingServices if tracker.stoppingPoint.id == relais.uid), None)
            if trackingService:
                trackingService.stopTracking()
                trackingServices.remove(trackingService)
        return relais.setStatus(GPIO.LOW)
    else:
        if isinstance(relais, GPIOStoppingPoint) and relais.measurmentpin is not None:
            startTrackingFor(relais)
        return relais.setStatus(GPIO.HIGH)


def receivedMessage(message):
    if is_json(message):
        jsonData = json.loads(message)
        results = "["
        if "CONFIG" in jsonData[0]["commandType"]:
            resetData()
        for commandData in jsonData:
            results = results + performCommand(commandData) + ","

        results = results[:-1] + "]"
        return results
    # Insert more here
    else:
        return "msg:Not valid json"

##
# Switch
##


def getSwitch(id: str) -> str:
    switch = getSwitchFor(int(id))
    if switch is not None:
        currentValue = switch.getStatus()
        return json.dumps({"model": switch.to_dict(), "currentValue": currentValue})
    return json.dumps({"error": "Switch for id {} not found".format(id)})


def getAllSwitches():
    return json.dumps([ob.to_dict() for ob in DatabaseController().getAllSwichtModels()])


def setSwitch(id: str) -> str:
    relais = getRelaisWithID(int(id))
    if relais is not None:
        switch = getSwitchFor(int(id))
        if switch is not None:
            newValue = switchPin(relais)
            return json.dumps({"model": switch.to_dict(), "currentValue": newValue})
    raise ValueError("Relais not found for id {}".format(id))

def getSwitchFor(uid: int) -> Optional[GPIOSwitchPoint]:
    for switch in DatabaseController().getAllSwichtModels():
        if switch.uid == uid:
            return switch
    return None

def configSwitch(data):
    params = data["params"]
    switchType = params["switchType"]
    if GPIOSwitchHelper.isValidType(switchType):
        result = createSwitch(int(data["id"]), int(data["defaultValue"]), params["switchType"])
        if result is not None:
            currentValue = getValueForPin(int(result.pin))
            return json.dumps({"model": result.to_dict(), "currentValue": currentValue})
        else:
            raise ValueError("{ \"error\":\"Could not create switch\"}")
    else:
        raise ValueError("{ \"error\":\"Inavlid switch type\"}")


##
# Stop Point
##


def getStop(id: str):
    for stop in DatabaseController().getAllStopModels():
        if str(stop.id) == id:
            currentValue = getValueForPin(int(stop.id))
            return json.dumps({"model": stop.to_dict(), "currentValue": currentValue})

    return json.dumps({"error": "Stop for id {} not found".format(id)})


def getAllStopPoints():
    return json.dumps([ob.to_dict() for ob in DatabaseController().getAllStopModels()])

def setStop(id: str):
    relais = getRelaisWithID(int(id))
    if relais is not None:
        stop = getStopFor(int(id))
        if stop is not None:
            newValue = switchPin(relais)
            return json.dumps({"model": stop.to_dict(), "currentValue": newValue})
    raise ValueError("Relais not found for id {}".format(id))

def getStopFor(uid: int) -> Optional[GPIOStoppingPoint]:
    for stop in DatabaseController().getAllStopModels():
        if stop.uid == uid:
            return stop
    return None

def configStop(data):
    if "measurmentId" in data:
        result = createStop(int(data["id"]), int(data["measurmentId"]))
    else:
        result = createStop(int(data["id"]), None)

    if result is not None:
        currentValue = getValueForPin(int(result.pin))
        return json.dumps({"model": result.to_dict(), "currentValue": currentValue})
    else:
        raise ValueError("{ \"error\":\"Could not create stop\"}")


def performCommand(command):
    commandType = command["commandType"]
    if commandType == "SET_SWITCH" or commandType == "SET_STOPPING_POINT":
        relais = getRelaisWithID(int(command["id"]))
        if relais is not None:
            return json.dumps(CommandResultModel(commandType, command["id"], switchPin(relais)).__dict__)
        else:
            return "{ \"error\":\"Relais not found\"}"
    elif commandType == "CONFIG_SWITCH":
        params = command["params"]
        resultId = createSwitch(int(command["id"]), int(command["defaultValue"]), params["switchType"])
        return json.dumps(CommandResultModel(commandType, resultId, "success").__dict__)
    elif commandType == "CONFIG_STOPPING_POINT":
        if 'measurmentId' in command:
            resultId = createStop(int(command["id"]), int(command["measurmentId"]))
        else:
            resultId = createStop(int(command["id"]), None)
        return json.dumps(CommandResultModel(commandType, resultId, "success").__dict__)
    elif commandType == "PERFORM_GIT_UPDATE":
        return json.dumps(CommandResultModel(commandType, 0, 'success').__dict__)
    else:
        return "{ \"error\":\"Command not supported\"}"


def setAllToDefault():
    for relais in gpioRelais:
        relais.toDefault()


# Validation


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True


def isValidRaspberryPiGPIO(pinNumber: int):
    return pinNumber in validGpios
