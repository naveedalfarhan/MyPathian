from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.UtilityCompany import UtilityCompany

from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions


UtilityCompaniesBlueprint = Blueprint("UtilityCompaniesBlueprint", __name__)


@UtilityCompaniesBlueprint.route("/api/UtilityCompanies", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(["Manage Utility Companies", "View Utility Companies"])
def utilitycompanies_get(query_parameters):
    query_result = g.uow.utility_companies.get_all_utilitycompanies(query_parameters)
    return jsonify(query_result.__dict__)


@UtilityCompaniesBlueprint.route("/api/UtilityCompanies", methods=["POST"])
@login_required
@from_request_body("model", UtilityCompany)
@require_permissions(["Manage Utility Companies"])
def insert(model):

    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    if model.address2 is None:
        model.address2 = ''

    if g.uow.utility_companies.does_utility_exist_by_name(model.name):
        response = jsonify({"message": "You can only have one utility company with that name."})
        response.status_code = 400
        return response

    print("insert")
    g.uow.utility_companies.insert(model)
    return ""


@UtilityCompaniesBlueprint.route("/api/UtilityCompanies/<id>", methods=["GET"])
@login_required
@require_permissions(["Manage Utility Companies"])
def get(id):
    c = g.uow.utility_companies.get(id)
    return jsonify(c.__dict__)


@UtilityCompaniesBlueprint.route("/api/UtilityCompanies/<id>", methods=["PUT"])
@login_required
@from_request_body("model", UtilityCompany)
@require_permissions(["Manage Utility Companies"])
def update(id, model):
    model.id = id

    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response

    g.uow.utility_companies.update(model)
    return ""


@UtilityCompaniesBlueprint.route("/api/UtilityCompanies/<id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Utility Companies"])
def delete(id):
    try:
        g.uow.utility_companies.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})