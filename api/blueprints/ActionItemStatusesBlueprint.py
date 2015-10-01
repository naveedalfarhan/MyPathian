from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.ActionItemStatus import ActionItemStatus

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


ActionItemStatusesBlueprint = Blueprint("ActionItemStatusesBlueprint", __name__)


@ActionItemStatusesBlueprint.route("/api/ActionItemStatuses", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Action Item Statuses", "View Action Item Statuses"])
def actionitemstatuses_get(query_parameters):
    query_result = g.uow.action_item_statuses.get_all_actionitemstatuses(query_parameters)
    return jsonify(query_result.__dict__)


@ActionItemStatusesBlueprint.route("/api/ActionItemStatuses", methods=["POST"])
@login_required
@from_request_body("model", ActionItemStatus)
@require_permissions(["Manage Action Item Statuses"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.action_item_statuses.does_status_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one status with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.action_item_statuses.insert(model)
    return ""


@ActionItemStatusesBlueprint.route("/api/ActionItemStatuses/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Action Item Statuses"])
def get(id):
    c = g.uow.action_item_statuses.get(id)
    return jsonify(c.__dict__)


@ActionItemStatusesBlueprint.route("/api/ActionItemStatuses/<id>", methods=["PUT"])
@login_required
@from_request_body("model", ActionItemStatus)
@require_permissions(["Manage Action Item Statuses"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.action_item_statuses.does_status_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one status with that name."})
        response.status_code = 400
        return response

    g.uow.action_item_statuses.update(model)
    return ""


@ActionItemStatusesBlueprint.route("/api/ActionItemStatuses/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Action Item Statuses"])
def delete(id):
    try:
        g.uow.action_item_statuses.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})