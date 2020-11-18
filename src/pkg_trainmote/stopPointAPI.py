from flask import Blueprint
from flask import request
from flask import abort
from flask import Response
from . import baseAPI
from . import gpioservice

stopPointApi = Blueprint('stopPointApi', __name__)

@stopPointApi.route('/trainmote/api/v1/stoppoint/<stop_id>', methods=["GET"])
def stop(stop_id: str):
    if stop_id is None:
        abort(400)
    return gpioservice.getStop(stop_id), 200, baseAPI.defaultHeader()
