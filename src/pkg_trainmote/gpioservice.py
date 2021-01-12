import json
import RPi.GPIO as GPIO
from .traintrackingservice import TrackingService
from .models.GPIORelaisModel import GPIORelaisAdapter, GPIORelaisModel, GPIOSwitchHelper
from .models.GPIORelaisModel import GPIOStoppingPoint
from .models.GPIORelaisModel import GPIOSwitchPoint
from .databaseControllerModule import DatabaseController
from typing import Optional

gpioRelais = []
trackingServices = []
validGpios = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
switchPowerRelais: Optional[GPIORelaisModel] = None
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
    global switchPowerRelais
    config = DatabaseController().getConfig()
    if config is not None:
        if config.switchPowerRelais is not None:
            # Initialise GPIO for switch power relais
            switchPowerRelais = GPIORelaisModel("switchPowerRelais", config.switchPowerRelais)
            GPIO.setup(switchPowerRelais.relais_id, GPIO.OUT, initial=GPIO.HIGH)

    switchModels = DatabaseController().getAllSwichtModels()
    for model in switchModels:
        addSwitch(model)

    stopModels = DatabaseController().getAllStopModels()
    for stop in stopModels:
        addRelais(stop)

def removeRelais(relais: GPIORelaisModel):
    if relais in gpioRelais:
        gpioRelais.remove(relais)
        GPIO.cleanup(relais.relais_id)

def addSwitch(switch: GPIOSwitchPoint):    
    if switch.needsPowerOn and switchPowerRelais is not None:
        switch.setPowerRelais(switchPowerRelais)
    addRelais(switch)

def addRelais(relais: GPIORelaisModel):
    try:
        GPIO.setup(relais.relais_id, GPIO.OUT, initial=relais.defaultValue)
        gpioRelais.append(relais)
    except Exception as e:
        print(e)

def setupTrackingDefault():
    for relais in gpioRelais:
        if isinstance(relais, GPIOStoppingPoint) and relais.mess_id is not None:
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

def getValueForPin(pin):
    return GPIO.input(pin)


def getSwitchWithID(id):
    for relais in gpioRelais:
        if isinstance(relais, GPIOSwitchPoint):
            if relais.uid == id:
                return relais
    return None

def getStopWithID(id):
    for relais in gpioRelais:
        if isinstance(relais, GPIOStoppingPoint):
            if relais.uid == id:
                return relais
    return None

# Relais Actions


def switchPin(relais):
    if relais.getStatus():
        if isinstance(relais, GPIOStoppingPoint):
            trackingService = next(
                (tracker for tracker in trackingServices if tracker.stoppingPoint.uid == relais.uid),
                None
            )
            if trackingService:
                trackingService.stopTracking()
                trackingServices.remove(trackingService)
        return relais.setStatus(GPIO.LOW)
    else:
        if isinstance(relais, GPIOStoppingPoint) and relais.mess_id is not None:
            startTrackingFor(relais)
        return relais.setStatus(GPIO.HIGH)


def receivedMessage(message):
    return "msg:Not valid json"

##
# Switch
##


def getSwitch(id: str) -> str:
    switch = getSwitchFor(id)
    if switch is not None:
        return json.dumps(switch.to_dict())
    raise ValueError("Switch for id {} not found".format(id))


def getAllSwitches():
    return json.dumps([ob.to_dict() for ob in DatabaseController().getAllSwichtModels()])


def setSwitch(id: str) -> str:
    relais = getSwitchWithID(id)
    if relais is not None:
        switch = getSwitchFor(id)
        if switch is not None:
            newValue = switchPin(relais)
            return json.dumps({"model": switch.to_dict(), "currentValue": newValue})
    raise ValueError("Relais not found for id {}".format(id))

def getSwitchFor(uid: str) -> Optional[GPIOSwitchPoint]:
    for switch in DatabaseController().getAllSwichtModels():
        if switch.uid == uid:
            return switch
    return None

def createSwitch(data):
    gpioRelais = GPIORelaisAdapter.getGPIORelaisFor(data)
    if gpioRelais is not None:
        switchType = data.get("switchType")
        needsPowerOn = data.get("needsPowerOn")
        if GPIOSwitchHelper.isValidType(switchType):
            switch = GPIOSwitchPoint.fromParent(gpioRelais, switchType, needsPowerOn)
            result = storeSwitch(switch)
            if result is not None and result.relais_id is not None:
                return json.dumps(result.to_dict())
            else:
                raise ValueError("Could not create switch")
        else:
            raise ValueError("Inavlid switch type")
    else:
        raise ValueError("Could not create switch")

# Stores a Switch Point to the database if is a valid pin number.
# Throws error if not valid. Adds the relais to the gpioservice relais.
def storeSwitch(model: GPIOSwitchPoint) -> Optional[GPIOSwitchPoint]:
    if (model.relais_id is not None and isValidRaspberryPiGPIO(model.relais_id)):
        databaseController = DatabaseController()
        result = databaseController.insertSwitchModel(
            model.relais_id,
            model.switchType,
            model.needsPowerOn,
            model.defaultValue,
            model.name,
            model.description
        )
        if (result is not None):
            switch = databaseController.getSwitch(result)
            if (switch is not None):
                switch.setDefaultValue(model.defaultValue)
                addRelais(switch)
                return switch
    else:
        raise ValueError("Invalid gpio")


##
# Stop Point
##


def getStop(id: str):
    stop = getStopFor(id)
    if stop is not None:
        return json.dumps(stop.to_dict())
    return json.dumps({"error": "Stop for id {} not found".format(id)})


def getAllStopPoints():
    return json.dumps([ob.to_dict() for ob in DatabaseController().getAllStopModels()])

def setStop(id: str):
    relais = getStopWithID(id)
    if relais is not None:
        stop = getStopFor(id)
        if stop is not None:
            newValue = switchPin(relais)
            return json.dumps({"model": stop.to_dict(), "currentValue": newValue})
    raise ValueError("Relais not found for id {}".format(id))

def getStopFor(uid: str) -> Optional[GPIOStoppingPoint]:
    for stop in DatabaseController().getAllStopModels():
        if stop.uid == uid:
            return stop
    return None

def createStop(data):
    gpioRelais = GPIORelaisAdapter.getGPIORelaisFor(data)
    if gpioRelais is not None:
        mess_id = int(data.get("mess_id"))
        stop = GPIOStoppingPoint.fromParent(gpioRelais, mess_id)
        result = storeStop(stop)
        if result is not None and result.relais_id is not None:
            return json.dumps(result.to_dict())
        else:
            raise ValueError("Could not create stop")
    else:
        raise ValueError("Could not create stop")

# Stores a Stop Point to the database if is a valid pin number.
# Throws error if not valid. Adds the relais to the gpioservice relais.
def storeStop(model: GPIOStoppingPoint) -> Optional[GPIOStoppingPoint]:
    if (model.relais_id is not None and isValidRaspberryPiGPIO(model.relais_id)):
        databaseController = DatabaseController()
        result = databaseController.insertStopModel(
            model.relais_id,
            model.mess_id,
            model.name,
            model.defaultValue,
            model.description
        )
        if (result is not None):
            stop = databaseController.getStop(result)
            if (stop is not None):
                addRelais(stop)
                return stop
    else:
        raise ValueError("Invalid gpio")

def setAllToDefault():
    for relais in gpioRelais:
        relais.toDefault()

# Validation

def isValidRaspberryPiGPIO(pinNumber: int):
    return pinNumber in validGpios
