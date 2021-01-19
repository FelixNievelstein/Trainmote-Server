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
from .authentication import auth

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
@auth.login_required(role="admin")
def updateSwitch(switch_id: str):
    mJson = request.get_json()
    if mJson is not None:
        validator = Validator()
        if validator.validateDict(mJson, "switch_update_scheme") is False:
            abort(400)
        try:
            database = DatabaseController()
            exModel = database.getSwitch(switch_id)
            if exModel is None:
                return json.dumps({"error": "Switch for id {} not found".format(switch_id)}), 404, baseAPI.defaultHeader()            
            model = GPIOSwitchPoint.from_dict(mJson, switch_id)
            if model.relais_id is not None and exModel.relais_id is not None and model.relais_id is not exModel.relais_id:
                validator.isAlreadyInUse(int(mJson["relais_id"]))
            updatedSwitch = database.updateSwitch(switch_id, model)
            if updateSwitch is not None:
                if exModel.relais_id != model.relais_id:
                    gpioservice.removeRelais(exModel)
                    gpioservice.addSwitch(model)
                return json.dumps(updatedSwitch.to_dict()), 200, baseAPI.defaultHeader()
            else:
                abort(500)

        except ValueError as e:
            return json.dumps({"error": str(e)}), 409, baseAPI.defaultHeader()
        except Error as e:
            return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()
    else:
        abort(400)


@switchApiBlueprint.route('/trainmote/api/v1/switch/<switch_id>', methods=["DELETE"])
@auth.login_required(role="admin")
def deleteSwitch(switch_id: str):
    if switch_id is None:
        abort(400)
    try:
        database = DatabaseController()
        exModel = database.getSwitch(switch_id)
        if exModel is None:
            return json.dumps({"error": "Switch for id {} not found".format(switch_id)}), 404
        database.deleteSwitchModel(switch_id)
        return "", 205, baseAPI.defaultHeader()
    except Error as e:
        return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()    


@switchApiBlueprint.route('/trainmote/api/v1/switch', methods=["POST"])
@auth.login_required(role="admin")
def addSwitch():
    mJson = request.get_json()
    if mJson is not None:
        if Validator().validateDict(mJson, "switch_scheme") is False:
            abort(400)
        config = DatabaseController().getConfig()
        if config is not None and config.containsPin(mJson["relais_id"]):
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
