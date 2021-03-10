from sqlite3.dbapi2 import Error
from flask import Blueprint
from flask import request
from flask import abort
from flask import Response

from .programMachine import ProgramMachine

from . import baseAPI
from .validators.validator import Validator
import json
from .databaseControllerModule import DatabaseController
from .authentication import auth
from .models.Program import Program


programApi = Blueprint('programApi', __name__)
programMachine = ProgramMachine()
##
# Endpoint Program
##

@programApi.route('/trainmote/api/v1/control/program/start/<program_id>', methods=["PATCH"])
def startProgram(program_id: str):
    if program_id is None:
        abort(400)
    try:
        database = DatabaseController()
        exModel = database.getProgram(program_id)
        if exModel is None:
            return json.dumps({"error": "Program for id {} not found".format(program_id)}), 404
        programMachine.start(exModel)
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
def deleteProgram(program_id: str):
    if program_id is None:
        abort(400)
    try:
        database = DatabaseController()
        exModel = database.getProgram(program_id)
        if exModel is None:
            return json.dumps({"error": "Program for id {} not found".format(program_id)}), 404
        database.deleteProgram(program_id)
        return "", 205, baseAPI.defaultHeader()
    except Error as e:
        return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()


@programApi.route('/trainmote/api/v1/program', methods=["POST"])
@auth.login_required(role="admin")
def addProgram():
    mJson = request.get_json()
    if mJson is not None:
        try:
            programModel = Program.from_Json(mJson)
            database = DatabaseController()
            programId = database.insertProgram(programModel.name)
            if programId is None:
                abort(500)

            programPk = database.getProgramPk(programId)
            if programPk is None:
                abort(500)

            for action in programModel.actions:
                database.insertAction(action, programPk)

            dbProgram = database.getProgram(programId)
            if dbProgram is None:
                abort(500)

            return json.dumps(dbProgram.to_dict()), 200, baseAPI.defaultHeader()
        except ValueError as e:
            return json.dumps({"error": str(e)}), 400, baseAPI.defaultHeader()
    else:
        abort(400)


@programApi.route('/trainmote/api/v1/program/all', methods=["GET"])
def getAllPrograms():
    jsonResponse = json.dumps([ob.to_dict() for ob in DatabaseController().getAllPrograms()])
    return Response(jsonResponse, mimetype="application/json"), 200, baseAPI.defaultHeader()


@programApi.route('/trainmote/api/v1/program/<program_id>', methods=["GET"])
def program(program_id: str):
    if program_id is None:
        abort(400)
    return json.dumps(DatabaseController().getProgram(program_id).to_dict()), 200, baseAPI.defaultHeader()
