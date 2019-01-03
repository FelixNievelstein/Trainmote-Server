import logging
import logging.handlers
import argparse
import sys
import os
import time
import json
from bluetooth import *
import RPi.GPIO as GPIO

P_Switch1 = 29 # switch 1
P_Switch2 = 31 # switch 2
P_Switch3 = 33 # switch 3

class LoggerHelper(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

def switchPin(pin):        
    if GPIO.input(pin):
        GPIO.output(pin, GPIO.LOW)
        print "GPIO Low" + pin
    else:
        GPIO.output(pin, GPIO.HIGH)
        print "GPIO High" + pin

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(P_Switch1, GPIO.OUT)
    GPIO.setup(P_Switch2, GPIO.OUT)
    GPIO.setup(P_Switch3, GPIO.OUT)


def setup_logging():
    # Default logging settings
    LOG_FILE = "/var/log/bluetoothservice.log"
    LOG_LEVEL = logging.INFO

    # Define and parse command line arguments
    argp = argparse.ArgumentParser(description="Raspberry PI Bluetooth Server")
    argp.add_argument("-l", "--log", help="log (default '" + LOG_FILE + "')")

    # Grab the log file from arguments
    args = argp.parse_args()
    if args.log:
        LOG_FILE = args.log

    # Setup the logger
    logger = logging.getLogger(__name__)
    # Set the log level
    logger.setLevel(LOG_LEVEL)
    # Make a rolling event log that resets at midnight and backs-up every 3 days
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE,
        when="midnight",
        backupCount=3)

    # Log messages should include time stamp and log level
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # Attach the formatter to the handler
    handler.setFormatter(formatter)
    # Attach the handler to the logger
    logger.addHandler(handler)

    # Replace stdout with logging to file at INFO level
    sys.stdout = LoggerHelper(logger, logging.INFO)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = LoggerHelper(logger, logging.ERROR)

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

# Main loop
def main():
    
    setup()

    print "Starting main"
    # Setup logging
    # setup_logging()
    print "Setup Logging finished"
    # We need to wait until Bluetooth init is done
    time.sleep(10)
    print "Bluetooth initalised"

    # Make device visible
    os.system("hciconfig hci0 piscan")

    # Create a new server socket using RFCOMM protocol
    server_sock = BluetoothSocket(RFCOMM)
    # Bind to any port
    server_sock.bind(("", PORT_ANY))
    # Start listening
    server_sock.listen(1)

    # Get the port the server socket is listening
    port = server_sock.getsockname()[1]

    # The service UUID to advertise
    uuid = "aaabf455-b0e1-4b88-b9c8-184e53f15663"

    # Start advertising the service
    advertise_service(server_sock, "TrainmoteServer",
                       service_id=uuid,
                       service_classes=[uuid, SERIAL_PORT_CLASS],
                       profiles=[SERIAL_PORT_PROFILE])

    # These are the operations the service supports
    # Feel free to add more
    operations = ["ping", "example"]

    # Main Bluetooth server loop
    client_sock = None
    while True:                

        try:                        
            # This will block until we get a new connection
            if client_sock is None:
                print "Waiting for connection on RFCOMM channel %d" % port
                client_sock, client_info = server_sock.accept()
                print "Accepted connection from ", client_info

            # Read the data sent by the client
            data = client_sock.recv(1024)
            if len(data) == 0:
                break

            print "Received [%s]" % data

            # Handle the request
            if is_json(data):
                jsonData = json.loads(data)                                
                switchPin(jsonData["id"])
                    
                response = "msg:Setting GPIO"                
            # Insert more here
            else:
                response = "msg:Not supported"

            client_sock.send(response)
            print "Sent back [%s]" % response

        except IOError:
            pass

        except KeyboardInterrupt:

            if client_sock is not None:
                client_sock.close()

            server_sock.close()

            print "Server going down"
            break



main()