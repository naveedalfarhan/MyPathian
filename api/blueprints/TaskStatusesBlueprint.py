from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.TaskStatus import TaskStatus

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


TaskStatusesBlueprint = Blueprint("TaskStatusesBlueprint", __name__)


@TaskStatusesBlueprint.route("/api/TaskStatuses", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Task Statuses", "View Task Statuses"])
def taskstatuses_get(query_parameters):
    query_result = g.uow.task_statuses.get_all_taskstatuses(query_parameters)
    return jsonify(query_result.__dict__)


@TaskStatusesBlueprint.route("/api/TaskStatuses/GetAll", methods=["GET"])
@login_required
@require_any_permission({"Manage Task Statuses", "View Task Statuses"})
def task_statuses_get_all():
    return jsonify(result=g.uow.task_statuses.get_all())


@TaskStatusesBlueprint.route("/api/TaskStatuses", methods=["POST"])
@login_required
@from_request_body("model", TaskStatus)
@require_permissions(["Manage Task Statuses"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.task_statuses.does_task_status_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.task_statuses.insert(model)
    return ""


@TaskStatusesBlueprint.route("/api/TaskStatuses/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Task Statuses"])
def get(id):
    c = g.uow.task_statuses.get(id)
    return jsonify(c.__dict__)


@TaskStatusesBlueprint.route("/api/TaskStatuses/<id>", methods=["PUT"])
@login_required
@from_request_body("model", TaskStatus)
@require_permissions(["Manage Task Statuses"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.task_statuses.does_task_status_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    g.uow.task_statuses.update(model)
    return ""


@TaskStatusesBlueprint.route("/api/TaskStatuses/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Task Statuses"])
def delete(id):
    try:
        g.uow.task_statuses.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})