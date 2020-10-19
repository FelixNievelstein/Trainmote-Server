from typing import Optional

class ConfigModel():

    def __init__(self, uid: int, switchPowerRelais: Optional[int], powerRelais: Optional[int]):
        self.uid = uid
        self.switchPowerRelais = switchPowerRelais
        self.powerRelais = powerRelais

    def to_dict(self):
        return {"uid": self.uid, "switchPowerRelais": self.switchPowerRelais, "powerRelais": self.powerRelais}
