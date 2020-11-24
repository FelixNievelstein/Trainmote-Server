from flask import Blueprint
from flask import request
from flask import abort
from flask import Response
from . import baseAPI
from . import deviceController
from . import gpioservice


deviceApiBlueprint = Blueprint('deviceApi', __name__)

@deviceApiBlueprint.route('/trainmote/api/v1/device/restart', methods=["POST"])
def restartDevice():
    gpioservice.clean()
    timer = deviceController.RestartTimer()
    timer.start()
    return "", 200

@deviceApiBlueprint.route('/trainmote/api/v1/device/shutdown', methods=["POST"])
def shutdownDevice():
    gpioservice.clean()
    timer = deviceController.ShutDownTimer()
    timer.start()
    return "", 200
