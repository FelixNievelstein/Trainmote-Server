from typing import Optional

class ConfigModel():

    def __init__(
        self,
        uid: int,
        switchPowerRelais: Optional[int],
        powerRelais: Optional[int],
        stateRelais: Optional[int],
        deviceName: Optional[str]
    ):
        self.uid = uid
        if switchPowerRelais == 0:
            self.switchPowerRelais = None
        else:
            self.switchPowerRelais = switchPowerRelais

        if powerRelais == 0:
            self.powerRelais = None
        else:
            self.powerRelais = powerRelais

        if stateRelais == 0:
            self.stateRelais = None
        else:
            self.stateRelais = stateRelais
        
        self.deviceName = deviceName

    def to_dict(self):
        return {
            "uid": self.uid,
            "switchPowerRelais": self.switchPowerRelais,
            "powerRelais": self.powerRelais,
            "stateRelais": self.stateRelais,
            "deviceName": self.deviceName
        }

    def containsPin(self, pin: int) -> bool:
        isSwitchPowerRelais = self.switchPowerRelais is not None and self.switchPowerRelais == pin
        isPowerRelais = self.powerRelais is not None and self.powerRelais == pin
        isStateRelais = self.stateRelais is not None and self.stateRelais == pin
        return isSwitchPowerRelais or isPowerRelais or isStateRelais
