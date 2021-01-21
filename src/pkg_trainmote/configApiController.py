from flask import Blueprint
from flask import request
from flask import abort
from . import baseAPI
from .validator import Validator
from . import apiController
import json
from .databaseControllerModule import DatabaseController
from .authentication import auth

configApi = Blueprint('configApi', __name__)

##
# Endpoints Config
##

@configApi.route('/trainmote/api/v1/config', methods=["GET"])
@auth.login_required(role="admin")
def getConfig():
    config = DatabaseController().getConfig()
    if config is not None:
        return json.dumps(config.to_dict()), 200, baseAPI.defaultHeader()
    else:
        abort(404)

@configApi.route('/trainmote/api/v1/config', methods=["POST"])
@auth.login_required(role="admin")
def setConfig():
    mJson = request.get_json()
    if mJson is not None:
        validator = Validator()
        if validator.validateDict(mJson, "config_scheme") is False:
            abort(400)

        stops = DatabaseController().getAllStopModels()
        switchs = DatabaseController().getAllSwichtModels()

        switchPowerRelais = None
        if "switchPowerRelais" in mJson:
            switchPowerRelais = int(mJson["switchPowerRelais"])
            if switchPowerRelais is not None:
                switchPowerRelaisIsStop = validator.containsPin(switchPowerRelais, stops)
                switchPowerRelaisIsSwitch = validator.containsPin(switchPowerRelais, switchs)
                if switchPowerRelaisIsStop or switchPowerRelaisIsSwitch:
                    return json.dumps({"error": "Switch power relais pin is already in use"}), 409, baseAPI.defaultHeader()

        powerRelais = None
        if "powerRelais" in mJson:
            powerRelais = int(mJson["powerRelais"])
            if powerRelais is not None:
                powerRelaisIsStop = validator.containsPin(int(mJson["powerRelais"]), stops)
                powerRelaisIsSwitch = validator.containsPin(int(mJson["powerRelais"]), switchs)
                if powerRelaisIsStop or powerRelaisIsSwitch:
                    return json.dumps({"error": "Power relais pin is already in use"}), 409, baseAPI.defaultHeader()

        stateRelais = None
        if "stateRelais" in mJson:
            stateRelais = int(mJson["stateRelais"])
            if stateRelais is not None:
                stateRelaisIsStop = validator.containsPin(int(mJson["stateRelais"]), stops)
                stateRelaisIsSwitch = validator.containsPin(int(mJson["stateRelais"]), switchs)
                if stateRelaisIsStop or stateRelaisIsSwitch:
                    return json.dumps({"error": "State relais pin is already in use"}), 409, baseAPI.defaultHeader()

        deviceName = None
        if "deviceName" in mJson:
            deviceName = str(mJson["deviceName"])

        DatabaseController().insertConfig(
            switchPowerRelais,
            powerRelais,
            stateRelais,
            deviceName
        )

        if apiController.powerThread is not None:
            apiController.powerThread.stop()

        config = DatabaseController().getConfig()
        if config.powerRelais is not None:
            apiController.setupPowerGPIO(config.powerRelais)
        if config is not None:
            return json.dumps(config.to_dict()), 201, baseAPI.defaultHeader()
        else:
            abort(500)
    else:
        abort(400)
