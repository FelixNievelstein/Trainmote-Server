from typing import List
from jsonschema import validate

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

    def containsPin(self, pin: int, relais: List[GPIORelaisModel]) -> bool:
        for rel in relais:
            if rel.pin == pin:
                return True
        return False
