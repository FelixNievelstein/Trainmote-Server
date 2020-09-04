import RPi.GPIO as GPIO
import time


class GPIORelaisModel(object):

    defaultValue = GPIO.HIGH

    def __init__(self, id, pin):
        self.id = id
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.toDefault()

    def setDefaultValue(self, value):
        self.defaultValue = value

    def toDefault(self):
        GPIO.output(self.pin, self.defaultValue)

    def getStatus(self):
        return GPIO.input(self.pin)

    def setStatus(self, value):
        GPIO.output(self.pin, value)
        return self.getStatus()

    def to_dict(self):
        return {"id": self.id, "pin": self.pin, "defaultValue": self.defaultValue, "status": self.getStatus()}


class GPIOStoppingPoint(GPIORelaisModel):

    def __init__(self, id, pin, measurmentpin):
        self.measurmentpin = measurmentpin
        super(GPIOStoppingPoint, self).__init__(id, pin)        

    def to_dict(self):
        mdict = super(GPIOStoppingPoint, self).to_dict()
        print(mdict)
        mdict["measurmentpin"] = self.measurmentpin
        return mdict


class GPIOSwitchPoint(GPIORelaisModel):

    def __init__(self, id, switchType, pin):
        self.needsPowerOn = True
        self.switchType = switchType
        self.powerRelais = GPIORelaisModel(33, 33)
        super(GPIOSwitchPoint, self).__init__(id, pin)        

    def setStatus(self, value):
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
        print(mdict)
        mdict["needsPowerOn"] = self.needsPowerOn
        mdict["switchType"] = self.switchType
        return mdict
