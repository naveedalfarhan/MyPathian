from datetime import datetime
from time import strptime, mktime
from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import pytz
import sys
from api.models.QueryParameters import QueryParameters
from api.models.Task import Task
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions

TasksBlueprint = Blueprint("TasksBlueprint", __name__)


@TasksBlueprint.route("/api/Tasks", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage Tasks', 'View Tasks', 'View Dashboard'])
def tasks_get(query_parameters):
    query_result = g.uow.tasks.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@TasksBlueprint.route("/api/Tasks", methods=["POST"])
@login_required
@from_request_body("model", Task)
@require_permissions(['Manage Tasks'])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.estimated_cost:
        response = jsonify({"message": "Estimated cost is required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Commissioning Group is required."})
        response.status_code = 400
        return response
    if not model.assigned_to_id:
        response = jsonify({"message": "Task must be assigned."})
        response.status_code = 400
        return response
    # TODO: Validate the priority status and type

    try:
        if model.accepted_date:
            model.accepted_date = pytz.UTC.localize(
                datetime.fromtimestamp(mktime(strptime(model.accepted_date[:10], "%Y-%m-%d"))))
        if model.start_date:
            model.start_date = pytz.UTC.localize(
                datetime.fromtimestamp(mktime(strptime(model.start_date[:10], "%Y-%m-%d"))))
        if model.completed_date:
            model.completed_date = pytz.UTC.localize(
                datetime.fromtimestamp(mktime(strptime(model.completed_date[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the dates."})
        response.status_code = 500
        return response

    print "Insert"

    g.uow.tasks.insert(model)
    return ""


@TasksBlueprint.route("/api/Tasks/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Task)
@require_permissions(['Manage Tasks'])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.estimated_cost:
        response = jsonify({"message": "Estimated cost is required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Commissioning Group is required."})
        response.status_code = 400
        return response
    if not model.assigned_to_id:
        response = jsonify({"message": "Task must be assigned."})
        response.status_code = 400
        return response
    # TODO: Validate the priority status and type

    try:
        if model.accepted_date:
            model.accepted_date = pytz.UTC.localize(
                datetime.fromtimestamp(mktime(strptime(model.accepted_date[:10], "%Y-%m-%d"))))
        if model.start_date:
            model.start_date = pytz.UTC.localize(
                datetime.fromtimestamp(mktime(strptime(model.start_date[:10], "%Y-%m-%d"))))
        if model.completed_date:
            model.completed_date = pytz.UTC.localize(
                datetime.fromtimestamp(mktime(strptime(model.completed_date[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the dates."})
        response.status_code = 500
        return response

    g.uow.tasks.update(model)
    return ""


@TasksBlueprint.route("/api/Tasks/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Tasks'])
def get(id):
    task = g.uow.tasks.get(id)
    return jsonify(task.__dict__)


@TasksBlueprint.route("/api/Tasks/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Tasks'])
def delete(id):
    try:
        g.uow.tasks.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})


@TasksBlueprint.route("/api/Tasks/<component_id>/GetAllAvailable", methods=["GET"])
@login_required
@require_any_permission(['Manage Tasks', 'View Tasks'])
def get_all(component_id):
    issues = g.uow.tasks.get_tasks_not_mapped_to_component(component_id)
    return jsonify(data=issues)