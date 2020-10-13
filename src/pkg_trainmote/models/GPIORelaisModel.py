import RPi.GPIO as GPIO
import time


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


class GPIOSwitchPoint(GPIORelaisModel):

    def __init__(self, uid: int, switchType: str, pin: int):
        self.needsPowerOn = True
        self.switchType = switchType
        self.powerRelais = GPIORelaisModel(13, 13)
        super(GPIOSwitchPoint, self).__init__(uid, pin)

    def setStatus(self, value: int):
        if self.needsPowerOn:
            self.powerRelais.setStatus(GPIO.LOW)
        GPIO.output(self.pin, value)
        time.sleep(0.2)
        self.powerRelais.setStatus(GPIO.HIGH)
        return self.getStatus()

    def toDefault(self):
        if self.needsPowerOn:
            self.powerRelais.setStatus(GPIO.LOW)
        GPIO.output(self.pin, self.defaultValue)
        time.sleep(0.2)
        self.powerRelais.setStatus(GPIO.HIGH)

    def to_dict(self):
        mdict = super(GPIOSwitchPoint, self).to_dict()
        mdict["needsPowerOn"] = self.needsPowerOn
        mdict["switchType"] = self.switchType
        mdict["uid"] = self.uid
        return mdict
