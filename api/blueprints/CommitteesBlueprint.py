from flask import Blueprint, current_app, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.Committee import Committee
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions

CommitteesBlueprint = Blueprint("CommitteesBlueprint", __name__)


@CommitteesBlueprint.route("/api/Committees", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage Committees', 'View Committees'])
def get_committees(query_parameters):
    query_result = g.uow.committees.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@CommitteesBlueprint.route("/api/Committees", methods=["POST"])
@login_required
@from_request_body("model", Committee)
@require_permissions(['Manage Committees'])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Group is required."})
        response.status_code = 400
        return response
    if not model.corporate_energy_director_id:
        response = jsonify({"message": "Corporate Energy Director is required."})
        response.status_code = 400
        return response
    g.uow.committees.insert(model)
    return ""


@CommitteesBlueprint.route("/api/Committees/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Committees'])
def get(id):
    model = g.uow.committees.get(id)
    return jsonify(model.__dict__)


@CommitteesBlueprint.route("/api/Committees/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Committee)
@require_permissions(['Manage Committees'])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Group is required."})
        response.status_code = 400
        return response
    if not model.corporate_energy_director_id:
        response = jsonify({"message": "Corporate Energy Director is required."})
        response.status_code = 400
        return response
    g.uow.committees.update(model)
    return ""


@CommitteesBlueprint.route("/api/Committees/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Committees'])
def delete(id):
    try:
        g.uow.committees.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})