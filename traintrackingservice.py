import Adafruit_ADS1x15
import time
import threading

class TrackingService: 
    
    isTracking = False

    def __init__(self, stoppingPoint):
        self.stoppingPoint = stoppingPoint
        self.trackingThread = TrackerThread(stoppingPoint)
        
    def startTracking(self):
        # do some stuff
        self.isTracking = True
        self.trackingThread.start()
        print ('Start Tracking: ', self.stoppingPoint.measurmentpin)
        # continue doing stuff    

    def stopTracking(self):
        print ('Stop Tracking: ',  self.stoppingPoint.measurmentpin)
        self.trackingThread.kill.set()
        self.trackingThread.join()
        self.isTracking = False

class TrackerThread(threading.Thread):

    GAIN = 1
    adc = Adafruit_ADS1x15.ADS1115()

    def __init__(self, stoppingPoint):
        threading.Thread.__init__(self)
        self.stoppingPoint = stoppingPoint
        self.kill = threading.Event()
    
    def run (self):
        self.trackVoltage()

    def trackVoltage(self):
        while not self.kill.is_set():
            currentVoltage = self.adc.read_adc(self.stoppingPoint.measurmentpin, gain= self.GAIN)
            #if abs(currentVoltage) > 10:
             #   print ('Detected voltage at Stopping Point: ', self.stoppingPoint.measurmentpin)
            time.sleep(0.3)