import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
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
        print('Start Tracking: ', self.stoppingPoint.mess_id)
        # continue doing stuff

    def stopTracking(self):
        print('Stop Tracking: ', self.stoppingPoint.mess_id)
        self.trackingThread.kill.set()
        self.trackingThread.join()
        self.isTracking = False


class TrackerThread(threading.Thread):

    GAIN = 1
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    def __init__(self, stoppingPoint):
        threading.Thread.__init__(self)
        self.stoppingPoint = stoppingPoint
        self.kill = threading.Event()

        try:
            # Create the ADC object using the I2C bus
            ads = ADS.ADS1115(self.i2c)
        except ValueError:
            print("Oops! ADS1115 not installed")

    def run(self):
        self.trackVoltage()

    def trackVoltage(self):
        while not self.kill.is_set():
            # chan = AnalogIn(ads, ADS.P0)
            # currentVoltage = self.ads.read_adc(self.stoppingPoint.measurmentpin, gain= self.GAIN)
            # if abs(currentVoltage) > 10:
            # print ('Detected voltage at Stopping Point: ', self.stoppingPoint.measurmentpin)
            time.sleep(0.3)
