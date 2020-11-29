from flask import Blueprint
from . import baseAPI
from . import deviceController
from . import gpioservice
from .apiController import stateController, powerThread

import json


deviceApiBlueprint = Blueprint('deviceApi', __name__)

@deviceApiBlueprint.route('/trainmote/api/v1/device/restart', methods=["POST"])
def restartDevice():
    try:
        deviceController.restartAfter(2)
        stopRunningThreads()
        gpioservice.clean()
        return "", 200
    except PermissionError as e:
        return json.dumps({"error": str(e)}), 401, baseAPI.defaultHeader()

@deviceApiBlueprint.route('/trainmote/api/v1/device/shutdown', methods=["POST"])
def shutdownDevice():
    try:
        deviceController.shutdownAfter(2)
        stopRunningThreads()
        gpioservice.clean()
        return "", 200
    except PermissionError as e:
        return json.dumps({"error": str(e)}), 401, baseAPI.defaultHeader()

@deviceApiBlueprint.route('/trainmote/api/v1/device/update', methods=["POST"])
def updateDevice():    
    deviceController.update()
    stopRunningThreads()
    gpioservice.clean()
    return "", 200

def stopRunningThreads():
    if stateController is not None:
        stateController.stop()
    if powerThread is not None:
        powerThread.stop()
