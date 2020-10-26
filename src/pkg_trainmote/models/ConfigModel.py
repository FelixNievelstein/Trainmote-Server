from typing import Optional

class ConfigModel():

    def __init__(self, uid: int, switchPowerRelais: Optional[int], powerRelais: Optional[int]):
        self.uid = uid
        self.switchPowerRelais = switchPowerRelais
        self.powerRelais = powerRelais

    def to_dict(self):
        return {"uid": self.uid, "switchPowerRelais": self.switchPowerRelais, "powerRelais": self.powerRelais}

    def containsPin(self, pin: int) -> bool:
        isSwitchPowerRelais = self.switchPowerRelais is not None and self.switchPowerRelais == pin
        isPowerRelais = self.powerRelais is not None and self.powerRelais == pin
        return isSwitchPowerRelais or isPowerRelais
