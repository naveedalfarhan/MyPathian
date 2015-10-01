import json
from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.Contract import Contract

from api.models.QueryParameters import QueryParameters
from api.models.User import User
from extensions.binding import from_query_string, from_request_body


ContractsBlueprint = Blueprint("ContractsBlueprint", __name__)


@ContractsBlueprint.route("/api/Contracts", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def contracts_get(query_parameters):
    query_result = g.uow.contracts.get_all_contracts(query_parameters)
    return jsonify(query_result.__dict__)

@ContractsBlueprint.route("/api/Contracts", methods=["POST"])
@login_required
@from_request_body("model", Contract)
def insert(model):
    if not model.name:
        response = jsonify({"message":"Name is required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Group is required."})
        response.status_code = 400
        return response

    if g.uow.contracts.does_contract_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one contract with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.contracts.insert(model)
    return ""

@ContractsBlueprint.route("/api/Contracts/<id>", methods=["GET"])
@login_required
def get(id):
    c = g.uow.contracts.get(id)
    usersarray = []
    if c.user_ids:
        users = g.uow.users.get_users_by_ids(c.user_ids)
        for user in users:
            u = User(user).__dict__
            usersarray.append({"id": u['id'], "username": u['username']})

    if c.group_id:
        c.group = g.uow.groups.get_group_by_id(c.group_id).__dict__
    else:
        c.group = None

    c.users = usersarray
    return json.dumps(c.__dict__)

@ContractsBlueprint.route("/api/Contracts/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Contract)
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message":"Name is required."})
        response.status_code = 400
        return response
    if not model.group_id:
        response = jsonify({"message": "Group is required."})
        response.status_code = 400
        return response

    g.uow.contracts.update(model)
    return ""

@ContractsBlueprint.route("/api/Contracts/<id>", methods=["DELETE"])
@login_required
def delete(id):
    try:
        g.uow.contracts.delete(id)
        return jsonify({"Success":"true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success":"false"})

@ContractsBlueprint.route("/api/Contracts/Users/<id>", methods=["GET"])
@login_required
def users_for_contract_get(id):
    contract = g.uow.contracts.get(id)
    usersarray = []
    if contract.user_ids:
        users = g.uow.users.get_users_by_ids(contract.user_ids)
        for user in users:
            u = User(user).__dict__
            usersarray.append({"id": u["id"], "username": u["username"]})

    return json.dumps(usersarray)