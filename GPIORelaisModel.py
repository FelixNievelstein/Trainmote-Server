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


class GPIOStoppingPoint(GPIORelaisModel):

    def __init__(self, id, pin, measurmentpin):
        self.measurmentpin = measurmentpin
        GPIORelaisModel.__init__(self, id, pin)

    
        
class GPIOSwitchPoint(GPIORelaisModel):        
    
    
    def __init__(self, id, pin):
        self.needsPowerOn = True
        self.powerRelais = GPIORelaisModel(33, 33)
        GPIORelaisModel.__init__(self, id, pin) 

    def setStatus(self, value):
        if self.needsPowerOn:
                self.powerRelais.setStatus(GPIO.LOW)
        GPIO.output(self.pin, value)
        time.sleep(0.6)
        self.powerRelais.setStatus(GPIO.HIGH)
        return self.getStatus()

