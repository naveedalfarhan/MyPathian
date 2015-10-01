from datetime import datetime
from time import mktime, strptime
from flask import Blueprint, current_app, jsonify, g
from flask.ext.login import login_required
import pytz
import sys
from api.models.Meeting import Meeting
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions

MeetingsBlueprint = Blueprint("MeetingsBlueprint", __name__)


@MeetingsBlueprint.route("/api/Meetings", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage Meetings', 'View Meetings'])
def get_meetings(query_parameters):
    query_result = g.uow.meetings.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@MeetingsBlueprint.route("/api/Meetings", methods=["POST"])
@login_required
@from_request_body("model", Meeting)
@require_permissions(['Manage Meetings'])
def insert(model):
    if not model.title:
        response = jsonify({"message": "Title is required."})
        response.status_code = 400
        return response
    if not model.called_by_id:
        response = jsonify({"message": "Called By contact is required."})
        response.status_code = 400
        return response
    if not model.note_taker_id:
        response = jsonify({"message": "Note Taker contact is required."})
        response.status_code = 400
        return response
    if not model.facilitator_id:
        response = jsonify({"message": "Facilitator contact is required."})
        response.status_code = 400
        return response
    if not model.time_keeper_id:
        response = jsonify({"message": "Time Keeper contact is required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Group is required."})
        response.status_code = 400
        return response

    # TODO: Check meeting type
    try:
        model.date = pytz.UTC.localize(datetime.fromtimestamp(mktime(strptime(model.date[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the date."})
        response.status_code = 500
        return response
    print("insert")
    g.uow.meetings.insert(model)
    return ""


@MeetingsBlueprint.route("/api/Meetings/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Meetings'])
def get(id):
    return jsonify(g.uow.meetings.get(id).__dict__)


@MeetingsBlueprint.route("/api/Meetings/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Meeting)
@require_permissions(['Manage Meetings'])
def update(id, model):
    model.id = id
    if not model.title:
        response = jsonify({"message": "Title is required."})
        response.status_code = 400
        return response
    if not model.called_by_id:
        response = jsonify({"message": "Called By contact is required."})
        response.status_code = 400
        return response
    if not model.note_taker_id:
        response = jsonify({"message": "Note Taker contact is required."})
        response.status_code = 400
        return response
    if not model.facilitator_id:
        response = jsonify({"message": "Facilitator contact is required."})
        response.status_code = 400
        return response
    if not model.time_keeper_id:
        response = jsonify({"message": "Time Keeper contact is required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Group is required."})
        response.status_code = 400
        return response

    # TODO: Check meeting type
    try:
        model.date = pytz.UTC.localize(datetime.fromtimestamp(mktime(strptime(model.date[:10], "%Y-%m-%d"))))
    except:
        response = jsonify({"message": "There was an error parsing the date."})
        response.status_code = 500
        return response
    print("insert")
    g.uow.meetings.update(model)
    return ""


@MeetingsBlueprint.route("/api/Meetings/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Meetings'])
def delete(id):
    try:
        g.uow.meetings.delete(id)
        return jsonify({"Success": "True"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "False"})