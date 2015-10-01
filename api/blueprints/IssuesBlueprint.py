from datetime import datetime
from time import strptime, mktime
from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import pytz
import sys
from api.models.Issue import Issue
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions

IssuesBlueprint = Blueprint("IssuesBlueprint", __name__)


@IssuesBlueprint.route("/api/Issues", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage Issues', 'View Issues'])
def get_issues(query_parameters):
    query_result = g.uow.issues.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@IssuesBlueprint.route("/api/Issues", methods=["POST"])
@login_required
@from_request_body("model", Issue)
@require_permissions(['Manage Issues'])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.open_date or not model.due_date:
        response = jsonify({"message": "An opening date and due date are required."})
        response.status_code = 400
        return response
    if not model.issued_by_ids or not model.issued_to_ids:
        response = jsonify({"message": "At least one Issued By and Issued To contact must be set."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Commissioning group is required."})
        response.status_code = 400
        return response
    # TODO: Check priority, status, type
    try:
        model.open_date = pytz.UTC.localize(datetime.fromtimestamp(mktime(strptime(model.open_date[:10], "%Y-%m-%d"))))
        model.due_date = pytz.UTC.localize(datetime.fromtimestamp(mktime(strptime(model.due_date[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the dates."})
        response.status_code = 500
        return response
    print("insert")
    g.uow.issues.insert(model)
    return ""


@IssuesBlueprint.route("/api/Issues/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Issue)
@require_permissions(['Manage Issues'])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.open_date or not model.due_date:
        response = jsonify({"message": "An opening date and due date are required."})
        response.status_code = 400
        return response
    if not model.issued_by_ids or not model.issued_to_ids:
        response = jsonify({"message": "At least one Issued By and Issued To contact must be set."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Commissioning group is required."})
        response.status_code = 400
        return response
    # TODO: Check priority, status, type
    try:
        model.open_date = pytz.UTC.localize(datetime.fromtimestamp(mktime(strptime(model.open_date[:10], "%Y-%m-%d"))))
        model.due_date = pytz.UTC.localize(datetime.fromtimestamp(mktime(strptime(model.due_date[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the dates."})
        response.status_code = 500
        return response
    g.uow.issues.update(model)
    return ""


@IssuesBlueprint.route("/api/Issues/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Issues'])
def get(id):
    issue = g.uow.issues.get(id)
    issue.issued_by_model = g.uow.contacts.get_list(issue.issued_by_ids)
    issue.issued_to_model = g.uow.contacts.get_list(issue.issued_to_ids)
    return jsonify(issue.__dict__)


@IssuesBlueprint.route("/api/Issues/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Issues'])
def delete(id):
    try:
        g.uow.issues.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success", "false"})


@IssuesBlueprint.route("/api/Issues/<component_id>/GetAllAvailable", methods=["GET"])
@login_required
@require_any_permission(['Manage Issues', 'View Issues'])
def get_all(component_id):
    issues = g.uow.issues.get_issues_not_mapped_to_component(component_id)

    return jsonify(data=issues)