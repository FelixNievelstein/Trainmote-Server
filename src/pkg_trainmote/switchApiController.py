from flask import Blueprint
from flask import request
from flask import abort
from flask import Response
from . import baseAPI
from . import gpioservice
from .validator import Validator
import json
from .databaseControllerModule import DatabaseController

switchApiBlueprint = Blueprint('switchApi', __name__)

##
# Endpoint Switch
##

@switchApiBlueprint.route('/trainmote/api/v1/switch/<switch_id>', methods=["GET"])
def switch(switch_id: str):
    if switch_id is None:
        abort(400)
    return gpioservice.getSwitch(switch_id), 200, baseAPI.defaultHeader()


@switchApiBlueprint.route('/trainmote/api/v1/control/switch/<switch_id>', methods=["PATCH"])
def setSwitch(switch_id: str):
    if switch_id is None:
        abort(400)
    try:
        return gpioservice.setSwitch(switch_id), 200, baseAPI.defaultHeader()
    except ValueError as e:
        return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()


@switchApiBlueprint.route('/trainmote/api/v1/switch/<switch_id>', methods=["PATCH"])
def updateSwitch(switch_id: str):
    mJson = request.get_json()
    if mJson is not None:
        abort(501)
    else:
        abort(400)


@switchApiBlueprint.route('/trainmote/api/v1/switch/<switch_id>', methods=["DELETE"])
def deleteSwitch(switch_id: str):
    if switch_id is None:
        abort(400)
    DatabaseController().deleteSwitchModel(int(switch_id)), 205, baseAPI.defaultHeader()
    return 'ok'


@switchApiBlueprint.route('/trainmote/api/v1/switch', methods=["POST"])
def addSwitch():
    mJson = request.get_json()
    if mJson is not None:
        if Validator().validateDict(mJson, "switch_scheme") is False:
            abort(400)
        config = DatabaseController().getConfig()
        if config is not None and config.containsPin(mJson["id"]):
            return json.dumps({"error": "Pin is already in use as power relais"}), 409, baseAPI.defaultHeader()

        try:
            return gpioservice.createSwitch(mJson), 201, baseAPI.defaultHeader()
        except ValueError as e:
            return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()
    else:
        abort(400)


@switchApiBlueprint.route('/trainmote/api/v1/switch/all')
def getAllSwitches():
    return Response(gpioservice.getAllSwitches(), mimetype="application/json"), 200, baseAPI.defaultHeader()
