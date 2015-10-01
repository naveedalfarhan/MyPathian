from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.ActionItemType import ActionItemType

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


ActionItemTypesBlueprint = Blueprint("ActionItemTypesBlueprint", __name__)


@ActionItemTypesBlueprint.route("/api/ActionItemTypes", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Action Item Types", "View Action Item Types"])
def actionitemtypes_get(query_parameters):
    query_result = g.uow.action_item_types.get_all_actionitemtypes(query_parameters)
    return jsonify(query_result.__dict__)


@ActionItemTypesBlueprint.route("/api/ActionItemTypes", methods=["POST"])
@login_required
@from_request_body("model", ActionItemType)
@require_permissions(["Manage Action Item Types"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.action_item_types.does_type_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one status with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.action_item_types.insert(model)
    return ""


@ActionItemTypesBlueprint.route("/api/ActionItemTypes/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Action Item Types"])
def get(id):
    c = g.uow.action_item_types.get(id)
    return jsonify(c.__dict__)


@ActionItemTypesBlueprint.route("/api/ActionItemTypes/<id>", methods=["PUT"])
@login_required
@from_request_body("model", ActionItemType)
@require_permissions(["Manage Action Item Types"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.action_item_types.does_type_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one status with that name."})
        response.status_code = 400
        return response

    g.uow.action_item_types.update(model)
    return ""


@ActionItemTypesBlueprint.route("/api/ActionItemTypes/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Action Item Types"])
def delete(id):
    try:
        g.uow.action_item_types.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})