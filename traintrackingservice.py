import Adafruit_ADS1x15
import time
import threading

class TrackingService: 

    GAIN = 1
    adc = Adafruit_ADS1x15.ADS1115()    
    isTracking = False

    def __init__(self, stoppingPoint):
        self.stoppingPoint = stoppingPoint
        self.trackingThread = threading.Thread(target=self.trackVoltageInBackground)
        
    def startTracking(self):
        # do some stuff
        self.isTracking = True
        self.trackingThread.start()
        print 'Start Tracking: '
        # continue doing stuff

    def trackVoltageInBackground(self):
        while self.isTracking:
            currentVoltage = self.adc.read_adc(self.stoppingPoint.measurmentpin, gain= self.GAIN)
            if abs(currentVoltage) > 10:
                print 'Detected voltage at Stopping Point: ' + self.stoppingPoint.measurmentpin
            time.sleep(0.3)

    def stopTracking(self):
        print 'Stop Tracking: ' +  self.stoppingPoint.measurmentpin
        self.isTracking = False
    