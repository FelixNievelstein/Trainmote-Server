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
from .validator import Validator
from subprocess import call
import sys
import os
import json


gpioservice.setup()
gpioservice.loadInitialData()
stateController = stateControllerModule.StateController()
dataBaseController = DatabaseController()
powerThread = PowerThread()
client_sock = None
config = ConfigController()
app = Flask(__name__)

version: str = '0.3.32'


def loadPersistentData():
    if config.loadPreferences():
        if not config.isSQLiteInstalled():
            libInstaller = LibInstaller()
            libInstaller.installSQLite()
            if config.setSQLiteInstalled():
                restart()
            else:
                shutDown()


def main():
    print("Start webserver")
    app.run(debug=True, host="0.0.0.0")
    stateController.setState(stateControllerModule.STATE_NOT_CONNECTED)


@app.route('/trainmote/api/v1')
def hello_world():
    stateController.setState(stateControllerModule.STATE_CONNECTED)
    return json.dumps({"trainmote": "trainmote.module.felix-nievelstein.de", "version": version})

# Endpoint Switch


@app.route('/trainmote/api/v1/switch/<switch_id>', methods=["GET"])
def switch(switch_id: str):
    if switch_id is None:
        abort(400)
    return gpioservice.getSwitch(switch_id)


@app.route('/trainmote/api/v1/switch/<switch_id>', methods=["PATCH"])
def setSwitch(switch_id: str):
    if switch_id is None:
        abort(400)
    try:
        return gpioservice.setSwitch(switch_id)
    except ValueError as e:
        return json.dumps(str(e)), 400


@app.route('/trainmote/api/v1/switch/<switch_id>', methods=["DELETE"])
def deleteSwitch(switch_id: str):
    if switch_id is None:
        abort(400)
    dataBaseController.deleteSwitchModel(int(switch_id))
    return 'ok'


@app.route('/trainmote/api/v1/switch', methods=["POST"])
def addSwitch():
    mJson = request.get_json()
    if mJson is not None:
        if Validator().validateDict(mJson, "switch_scheme") is False:
            abort(400)
        result = gpioservice.configSwitch(mJson)
        if result is not None:
            return result
        else:
            abort(406)
    else:
        abort(400)


@app.route('/trainmote/api/v1/switch/all')
def getAllSwitches():
    return Response(gpioservice.getAllSwitches(), mimetype="application/json")

# Endpoint StopPoint


@app.route('/trainmote/api/v1/stoppoint/<stop_id>', methods=["GET", "PATCH"])
def stop(stop_id: str):
    if stop_id is None:
        abort(400)
    if request.method == "PATCH":
        try:
            return gpioservice.setStop(stop_id)
        except ValueError as e:
            return e.args, 400
    else:
        return gpioservice.getStop(stop_id)


@app.route('/trainmote/api/v1/stoppoint/<stop_id>', methods=["DELETE"])
def deleteStop(stop_id: str):
    if stop_id is None:
        abort(400)
    dataBaseController.deleteStopModel(int(stop_id))
    return 'ok'


@app.route('/trainmote/api/v1/stoppoint', methods=["POST"])
def addStop():
    mJson = request.get_json()
    if mJson is not None:
        if Validator().validateDict(mJson, "stop_scheme") is False:
            abort(400)
        result = gpioservice.configStop(mJson)
        if result is not None:
            return result
        else:
            abort(406)
    else:
        abort(400)


@app.route('/trainmote/api/v1/stoppoint/all')
def getAllStops():
    return Response(gpioservice.getAllStopPoints(), mimetype="application/json")


def restart():
    shutDown()
    os.execv(sys.executable, ['python'] + sys.argv)


def shutDown():
    powerThread.kill.set()
    powerThread.isTurningOff = True
    powerThread.join()
    stateController.setState(stateControllerModule.STATE_SHUTDOWN)
    print("Server going down")
    stateController.stop()


def closeClientConnection():
    print("Closing client socket")


if __name__ == '__main__':
    main()
