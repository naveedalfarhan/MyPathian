from datetime import datetime
from time import mktime, strptime
from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import pytz
import sys
from api.models.ECO import Eco
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions

EcoBlueprint = Blueprint("EcoBlueprint", __name__)


@EcoBlueprint.route("/api/Eco", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage ECO', 'View ECO'])
def get_all(query_parameters):
    query_result = g.uow.eco.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@EcoBlueprint.route("/api/Eco", methods=["POST"])
@login_required
@from_request_body("model", Eco)
@require_permissions(['Manage ECO'])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.project_id:
        response = jsonify({"message": "Project is required."})
        response.status_code = 400
        return response
    if not model.reduction_goal:
        response = jsonify({"message": "Reduction Goal is required."})
        response.status_code = 400
        return response
    if not model.original_date:
        response = jsonify({"message": "Original Date is required."})
        response.status_code = 400
        return response
    if not model.completion_goal:
        response = jsonify({"message": "Completion Goal is required."})
        response.status_code = 400
        return response
    try:
        model.original_date = pytz.UTC.localize(
            datetime.fromtimestamp(mktime(strptime(model.original_date[:10], "%Y-%m-%d"))))
        model.completion_goal = pytz.UTC.localize(
            datetime.fromtimestamp(mktime(strptime(model.completion_goal[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the dates."})
        response.status_code = 500
        return response

    print "Insert"

    g.uow.eco.insert(model)
    return ""


@EcoBlueprint.route("/api/Eco/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Eco)
@require_permissions(['Manage ECO'])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.project_id:
        response = jsonify({"message": "Project is required."})
        response.status_code = 400
        return response
    if not model.reduction_goal:
        response = jsonify({"message": "Reduction Goal is required."})
        response.status_code = 400
        return response
    if not model.original_date:
        response = jsonify({"message": "Original Date is required."})
        response.status_code = 400
        return response
    if not model.completion_goal:
        response = jsonify({"message": "Completion Goal is required."})
        response.status_code = 400
        return response
    try:
        model.original_date = pytz.UTC.localize(
            datetime.fromtimestamp(mktime(strptime(model.original_date[:10], "%Y-%m-%d"))))
        model.completion_goal = pytz.UTC.localize(
            datetime.fromtimestamp(mktime(strptime(model.completion_goal[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the dates."})
        response.status_code = 500
        return response

    g.uow.eco.update(model)
    return ""


@EcoBlueprint.route("/api/Eco/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage ECO'])
def get(id):
    eco = g.uow.eco.get(id)
    eco.project_model = g.uow.projects.get(eco.project_id).__dict__
    return jsonify(eco.__dict__)


@EcoBlueprint.route("/api/Eco/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage ECO'])
def delete(id):
    try:
        g.uow.eco.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})