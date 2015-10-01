import json
from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.Category import Category
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions

CategoriesBlueprint = Blueprint("CategoriesBlueprint", __name__)


@CategoriesBlueprint.route("/api/Categories", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage Categories', "View Categories"])
def categories_get(query_parameters):
    query_result = g.uow.categories.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@CategoriesBlueprint.route("/api/Categories/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Categories'])
def get(id):
    c = g.uow.categories.get(id)
    return jsonify(c.__dict__)


@CategoriesBlueprint.route("/api/Categories", methods=["POST"])
@login_required
@from_request_body("model", Category)
@require_permissions(['Manage Categories'])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if g.uow.categories.name_exists(model.name):
        response = jsonify({"message": "Name already exists."})
        response.status_code = 409
        return response
    print("insert")
    g.uow.categories.insert(model)
    return ""


@CategoriesBlueprint.route("/api/Categories/<id>", methods=["PUT"])
@login_required
@from_request_body("model", Category)
@require_permissions(['Manage Categories'])
def update(id, model):
    model.id = id
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    cat = g.uow.categories.get(id)
    if (not cat.name == model.name) and g.uow.categories.name_exists(model.name):
        response = jsonify({"message": "A category with that name already exists."})
        response.status_code = 409
        return response
    g.uow.categories.update(model)
    return ""


@CategoriesBlueprint.route("/api/Categories/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Categories'])
def delete(id):
    try:
        g.uow.categories.delete(id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})


@CategoriesBlueprint.route("/api/Categories/GetAll", methods=["GET"])
@login_required
@require_permissions(['View Categories'])
def get_all():
    categories = g.uow.categories.get_all_as_list()
    data = []
    for c in categories:
        data.append(c)
    return json.dumps(data)