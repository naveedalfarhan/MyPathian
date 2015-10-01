from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.TaskType import TaskType

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


TaskTypesBlueprint = Blueprint("TaskTypesBlueprint", __name__)


@TaskTypesBlueprint.route("/api/TaskTypes", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Task Types", "View Task Types"])
def tasktypes_get(query_parameters):
    query_result = g.uow.task_types.get_all_tasktypes(query_parameters)
    return jsonify(query_result.__dict__)


@TaskTypesBlueprint.route("/api/TaskTypes/GetAll", methods=["GET"])
@login_required
@require_any_permission({"Manage Task Types", "View Task Types"})
def task_types_get_all():
    return jsonify(result=g.uow.task_types.get_all())


@TaskTypesBlueprint.route("/api/TaskTypes", methods=["POST"])
@login_required
@from_request_body("model", TaskType)
@require_permissions(["Manage Task Types"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.task_types.does_task_type_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.task_types.insert(model)
    return ""


@TaskTypesBlueprint.route("/api/TaskTypes/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Task Types"])
def get(id):
    c = g.uow.task_types.get(id)
    return jsonify(c.__dict__)


@TaskTypesBlueprint.route("/api/TaskTypes/<id>", methods=["PUT"])
@login_required
@from_request_body("model", TaskType)
@require_permissions(["Manage Task Types"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.task_types.does_task_type_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    g.uow.task_types.update(model)
    return ""


@TaskTypesBlueprint.route("/api/TaskTypes/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Task Types"])
def delete(id):
    try:
        g.uow.task_types.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})