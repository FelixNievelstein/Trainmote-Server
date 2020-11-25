from .models.ConfigModel import ConfigModel
from pkg_trainmote.stateControllerModule import StateController
from . import gpioservice
from flask import Flask
from flask import request
from flask import abort
from flask import Response
from .powerControllerModule import PowerThread
from .configControllerModule import ConfigController
from . import stateControllerModule
from .libInstaller import LibInstaller
from .databaseControllerModule import DatabaseController
from .stopPointApiController import stopPointApi
from .deviceApiController import deviceApiBlueprint
from .switchApiController import switchApiBlueprint
from .validator import Validator
from . import baseAPI
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
    stateController.setState(stateControllerModule.STATE_CONNECTED)
    return json.dumps({"trainmote": "trainmote.module.felix-nievelstein.de", "version": mVersion})


##
# Endpoints Config
##

@app.route('/trainmote/api/v1/config', methods=["GET"])
def getConfig():
    config = dataBaseController.getConfig()
    if config is not None:
        return json.dumps(config.to_dict()), 200, baseAPI.defaultHeader()
    else:
        abort(404)

@app.route('/trainmote/api/v1/config', methods=["POST"])
def setConfig():
    mJson = request.get_json()
    if mJson is not None:
        validator = Validator()
        if validator.validateDict(mJson, "config_scheme") is False:
            abort(400)

        stops = dataBaseController.getAllStopModels()
        switchs = dataBaseController.getAllSwichtModels()
        switchPowerRelaisIsStop = validator.containsPin(int(mJson["switchPowerRelais"]), stops)
        switchPowerRelaisIsSwitch = validator.containsPin(int(mJson["switchPowerRelais"]), switchs)
        if switchPowerRelaisIsStop or switchPowerRelaisIsSwitch:
            return json.dumps({"error": "Switch power relais pin is already in use"}), 409, baseAPI.defaultHeader()

        powerRelaisIsStop = validator.containsPin(int(mJson["powerRelais"]), stops)
        powerRelaisIsSwitch = validator.containsPin(int(mJson["powerRelais"]), switchs)
        if powerRelaisIsStop or powerRelaisIsSwitch:
            return json.dumps({"error": "Power relais pin is already in use"}), 409, baseAPI.defaultHeader()

        stateRelaisIsStop = validator.containsPin(int(mJson["stateRelais"]), stops)
        stateRelaisIsSwitch = validator.containsPin(int(mJson["stateRelais"]), switchs)
        if stateRelaisIsStop or stateRelaisIsSwitch:
            return json.dumps({"error": "State relais pin is already in use"}), 409, baseAPI.defaultHeader()

        dataBaseController.insertConfig(
            int(mJson["switchPowerRelais"]),
            int(mJson["powerRelais"]),
            int(mJson["stateRelais"])
        )

        if powerThread is not None:
            powerThread.stop()

        config = dataBaseController.getConfig()
        if config.powerRelais is not None:
            setupPowerGPIO(config.powerRelais)
        if config is not None:
            return json.dumps(config.to_dict()), 201, baseAPI.defaultHeader()
        else:
            abort(500)
    else:
        abort(400)

def restart():
    shutDown()
    os.execv(sys.executable, ['python'] + sys.argv)


def shutDown():
    print("Server going down")
    gpioservice.clean()
    if powerThread.is_alive():
        powerThread.kill.set()
        powerThread.isTurningOff = True
        powerThread.join()
    stateController.setState(stateControllerModule.STATE_SHUTDOWN)
    stateController.stop()


def closeClientConnection():
    print("Closing client socket")


def handler(signal, frame):
    shutDown()
    sys.exit(0)
