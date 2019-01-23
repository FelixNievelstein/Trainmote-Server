import Adafruit_ADS1x15
import time
import threading

GAIN = 1
adc = Adafruit_ADS1x15.ADS1115()
trackingPoints = [None] * 1

def setupTrackingService():    
    startTracking()

def startTracking():
    # do some stuff
    trackingThread = threading.Thread(target=trackVoltage)
    trackingThread.start()
    # continue doing stuff

def trackVoltage():    
    # Print nice channel column headers.
    print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
    print('-' * 37)
    # Main loop.
    while True:
        # Read all the ADC channel values in a list.
        values = [0]*4

        for i in range(4):
            # Read the specified ADC channel using the previously set gain value.
            values[i] = adc.read_adc(i, gain=GAIN)
        # Print the ADC values.
        if 36 in trackingPoints and abs(values[2]) > 10:
            print 'Detected voltage at Stopping Point'
        # print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
        # Pause for half a second.
        time.sleep(0.25)

def trackStoppingPoint(id):
    trackingPoints.append(id)

def stopTrackSoppingPoint(id): 
    if id in trackingPoints:
        trackingPoints.remove(id)
    