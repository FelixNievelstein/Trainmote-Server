import RPi.GPIO as GPIO

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
        return GPIO.output(self.pin, value)


class GPIOStoppingPoint(GPIORelaisModel):

    def __init__(self, id, pin, measurmentpin):
        self.measurmentpin = measurmentpin    
        GPIORelaisModel.__init__(self, id, pin)


