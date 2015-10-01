from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.Contact import Contact

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


ContactsBlueprint = Blueprint("ContactsBlueprint", __name__)


@ContactsBlueprint.route("/api/Contacts", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage Contacts', 'View Contacts'])
def contacts_get(query_parameters):
    query_result = g.uow.contacts.get_all_contacts_table(query_parameters)
    return jsonify(query_result.__dict__)

@ContactsBlueprint.route("/api/Contacts/GetAll", methods=["GET"])
@login_required
@require_any_permission(['Manage Contacts', 'View Contacts'])
def contacts_get_all():
    result = g.uow.contacts.get_all_contacts()
    return jsonify(results=result)


@ContactsBlueprint.route("/api/Contacts", methods=["POST"])
@login_required
@from_request_body("model", Contact)
@require_permissions(['Manage Contacts'])
def insert(model):
    if not model.first_name or not model.last_name:
        response = jsonify({"message": "First and last names are required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Group is required."})
        response.status_code = 400
        return response
    print("insert")
    g.uow.contacts.insert(model)
    return ""


@ContactsBlueprint.route("/api/Contacts/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Contacts'])
def get(id):
    c = g.uow.contacts.get(id)
    return jsonify(c.__dict__)


@ContactsBlueprint.route("/api/Contacts/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Contact)
@require_permissions(['Manage Contacts'])
def update(id, model):
    model.id = id
    if not model.first_name or not model.last_name:
        response = jsonify({"message": "First and last names are required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Group is required"})
        response.status_code = 400
        return response
    g.uow.contacts.update(model)
    return ""


@ContactsBlueprint.route("/api/Contacts/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Contacts'])
def delete(id):
    try:
        g.uow.contacts.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})