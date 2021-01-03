from pkg_trainmote.stateControllerModule import StateController
from . import gpioservice
from flask import Flask
from .powerControllerModule import PowerThread
from .configControllerModule import ConfigController
from . import stateControllerModule
from .libInstaller import LibInstaller
from .databaseControllerModule import DatabaseController
from .stopPointApiController import stopPointApi
from .deviceApiController import deviceApiBlueprint
from .switchApiController import switchApiBlueprint
from .configApiController import configApi
from typing import Optional
import sys
import os
import json
import signal

stateController: Optional[StateController]
dataBaseController: Optional[DatabaseController]
powerThread: Optional[PowerThread]
config: Optional[ConfigController]
app = Flask(__name__)
app.register_blueprint(stopPointApi)
app.register_blueprint(deviceApiBlueprint)
app.register_blueprint(switchApiBlueprint)
app.register_blueprint(configApi)
mVersion: Optional[str] = None

def loadPersistentData():
    if config.loadPreferences():
        if not config.isSQLiteInstalled():
            libInstaller = LibInstaller()
            libInstaller.installSQLite()
            if config.setSQLiteInstalled():
                restart()
            else:
                shutDown()


def setup(version):
    global mVersion
    mVersion = version
    gpioservice.setup()
    global dataBaseController
    dataBaseController = DatabaseController()
    dataBaseController.checkUpdate(version)

    global powerThread
    powerThread = None

    global stateController
    stateController = None

    conf = DatabaseController().getConfig()
    if conf is not None:
        if conf.powerRelais is not None:
            setupPowerGPIO(conf.powerRelais)
        if conf.stateRelais is not None:
            stateController = stateControllerModule.StateController(conf.stateRelais)
            stateController.setState(stateControllerModule.STATE_NOT_CONNECTED)

    global config
    config = ConfigController()
    print("Start webserver")
    app.run(host="0.0.0.0")
    signal.signal(signal.SIGINT, handler)

##
# Setup PowerThread to track user event to shut down.
##
def setupPowerGPIO(pin: int):
    powerThread = PowerThread(pin)
    powerThread.start()

@app.route('/trainmote/api/v1')
def hello_world():
    if stateController is not None:
        stateController.setState(stateControllerModule.STATE_CONNECTED)
    return json.dumps({"trainmote": "trainmote.module.felix-nievelstein.de", "version": mVersion})


def restart():
    shutDown()
    os.execv(sys.executable, ['python'] + sys.argv)


def shutDown():
    print("Server going down")
    gpioservice.clean()


def closeClientConnection():
    print("Closing client socket")


def handler(signal, frame):
    shutDown()
    sys.exit(0)

def stopRunningThreads():
    if powerThread is not None:
        if powerThread.is_alive():
            powerThread.stop()
            powerThread.isTurningOff = True
            powerThread.join()
    if stateController is not None:
        stateController.setState(stateControllerModule.STATE_SHUTDOWN)
        stateController.stop()
