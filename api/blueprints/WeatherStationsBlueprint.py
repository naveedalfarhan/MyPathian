import json
import sys

from flask import abort, jsonify, Blueprint, g

from flask.ext.login import login_required
from ..models.WeatherStation import WeatherStation
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


WeatherStationsBlueprint = Blueprint("WeatherStationsBlueprint", __name__)


@WeatherStationsBlueprint.route("/api/weatherstations", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_any_permission(["View Weather Stations", "Manage Weather Stations"])
def get_all(query_parameters):
    query_result = g.uow.weather_stations.get_all(query_parameters)
    return jsonify(query_result.__dict__)

@WeatherStationsBlueprint.route("/api/weatherstations/list", methods=["GET"])
def get_all_list():
    weatherstations = g.uow.weather_stations.get_all_list()
    return json.dumps(weatherstations)


@WeatherStationsBlueprint.route("/api/weatherstations/<ws_id>", methods=["GET"])
@login_required
@require_permissions(["Manage Weather Stations"])
def get(ws_id):
    ws = g.uow.weather_stations.get_by_id(ws_id)
    if ws is None:
        abort(400)
    else:
        return jsonify(ws.__dict__)


@WeatherStationsBlueprint.route("/api/weatherstations", methods=["POST"])
@from_request_body("ws", WeatherStation)
@login_required
@require_permissions(["Manage Weather Stations"])
def insert(ws):
    print("insert")
    g.uow.weather_stations.insert(ws)
    return ""


@WeatherStationsBlueprint.route("/api/weatherstations/<ws_id>", methods=["PUT"])
@from_request_body("ws", WeatherStation)
@login_required
@require_permissions(["Manage Weather Stations"])
def update(ws_id, ws):
    ws.id = ws_id
    g.uow.weather_stations.update(ws)
    return ""


@WeatherStationsBlueprint.route("/api/weatherstations/<ws_id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Weather Stations"])
def delete(ws_id):
    try:
        g.uow.weather_stations.delete(ws_id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})