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
from .authentication import auth


programApi = Blueprint('programApi', __name__)
##
# Endpoint Program
##

@programApi.route('/trainmote/api/v1/control/program/start/<program_id>', methods=["PATCH"])
def startProgram(program_id: str):
    if program_id is None:
        abort(400)
    try:
        return "", 200
    except ValueError as e:
        return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()

@programApi.route('/trainmote/api/v1/control/program/stop/<program_id>', methods=["PATCH"])
def stopProgram(program_id: str):
    if program_id is None:
        abort(400)
    try:
        return "", 200
    except ValueError as e:
        return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()


@programApi.route('/trainmote/api/v1/program/<program_id>', methods=["PATCH"])
@auth.login_required(role="admin")
def updateProgram(program_id: str):
    mJson = request.get_json()
    if mJson is not None:
        validator = Validator()
        if validator.validateDict(mJson, "program_update_scheme") is False:
            abort(400)
        try:
            database = DatabaseController()

            """ exModel = database.getStop(program_id)
            if exModel is None:
                return json.dumps({"error": "Program for id {} not found".format(program_id)}), 404, baseAPI.defaultHeader()
            model = GPIOStoppingPoint.from_dict(mJson, stop_id)
            if (
                model.relais_id is not None
                and exModel.relais_id is not None
                and model.relais_id is not exModel.relais_id
            ):
                validator.isAlreadyInUse(int(mJson["relais_id"]))
            updateStop = database.updateStop(stop_id, model)
            if updateStop is not None:
                if exModel.relais_id != model.relais_id:
                    gpioservice.removeRelais(exModel)
                    gpioservice.addRelais(model)
                return json.dumps(updateStop.to_dict()), 200, baseAPI.defaultHeader()
            else: """
            abort(500)

        except ValueError as e:
            return json.dumps({"error": str(e)}), 409, baseAPI.defaultHeader()
        except Error as e:
            return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()
    else:
        abort(400)


@programApi.route('/trainmote/api/v1/program/<program_id>', methods=["DELETE"])
@auth.login_required(role="admin")
def deleteStop(program_id: str):
    if program_id is None:
        abort(400)
    try:
        database = DatabaseController()
        """ exModel = database.getStop(stop_id)
        if exModel is None:
            return json.dumps({"error": "Stop for id {} not found".format(stop_id)}), 404
        database.deleteStopModel(stop_id) """
        return "", 205, baseAPI.defaultHeader()
    except Error as e:
        return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()


@programApi.route('/trainmote/api/v1/program', methods=["POST"])
@auth.login_required(role="admin")
def addStop():
    mJson = request.get_json()
    if mJson is not None:
        if Validator().validateDict(mJson, "program_scheme") is False:
            abort(400)

        config = DatabaseController().getConfig()
        if config is not None and config.containsPin(mJson["relais_id"]):
            return json.dumps({"error": "Pin is already in use as power relais"}), 409, baseAPI.defaultHeader()

        try:
            return gpioservice.createStop(mJson), 201, baseAPI.defaultHeader()
        except ValueError as e:
            return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()
    else:
        abort(400)


@programApi.route('/trainmote/api/v1/program/all', methods=["GET"])
def getAllStops():
    return Response(gpioservice.getAllStopPoints(), mimetype="application/json"), 200, baseAPI.defaultHeader()


@programApi.route('/trainmote/api/v1/program/<program_id>', methods=["GET"])
def stop(program_id: str):
    if program_id is None:
        abort(400)
    return gpioservice.getStop(program_id), 200, baseAPI.defaultHeader()
