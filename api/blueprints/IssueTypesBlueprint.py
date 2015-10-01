from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.IssueType import IssueType

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


IssueTypesBlueprint = Blueprint("IssueTypesBlueprint", __name__)


@IssueTypesBlueprint.route("/api/IssueTypes", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Issue Types", "View Issue Types"])
def issuetypes_get(query_parameters):
    query_result = g.uow.issue_types.get_all_issuetypes(query_parameters)
    return jsonify(query_result.__dict__)


@IssueTypesBlueprint.route("/api/IssueTypes/GetAll", methods=["GET"])
@login_required
@require_any_permission({"Manage Issue Types", "View Issue Types"})
def issue_types_get_all():
    return jsonify(result=g.uow.issue_types.get_all())


@IssueTypesBlueprint.route("/api/IssueTypes", methods=["POST"])
@login_required
@from_request_body("model", IssueType)
@require_permissions(["Manage Issue Types"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.issue_statuses.does_issue_status_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.issue_types.insert(model)
    return ""


@IssueTypesBlueprint.route("/api/IssueTypes/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Issue Types"])
def get(id):
    c = g.uow.issue_types.get(id)
    return jsonify(c.__dict__)


@IssueTypesBlueprint.route("/api/IssueTypes/<id>", methods=["PUT"])
@login_required
@from_request_body("model", IssueType)
@require_permissions(["Manage Issue Types"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.issue_statuses.does_issue_status_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    g.uow.issue_types.update(model)
    return ""


@IssueTypesBlueprint.route("/api/IssueTypes/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Issue Types"])
def delete(id):
    try:
        g.uow.issue_types.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})