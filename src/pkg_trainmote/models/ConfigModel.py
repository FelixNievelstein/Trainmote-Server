from typing import Optional

class ConfigModel():

    def __init__(
        self,
        uid: int,
        switchPowerRelais: Optional[int],
        powerRelais: Optional[int],
        stateRelais: Optional[int]
    ):
        self.uid = uid
        self.switchPowerRelais = switchPowerRelais
        self.powerRelais = powerRelais
        self.stateRelais = stateRelais

    def to_dict(self):
        return {
            "uid": self.uid,
            "switchPowerRelais": self.switchPowerRelais,
            "powerRelais": self.powerRelais,
            "stateRelais": self.stateRelais
        }

    def containsPin(self, pin: int) -> bool:
        isSwitchPowerRelais = self.switchPowerRelais is not None and self.switchPowerRelais == pin
        isPowerRelais = self.powerRelais is not None and self.powerRelais == pin
        isStateRelais = self.stateRelais is not None and self.stateRelais == pin
        return isSwitchPowerRelais or isPowerRelais or isStateRelais
