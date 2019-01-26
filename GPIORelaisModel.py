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
        GPIO.output(self.pin, value)
        return self.getStatus()


class GPIOStoppingPoint(GPIORelaisModel):

    def __init__(self, id, pin, measurmentpin):
        self.measurmentpin = measurmentpin
        GPIORelaisModel.__init__(self, id, pin)

        
class GPIOSwitchPoint(GPIORelaisModel):        
    
    Power_Switch = 33 # Relais which powers switche    

    def __init__(self, id, pin):
        self.needsPowerOn = True
        powerRelais = GPIORelaisModel(Power_Switch, Power_Switch)
        GPIORelaisModel.__init__(self, id, pin) 

    def setStatus(self, value):
        if self.needsPowerOn:
                self.powerRelais.setStatus(GPIO.HIGH)
        GPIO.output(self.pin, value)
        self.powerRelais.setStatus(GPIO.LOW)
        return self.getStatus()


