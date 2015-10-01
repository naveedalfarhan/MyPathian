import json
from flask import Blueprint, jsonify, g
from flask.ext.login import login_required
import sys
from api.models.Category import Category
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions

SyrxCategoriesBlueprint = Blueprint("SyrxCategoriesBlueprint", __name__)


@SyrxCategoriesBlueprint.route("/api/SyrxCategories", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
@require_any_permission(['Manage Categories', "View Categories"])
def syrx_categories_get(query_parameters):
    query_result = g.uow.syrx_categories.get_all(query_parameters)
    return jsonify(query_result.__dict__)

@SyrxCategoriesBlueprint.route("/api/SyrxCategories/GetAll", methods=["GET"])
@login_required
@require_any_permission(['Manage Categories', "View Categories"])
def syrx_categories_get_all():
    result = g.uow.syrx_categories.get_all_categories()
    data = []
    for category in result:
        data.append(category)
    return json.dumps(data)

@SyrxCategoriesBlueprint.route("/api/SyrxCategories/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Categories'])
def get(id):
    c = g.uow.syrx_categories.get(id)
    return jsonify(c.__dict__)


@SyrxCategoriesBlueprint.route("/api/SyrxCategories", methods=["POST"])
@login_required
@from_request_body("model", Category)
@require_permissions(['Manage Categories'])
def insert(model):
    if not model.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 400
        return response
    if g.uow.syrx_categories.name_exists(model.name):
        response = jsonify({"message": "A category with that name already exists."})
        response.status_code = 409
        return response
    print("insert")
    g.uow.syrx_categories.insert(model)
    return ""


@SyrxCategoriesBlueprint.route("/api/SyrxCategories/<id>", methods=["PUT"])
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
    if (not cat.name == model.name) and g.uow.syrx_categories.name_exists(model.name):
        response = jsonify({"message": "A category with that name already exists."})
        response.status_code = 409
        return response
    g.uow.syrx_categories.update(model)
    return ""


@SyrxCategoriesBlueprint.route("/api/SyrxCategories/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Categories'])
def delete(id):
    try:
        g.uow.syrx_categories.delete(id)
        return jsonify({"Success": "true"})
    except:
        return jsonify({"Success": "false"})


@SyrxCategoriesBlueprint.route("/api/SyrxCategories/GetAll", methods=["GET"])
@login_required
@require_permissions(['View Categories'])
def get_all():
    categories = g.uow.syrx_categories.get_all_as_list()
    data = []
    for c in categories:
        data.append(c)
    return json.dumps(data)