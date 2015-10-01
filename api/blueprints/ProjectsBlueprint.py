from datetime import datetime
import json
from time import mktime, strptime
from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
import pytz
from api.models.Project import Project
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions

ProjectsBlueprint = Blueprint("ProjectsBlueprint", __name__)


@ProjectsBlueprint.route("/api/Projects", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage Projects', 'View Projects'])
def get_list(query_parameters):
    query_result = g.uow.projects.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@ProjectsBlueprint.route("/api/Projects", methods=["POST"])
@login_required
@from_request_body("model", Project)
@require_permissions(['Manage Projects'])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.start_date or not model.complete_date:
        response = jsonify({"message": "Start date and complete date are required."})
        response.status_code = 400
        return response
    if not model.estimated_cost:
        response = jsonify({"message": "Estimated cost is required."})
        response.status_code = 400
        return response
    try:
        model.start_date = pytz.UTC.localize(
            datetime.fromtimestamp(mktime(strptime(model.start_date[:10], "%Y-%m-%d"))))
        model.complete_date = pytz.UTC.localize(
            datetime.fromtimestamp(mktime(strptime(model.complete_date[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the dates."})
        response.status_code = 500
        return response
    print("insert")
    g.uow.projects.insert(model)
    return ""


@ProjectsBlueprint.route("/api/Projects/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Project)
@require_permissions(['Manage Projects'])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.start_date or not model.complete_date:
        response = jsonify({"message": "Start date and complete date are required."})
        response.status_code = 400
        return response
    if not model.estimated_cost:
        response = jsonify({"message": "Estimated cost is required."})
        response.status_code = 400
        return response
    try:
        model.start_date = pytz.UTC.localize(
            datetime.fromtimestamp(mktime(strptime(model.start_date[:10], "%Y-%m-%d"))))
        model.complete_date = pytz.UTC.localize(
            datetime.fromtimestamp(mktime(strptime(model.complete_date[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the dates."})
        response.status_code = 500
        return response
    g.uow.projects.update(model)
    return ""


@ProjectsBlueprint.route("/api/Projects/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Projects'])
def get(id):
    p = g.uow.projects.get(id)

    p.owner_model = None
    p.comm_authority_model = None
    p.engineer_model = None

    if p.owner_id:
        p.owner_model = g.uow.contacts.get(p.owner_id).__dict__
    if p.comm_authority_id:
        p.comm_authority_model = g.uow.contacts.get(p.comm_authority_id).__dict__
    if p.engineer_id:
        p.engineer_model = g.uow.contacts.get(p.engineer_id).__dict__
    return jsonify(p.__dict__)


@ProjectsBlueprint.route("/api/Projects/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Projects'])
def delete(id):
    try:
        g.uow.projects.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})


@ProjectsBlueprint.route("/api/Projects/GetAll", methods=["GET"])
@login_required
@require_any_permission(['Manage Projects', 'View Projects'])
def get_all():
    raw_data = g.uow.projects.get_all_as_list()
    data = []
    for p in raw_data:
        data.append(p)
    return json.dumps(data)