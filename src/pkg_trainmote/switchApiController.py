from sqlite3.dbapi2 import Error
from flask import Blueprint
from flask import request
from flask import abort
from flask import Response

from pkg_trainmote.models.GPIORelaisModel import GPIOSwitchPoint
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
    try:
        return gpioservice.getSwitch(switch_id), 200, baseAPI.defaultHeader()
    except ValueError as e:
        return json.dumps({"error": str(e)}), 404, baseAPI.defaultHeader()


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
        validator = Validator()
        if validator.validateDict(mJson, "switch_update_scheme") is False:
            abort(400)
        try:
            database = DatabaseController()
            exModel = database.getSwitch(int(switch_id))
            if exModel is None:
                return json.dumps({"error": "Switch for id {} not found".format(switch_id)}), 404
            model = GPIOSwitchPoint.from_dict(mJson, int(switch_id))
            if model.pin is not None and exModel.pin is not None and model.pin is not exModel.pin:
                validator.isAlreadyInUse(int(mJson["pin"]))
            updatedSwitch = database.updateSwitch(int(switch_id), model)
            if updateSwitch is not None:
                return json.dumps({"model": updatedSwitch.to_dict()})
            else:
                abort(500)

        except ValueError as e:
            return json.dumps({"error": str(e)}), 409, baseAPI.defaultHeader()
        except Error as e:
            return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()
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
