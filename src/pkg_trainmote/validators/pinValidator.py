from pkg_trainmote.databaseControllerModule import DatabaseController
from typing import List
from pkg_trainmote.models.GPIORelaisModel import GPIORelaisModel

def containsPin(relais_id: int, relais: List[GPIORelaisModel]) -> bool:
    for rel in relais:
        if rel.relais_id == relais_id:
            return True
    return False

def isAlreadyInUse(pin: int):
    database = DatabaseController()
    stops = database.getAllStopModels()
    switchs = database.getAllSwichtModels()
    relaisIsStop = containsPin(pin, stops)
    if relaisIsStop:
        raise ValueError("Pin is already in use as stop point")
    relaisIsSwitch = containsPin(pin, switchs)
    if relaisIsSwitch:
        raise ValueError("Pin is already in use as switch")
    config = database.getConfig()
    if config is not None:
        if config.powerRelais is pin:
            raise ValueError("Pin is already in use as power relais")
        if config.switchPowerRelais is pin:
            raise ValueError("Pin is already in use as switch power relais")
        if config.stateRelais is pin:
            raise ValueError("Pin is already in use as state relais")
