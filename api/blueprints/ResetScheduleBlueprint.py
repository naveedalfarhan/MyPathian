import json
from flask import jsonify, Blueprint, abort, g
from extensions.binding import from_query_string
from PathianExceptions import PathianException
from extensions.binding import from_query_string, require_any_permission, require_permissions
from extensions.binding import from_request_body
from api.models.QueryParameters import QueryParameters
from flask.ext.login import login_required
from api.models.ResetSchedule import ResetSchedule


ResetScheduleBlueprint = Blueprint("ResetScheduleBlueprint",  __name__)


@ResetScheduleBlueprint.route("/api/ResetSchedules", methods=["GET"])
@login_required
@require_any_permission(['Manage Reset Schedules', "View Reset Schedules"])
def reset_schedules_get_all():
    data = g.uow.reset_schedules.get_all_reset_schedules()

    return jsonify(results=data)


@ResetScheduleBlueprint.route("/api/ResetSchedules/<reset_schedule_id>", methods=["GET"])
@login_required
@require_permissions(['Manage Reset Schedules'])
def get(reset_schedule_id):
    c = g.uow.reset_schedules.get(reset_schedule_id)
    return jsonify(c.__dict__)


@ResetScheduleBlueprint.route("/api/ResetSchedules", methods=["POST"])
@login_required
@from_request_body("model", ResetSchedule)
@require_permissions(['Manage Reset Schedules'])
def insert(model):
    try:
        del model.id
        rest_schedule_id = g.uow.reset_schedules.insert(model)
        return jsonify({"Success": "true", "id": rest_schedule_id})
    except Exception as e:
        raise PathianException("Error while inserting raf pressure", status_code=500)


@ResetScheduleBlueprint.route("/api/ResetSchedules/<reset_schedule_id>", methods=["PUT"])
@login_required
@from_request_body("model", ResetSchedule)
@require_permissions(['Manage Reset Schedules'])
def update(reset_schedule_id, model):
    model.id = reset_schedule_id
    g.uow.reset_schedules.update(model)
    return ""


@ResetScheduleBlueprint.route("/api/ResetSchedules/<reset_schedule_id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Reset Schedules'])
def delete(reset_schedule_id):
    try:
        g.uow.reset_schedules.delete(reset_schedule_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while inserting reset schedule", status_code=500)

