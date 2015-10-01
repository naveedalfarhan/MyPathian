from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.IssueStatus import IssueStatus

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


IssueStatusesBlueprint = Blueprint("IssueStatusesBlueprint", __name__)


@IssueStatusesBlueprint.route("/api/IssueStatuses", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Issue Statuses", "View Issue Statuses"])
def issuestatuses_get(query_parameters):
    query_result = g.uow.issue_statuses.get_all_issuestatuses(query_parameters)
    return jsonify(query_result.__dict__)


@IssueStatusesBlueprint.route("/api/IssueStatuses/GetAll", methods=["GET"])
@login_required
@require_any_permission({"Manage Issue Statuses", "View Issue Statuses"})
def issue_statuses_get_all():
    return jsonify(result=g.uow.issue_statuses.get_all())


@IssueStatusesBlueprint.route("/api/IssueStatuses", methods=["POST"])
@login_required
@from_request_body("model", IssueStatus)
@require_permissions(["Manage Issue Statuses"])
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
    g.uow.issue_statuses.insert(model)
    return ""


@IssueStatusesBlueprint.route("/api/IssueStatuses/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Issue Statuses"])
def get(id):
    c = g.uow.issue_statuses.get(id)
    return jsonify(c.__dict__)


@IssueStatusesBlueprint.route("/api/IssueStatuses/<id>", methods=["PUT"])
@login_required
@from_request_body("model", IssueStatus)
@require_permissions(["Manage Issue Statuses"])
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

    g.uow.issue_statuses.update(model)
    return ""


@IssueStatusesBlueprint.route("/api/IssueStatuses/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Issue Statuses"])
def delete(id):
    try:
        g.uow.issue_statuses.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})