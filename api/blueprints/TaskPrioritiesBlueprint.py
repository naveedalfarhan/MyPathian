from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.TaskPriority import TaskPriority

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


TaskPrioritiesBlueprint = Blueprint("TaskPrioritiesBlueprint", __name__)


@TaskPrioritiesBlueprint.route("/api/TaskPriorities", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Task Priorities", "View Task Priorities"])
def taskpriorities_get(query_parameters):
    query_result = g.uow.task_priorities.get_all_taskpriorities(query_parameters)
    return jsonify(query_result.__dict__)


@TaskPrioritiesBlueprint.route("/api/TaskPriorities/GetAll", methods=["GET"])
@login_required
@require_any_permission({"Manage Task Priorities", "View Task Priorities"})
def task_priorities_get_all():
    return jsonify(result=g.uow.task_priorities.get_all())


@TaskPrioritiesBlueprint.route("/api/TaskPriorities", methods=["POST"])
@login_required
@from_request_body("model", TaskPriority)
@require_permissions(["Manage Task Priorities"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.task_priorities.does_task_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.task_priorities.insert(model)
    return ""


@TaskPrioritiesBlueprint.route("/api/TaskPriorities/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Task Priorities"])
def get(id):
    c = g.uow.task_priorities.get(id)
    return jsonify(c.__dict__)


@TaskPrioritiesBlueprint.route("/api/TaskPriorities/<id>", methods=["PUT"])
@login_required
@from_request_body("model", TaskPriority)
@require_permissions(["Manage Task Priorities"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.task_priorities.does_task_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    g.uow.task_priorities.update(model)
    return ""


@TaskPrioritiesBlueprint.route("/api/TaskPriorities/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Task Priorities"])
def delete(id):
    try:
        g.uow.task_priorities.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})