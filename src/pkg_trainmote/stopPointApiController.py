from sqlite3.dbapi2 import Error
from flask import Blueprint
from flask import request
from flask import abort
from flask import Response

from pkg_trainmote.models.GPIORelaisModel import GPIOStoppingPoint
from . import baseAPI
from . import gpioservice
from .validator import Validator
import json
from .databaseControllerModule import DatabaseController


stopPointApi = Blueprint('stopPointApi', __name__)
##
# Endpoint StopPoint
##

@stopPointApi.route('/trainmote/api/v1/control/stoppoint/<stop_id>', methods=["PATCH"])
def setStop(stop_id: str):
    if stop_id is None:
        abort(400)
    try:
        return gpioservice.setStop(stop_id), 200, baseAPI.defaultHeader()
    except ValueError as e:
        return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()


@stopPointApi.route('/trainmote/api/v1/stoppoint/<stop_id>', methods=["PATCH"])
def updateStop(stop_id: str):
    mJson = request.get_json()
    if mJson is not None:
        validator = Validator()
        if validator.validateDict(mJson, "stop_update_scheme") is False:
            abort(400)
        try:
            database = DatabaseController()
            exModel = database.getStop(int(stop_id))
            if exModel is None:
                return json.dumps({"error": "Stop for id {} not found".format(stop_id)}), 404
            model = GPIOStoppingPoint.from_dict(mJson, int(stop_id))
            if model.pin is not None and exModel.pin is not None and model.pin is not exModel.pin:
                validator.isAlreadyInUse(int(mJson["pin"]))
            updateStop = database.updateStop(int(stop_id), model)
            if updateStop is not None:
                return json.dumps({"model": updateStop.to_dict()})
            else:
                abort(500)

        except ValueError as e:
            return json.dumps({"error": str(e)}), 409, baseAPI.defaultHeader()
        except Error as e:
            return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()
    else:
        abort(400)


@stopPointApi.route('/trainmote/api/v1/stoppoint/<stop_id>', methods=["DELETE"])
def deleteStop(stop_id: str):
    if stop_id is None:
        abort(400)
    DatabaseController().deleteStopModel(int(stop_id)), 205, baseAPI.defaultHeader()
    return 'ok'


@stopPointApi.route('/trainmote/api/v1/stoppoint', methods=["POST"])
def addStop():
    mJson = request.get_json()
    if mJson is not None:
        if Validator().validateDict(mJson, "stop_scheme") is False:
            abort(400)

        config = DatabaseController().getConfig()
        if config is not None and config.containsPin(mJson["id"]):
            return json.dumps({"error": "Pin is already in use as power relais"}), 409, baseAPI.defaultHeader()

        try:
            return gpioservice.createStop(mJson), 201, baseAPI.defaultHeader()
        except ValueError as e:
            return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()
    else:
        abort(400)


@stopPointApi.route('/trainmote/api/v1/stoppoint/all', methods=["GET"])
def getAllStops():
    return Response(gpioservice.getAllStopPoints(), mimetype="application/json"), 200, baseAPI.defaultHeader()


@stopPointApi.route('/trainmote/api/v1/stoppoint/<stop_id>', methods=["GET"])
def stop(stop_id: str):
    if stop_id is None:
        abort(400)
    return gpioservice.getStop(stop_id), 200, baseAPI.defaultHeader()
