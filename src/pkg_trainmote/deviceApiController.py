from flask import Blueprint
from . import baseAPI
from . import deviceController
from . import gpioservice
from . import apiController

import json


deviceApiBlueprint = Blueprint('deviceApi', __name__)

@deviceApiBlueprint.route('/trainmote/api/v1/device/restart', methods=["POST"])
def restartDevice():
    try:
        deviceController.restartAfter(2)
        apiController.stopRunningThreads()
        gpioservice.clean()
        return "", 200
    except PermissionError as e:
        return json.dumps({"error": str(e)}), 401, baseAPI.defaultHeader()

@deviceApiBlueprint.route('/trainmote/api/v1/device/shutdown', methods=["POST"])
def shutdownDevice():
    try:
        deviceController.shutdownAfter(2)
        apiController.stopRunningThreads()
        gpioservice.clean()
        return "", 200
    except PermissionError as e:
        return json.dumps({"error": str(e)}), 401, baseAPI.defaultHeader()

@deviceApiBlueprint.route('/trainmote/api/v1/device/update', methods=["POST"])
def updateDevice():
    deviceController.update()
    apiController.stopRunningThreads()
    gpioservice.clean()
    return "", 200
