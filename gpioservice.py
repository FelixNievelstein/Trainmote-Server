import json
import RPi.GPIO as GPIO


P_Switch1 = 29 # switch 1
P_Switch2 = 31 # switch 2
P_Switch3 = 33 # switch 3

def switchPin(pin):        
    if GPIO.input(pin):
        GPIO.output(pin, GPIO.LOW)
    else:
        GPIO.output(pin, GPIO.HIGH)

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(P_Switch1, GPIO.OUT)
    GPIO.setup(P_Switch2, GPIO.OUT)
    GPIO.setup(P_Switch3, GPIO.OUT)


def receivedMessage(message):
    if is_json(message):
        jsonData = json.loads(message)                                
        switchPin(int(jsonData["id"]))
            
        return "msg:Setting GPIO"                
    # Insert more here
    else:
        return "msg:Not supported"

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True