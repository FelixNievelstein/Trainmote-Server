from typing import List
from jsonschema import validate


class Validator:

    def validateDict(self, json, schema: dict):

        try:
            validate(instance=json, schema=schema)
            return True
        except Exception as e:
            print(e)
            return False
