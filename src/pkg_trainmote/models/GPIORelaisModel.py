import RPi.GPIO as GPIO
import time
import enum

class GPIORelaisModel():

    defaultValue = GPIO.HIGH

    def __init__(self, uid: int, pin: int):
        self.uid = uid
        self.pin = pin

    def setDefaultValue(self, value: int):
        self.defaultValue = value

    def toDefault(self):
        GPIO.output(self.pin, self.defaultValue)

    def getStatus(self):
        return GPIO.input(self.pin)

    def setStatus(self, value):
        GPIO.output(self.pin, value)
        return self.getStatus()

    def to_dict(self):
        return {"uid": self.uid, "pin": self.pin, "defaultValue": self.defaultValue, "status": self.getStatus()}


class GPIOStoppingPoint(GPIORelaisModel):

    def __init__(self, uid: int, pin: int, measurmentpin: int):
        self.measurmentpin = measurmentpin
        super(GPIOStoppingPoint, self).__init__(uid, pin)

    def to_dict(self):
        mdict = super(GPIOStoppingPoint, self).to_dict()
        mdict["measurmentpin"] = self.measurmentpin
        mdict["uid"] = self.uid
        return mdict


class GPIOSwitchType(enum.Enum):
    TM_SWITCH_STRAIGHT_LEFT = 1
    TM_SWITCH_STRAIGHT_RIGHT = 2
    TM_SWITCH_BORN_LEFT = 3
    TM_SWITCH_BORN_RIGHT = 4
    TM_SWITCH_CROSS = 5


class GPIOSwitchPoint(GPIORelaisModel):

    def __init__(self, uid: int, switchType: str, pin: int):
        self.needsPowerOn = True
        self.switchType = switchType
        self.powerRelais = None
        super(GPIOSwitchPoint, self).__init__(uid, pin)

    def setPowerRelais(self, relais: GPIORelaisModel):
        self.powerRelais = relais

    def setStatus(self, value: int):
        if self.needsPowerOn and self.powerRelais is not None:
            self.powerRelais.setStatus(GPIO.LOW)
        GPIO.output(self.pin, value)
        time.sleep(0.2)
        if self.needsPowerOn and self.powerRelais is not None:
            self.powerRelais.setStatus(GPIO.HIGH)
        return self.getStatus()

    def toDefault(self):
        if self.needsPowerOn and self.powerRelais is not None:
            self.powerRelais.setStatus(GPIO.LOW)
        GPIO.output(self.pin, self.defaultValue)
        time.sleep(0.2)
        if self.needsPowerOn and self.powerRelais is not None:
            self.powerRelais.setStatus(GPIO.HIGH)

    def to_dict(self):
        mdict = super(GPIOSwitchPoint, self).to_dict()
        mdict["needsPowerOn"] = self.needsPowerOn
        mdict["switchType"] = self.switchType
        mdict["uid"] = self.uid
        return mdict


class GPIOSwitchHelper():

    @staticmethod
    def isValidType(type: str) -> bool:
        for mType in (GPIOSwitchType):
            if mType.name == type:
                return True
        return False
