from typing import List
from jsonschema import validate
from .databaseControllerModule import DatabaseController
from pkg_trainmote.models.GPIORelaisModel import GPIORelaisModel
from . import libInstaller
import sysconfig
import os.path
import json

class Validator:

    def validateDict(self, json, name: str):
        schema = self.get_schema(name)
        if schema is not None:
            try:
                validate(instance=json, schema=schema)
                return True
            except Exception as e:
                print(e)
        return False

    def get_schema(self, name: str):
        path = "{}/schemes/{}.json".format(os.path.dirname(libInstaller.__file__), name)
        try:
            with open(path, 'r') as file:
                schema = json.load(file)
                return schema
        except Exception as e:
            print(e)
            return None

    def containsPin(self, relais_id: int, relais: List[GPIORelaisModel]) -> bool:
        for rel in relais:
            if rel.relais_id == relais_id:
                return True
        return False 

    def isAlreadyInUse(self, pin: int):
        database = DatabaseController()
        stops = database.getAllStopModels()
        switchs = database.getAllSwichtModels()
        relaisIsStop = self.containsPin(pin, stops)
        if relaisIsStop:
            raise ValueError("Pin is already in use as stop point")
        relaisIsSwitch = self.containsPin(pin, switchs)
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
