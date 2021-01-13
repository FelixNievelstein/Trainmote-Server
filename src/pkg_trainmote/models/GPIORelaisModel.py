import RPi.GPIO as GPIO
import time
import enum
from typing import Any, Optional, Dict

class GPIORelaisModel():

    defaultValue = GPIO.HIGH

    def __init__(
        self, uid: str,
        relais_id: Optional[int],
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.uid = uid
        self.relais_id = relais_id
        self.name = name
        self.description = description

    def setDefaultValue(self, value: int):
        self.defaultValue = value

    def toDefault(self):
        GPIO.output(self.relais_id, self.defaultValue)

    def getStatus(self):
        return GPIO.input(self.relais_id)

    def setStatus(self, value):
        GPIO.output(self.relais_id, value)
        return self.getStatus()

    def to_dict(self):
        return {
            "uid": self.uid,
            "relais_id": self.relais_id,
            "defaultValue": self.defaultValue,
            "status": self.getStatus(),
            "name": self.name,
            "description": self.description
        }

    def __eq__(self, other):
        return self.relais_id == other.relais_id and self.uid == other.uid


class GPIORelaisAdapter():
    @staticmethod
    def getGPIORelaisFor(data) -> GPIORelaisModel:
        name = data.get("name")
        description = data.get("description")
        model = GPIORelaisModel("", int(data["relais_id"]), name, description)
        model.setDefaultValue(int(data["defaultValue"]))
        return model


class GPIOStoppingPoint(GPIORelaisModel):

    def __init__(
        self, uid: str,
        pin: Optional[int], mess_id: Optional[int],
        name: Optional[str], description: Optional[str]
    ):
        self.mess_id = mess_id
        super(GPIOStoppingPoint, self).__init__(uid, pin, name, description)

    def to_dict(self):
        mdict = super(GPIOStoppingPoint, self).to_dict()
        mdict["mess_id"] = self.mess_id
        mdict["uid"] = self.uid
        return mdict

    @classmethod
    def fromParent(cls, parent: GPIORelaisModel, mess_id: Optional[int]):
        classInstance = cls(parent.uid, parent.relais_id, mess_id, parent.name, parent.description)
        classInstance.setDefaultValue(parent.defaultValue)
        return classInstance

    @classmethod
    def from_dict(cls, data: Dict[str, Any], id: str):
        stop = cls(id, data.get("relais_id"), data.get("mess_id"), data.get("name"), data.get("description"))
        stop.defaultValue = data.get("defaultValue")
        return stop


class GPIOSwitchType(enum.Enum):
    TM_SWITCH_STRAIGHT_LEFT = 1
    TM_SWITCH_STRAIGHT_RIGHT = 2
    TM_SWITCH_BORN_LEFT = 3
    TM_SWITCH_BORN_RIGHT = 4
    TM_SWITCH_CROSS = 5


class GPIOSwitchPoint(GPIORelaisModel):

    def __init__(
        self, uid: str,
        switchType: Optional[str], pin: Optional[int],
        needsPowerOn: Optional[bool],
        name: Optional[str], description: Optional[str]
    ):
        self.needsPowerOn = needsPowerOn
        if needsPowerOn is None:
            self.needsPowerOn = True
        self.switchType = switchType
        self.powerRelais = None
        super(GPIOSwitchPoint, self).__init__(uid, pin, name, description)

    def setPowerRelais(self, relais: GPIORelaisModel):
        self.powerRelais = relais

    def setStatus(self, value: int):
        if self.needsPowerOn and self.powerRelais is not None:
            self.powerRelais.setStatus(GPIO.LOW)
        GPIO.output(self.relais_id, value)
        time.sleep(0.2)
        if self.needsPowerOn and self.powerRelais is not None:
            self.powerRelais.setStatus(GPIO.HIGH)
        return self.getStatus()

    def toDefault(self):
        if self.needsPowerOn and self.powerRelais is not None:
            self.powerRelais.setStatus(GPIO.LOW)
        GPIO.output(self.relais_id, self.defaultValue)
        time.sleep(0.2)
        if self.needsPowerOn and self.powerRelais is not None:
            self.powerRelais.setStatus(GPIO.HIGH)

    def to_dict(self):
        mdict = super(GPIOSwitchPoint, self).to_dict()
        mdict["needsPowerOn"] = self.needsPowerOn
        mdict["switchType"] = self.switchType
        mdict["uid"] = self.uid
        return mdict

    @classmethod
    def from_dict(cls, data: Dict[str, Any], id: str):
        switchType = data.get("switchType")
        if switchType is not None and GPIOSwitchHelper.isValidType(switchType) is False:
            raise ValueError("Invalid switch type")
        switch = cls(
            id,
            switchType,
            data.get("relais_id"),
            data.get("needsPowerOn"),
            data.get("name"),
            data.get("description")
        )
        switch.defaultValue = data.get("defaultValue")
        switch.needsPowerOn = data.get("needsPowerOn")
        return switch

    @classmethod
    def fromParent(cls, parent: GPIORelaisModel, switchType: str, needsPowerOn: bool):
        classInstance = cls(parent.uid, switchType, parent.relais_id, needsPowerOn, parent.name, parent.description)
        classInstance.setDefaultValue(parent.defaultValue)
        return classInstance


class GPIOSwitchHelper():

    @staticmethod
    def isValidType(type: str) -> bool:
        for mType in (GPIOSwitchType):
            if mType.name == type:
                return True
        return False
