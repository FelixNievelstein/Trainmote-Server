from . import gpioservice
from flask import Flask
from flask import jsonify
from .powerControllerModule import PowerThread
from .configControllerModule import ConfigController
from . import stateControllerModule
from .libInstaller import LibInstaller
from subprocess import call
import logging
import logging.handlers
import argparse
import sys
import os
import time

gpioservice.setup()
gpioservice.loadInitialData()
stateController = stateControllerModule.StateController()
powerThread = PowerThread()
client_sock = None
config = ConfigController()  
app = Flask(__name__)

def loadPersistentData():
    if config.loadPreferences():
        if not config.isSQLiteInstalled():
            libInstaller = LibInstaller()
            libInstaller.installSQLite()
            if config.setSQLiteInstalled():
                restart()
            else: 
                shutDown()
    
@app.route('/')
def hello_world():
    return jsonify(result='Hello World')
  

def restart():
    shutDown()
    os.execv(sys.executable, ['python'] + sys.argv)

def shutDown():
    powerThread.kill.set()
    powerThread.isTurningOff = True
    powerThread.join()
    stateController.setState(stateControllerModule.STATE_SHUTDOWN)
    print ("Server going down")
    stateController.stop()

def closeClientConnection():
    print ("Closing client socket")
    

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")  