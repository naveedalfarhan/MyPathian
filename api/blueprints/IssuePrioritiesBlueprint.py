from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.IssuePriority import IssuePriority

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


IssuePrioritiesBlueprint = Blueprint("IssuePrioritiesBlueprint", __name__)


@IssuePrioritiesBlueprint.route("/api/IssuePriorities", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Issue Priorities", "View Issue Priorities"])
def issuepriorities_get(query_parameters):
    query_result = g.uow.issue_priorities.get_all_issuepriorities(query_parameters)
    return jsonify(query_result.__dict__)


@IssuePrioritiesBlueprint.route("/api/IssuePriorities/GetAll", methods=["GET"])
@login_required
@require_any_permission({"Manage Issue Priorities", "View Issue Priorities"})
def issue_priorities_get_all():
    return jsonify(result=g.uow.issue_priorities.get_all())


@IssuePrioritiesBlueprint.route("/api/IssuePriorities", methods=["POST"])
@login_required
@from_request_body("model", IssuePriority)
@require_permissions(["Manage Issue Priorities"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.issue_priorities.does_issue_priority_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.issue_priorities.insert(model)
    return ""


@IssuePrioritiesBlueprint.route("/api/IssuePriorities/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Issue Priorities"])
def get(id):
    c = g.uow.issue_priorities.get(id)
    return jsonify(c.__dict__)


@IssuePrioritiesBlueprint.route("/api/IssuePriorities/<id>", methods=["PUT"])
@login_required
@from_request_body("model", IssuePriority)
@require_permissions(["Manage Issue Priorities"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.issue_priorities.does_issue_priority_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one priority with that name."})
        response.status_code = 400
        return response

    g.uow.issue_priorities.update(model)
    return ""


@IssuePrioritiesBlueprint.route("/api/IssuePriorities/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Issue Priorities"])
def delete(id):
    try:
        g.uow.issue_priorities.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})