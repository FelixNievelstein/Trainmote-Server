from . import gpioservice
from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
from flask import Response
from .powerControllerModule import PowerThread
from .configControllerModule import ConfigController
from . import stateControllerModule
from .libInstaller import LibInstaller
from .validator import Validator
from subprocess import call
import logging
import logging.handlers
import argparse
import sys
import os
import time
import json


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


def main():
    print("Start webserver")
    app.run(debug=True, host="0.0.0.0")


@app.route('/')
def hello_world():
    return jsonify(result='Hello World')

# Endpoint Switch


@app.route('/trainmote/api/v1/switch/<switch_id>', methods=["GET", "PATCH"])
def switch(switch_id: str):
    if switch_id is None:
        abort(400)
    if request.method == "PATCH":
        return gpioservice.setSwitch(switch_id)
    else:
        return gpioservice.getSwitch(switch_id)


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
            abort(400)
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
        return gpioservice.setStop(stop_id)
    else:
        return gpioservice.getStop(stop_id)


@app.route('/trainmote/api/v1/stoppoint', methods=["POST"])
def addStop():
    if request.get_json() is not None:
        if Validator().validateDict(request.get_json, ["measurmentId", "id"]) is False:
            abort(400)
        result = gpioservice.configStop(request.get_json())
        if result is not None:
            return result
        else:
            abort(400)
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
