from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.MeetingType import MeetingType

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


MeetingTypesBlueprint = Blueprint("MeetingTypesBlueprint", __name__)


@MeetingTypesBlueprint.route("/api/MeetingTypes", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Meeting Types", "View Meeting Types"])
def meetingtypes_get(query_parameters):
    query_result = g.uow.meeting_types.get_all_meetingtypes(query_parameters)
    return jsonify(query_result.__dict__)


@MeetingTypesBlueprint.route("/api/MeetingTypes", methods=["POST"])
@login_required
@from_request_body("model", MeetingType)
@require_permissions(["Manage Meeting Types"])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.meeting_types.does_meeting_type_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one meeting type with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.meeting_types.insert(model)
    return ""


@MeetingTypesBlueprint.route("/api/MeetingTypes/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Meeting Types"])
def get(id):
    c = g.uow.meeting_types.get(id)
    return jsonify(c.__dict__)


@MeetingTypesBlueprint.route("/api/MeetingTypes/<id>", methods=["PUT"])
@login_required
@from_request_body("model", MeetingType)
@require_permissions(["Manage Meeting Types"])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if g.uow.meeting_types.does_meeting_type_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one meeting type with that name."})
        response.status_code = 400
        return response

    g.uow.meeting_types.update(model)
    return ""


@MeetingTypesBlueprint.route("/api/MeetingTypes/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Meeting Types"])
def delete(id):
    try:
        g.uow.meeting_types.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})