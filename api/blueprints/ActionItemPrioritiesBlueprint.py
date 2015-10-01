from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.ActionItemPriority import ActionItemPriority

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


ActionItemPrioritiesBlueprint = Blueprint("ActionItemPrioritiesBlueprint", __name__)


@ActionItemPrioritiesBlueprint.route("/api/ActionItemPriorities", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Action Item Priorities", "View Action Item Priorities"])
def actionitempriorities_get(query_parameters):
    query_result = g.uow.action_item_priorities.get_all_actionitempriorities(query_parameters)
    return jsonify(query_result.__dict__)


@ActionItemPrioritiesBlueprint.route("/api/ActionItemPriorities", methods=["POST"])
@login_required
@from_request_body("model", ActionItemPriority)
@require_permissions(["Manage Action Item Priorities"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    # The api (not the ui) should not allow you to add a priority with the same name. This is the reason why it's
    # getting added here.
    if g.uow.action_item_priorities.does_priority_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    print("")
    g.uow.action_item_priorities.insert(model)
    return ""


@ActionItemPrioritiesBlueprint.route("/api/ActionItemPriorities/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Action Item Priorities"])
def get(id):
    c = g.uow.action_item_priorities.get(id)
    return jsonify(c.__dict__)


@ActionItemPrioritiesBlueprint.route("/api/ActionItemPriorities/<id>", methods=["PUT"])
@login_required
@from_request_body("model", ActionItemPriority)
@require_permissions(["Manage Action Item Priorities"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.action_item_priorities.does_priority_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    g.uow.action_item_priorities.update(model)
    return ""


@ActionItemPrioritiesBlueprint.route("/api/ActionItemPriorities/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Action Item Priorities"])
def delete(id):
    try:
        g.uow.action_item_priorities.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})