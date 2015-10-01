import json
import sys

from flask import request, jsonify, Blueprint, session, g

from api.models.PermissionCache import PermissionCache
from api.models.Role import Role
from extensions.binding import from_request_body, require_any_permission, require_permissions
from flask.ext.login import login_required
from api.models.QueryParameters import QueryParameters
from parseqs import parseqs


RolesBlueprint = Blueprint("RolesBlueprint", __name__)


@RolesBlueprint.route("/api/Roles", methods=["GET"])
@login_required
@require_any_permission(['Manage Roles', 'View Roles'])
def roles_get():
    query_parameters = QueryParameters(parseqs.parse(request.query_string))
    query_result = g.uow.roles.get_all(query_parameters)
    return jsonify(query_result.to_dict())


@RolesBlueprint.route("/api/Roles/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Roles'])
def role_get(id):
    role = g.uow.roles.get_role_by_id(id)
    return json.dumps(role.__dict__)


@RolesBlueprint.route("/api/Roles", methods=["POST"])
@from_request_body("role", Role)
@login_required
@require_permissions(['Manage Roles'])
def role_post(role):
    if not role.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 403
        return response

    # check if role exists
    if g.uow.roles.role_exists(role.name):
        response = jsonify({"message": "A role with that name already exists."})
        response.status_code = 409
        return response

    # insert data
    current_user = session['current_user']
    role = g.uow.roles.insert(role, current_user['id'])

    return ""


@RolesBlueprint.route("/api/Roles/<id>", methods=["PUT"])
@from_request_body("role", Role)
@login_required
@require_permissions(['Manage Roles'])
def role_put(id, role):
    if not role.name:
        response = jsonify({"message": "Name is required."})
        response.status_code = 403
        return response

    # check to make sure the role does not already exist
    if g.uow.roles.role_exists(role.name) and g.uow.roles.get_role_by_id(id).name != role.name:
        # role already exists
        response = jsonify({"message": "A role with that name already exists."})
        response.status_code = 409
        return response

    current_user = session['current_user']

    g.uow.roles.update(role, current_user['id'])

    # Permission cache is no longer valid because of the role update, so we clear the permission cache
    PermissionCache.clear_permission_cache()
    # Cache will rebuild itself
    return ""


@RolesBlueprint.route("/api/Roles/<id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Roles'])
def role_delete(id):
    try:
        g.uow.roles.delete(id)
        #TODO: Figure out how to handle deleting of roles if user is in it, as well as permission scheme
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})


@RolesBlueprint.route("/api/Roles/GetInactive/<id>", methods=["GET"])
@login_required
@require_permissions(['Manage Roles'])
def roles_getInactive(id):
    # get the roles that a user isn't using
    userroles = g.uow.users.get_users_roles(id)
    allroles = g.uow.roles.get_all_roles()
    userRoleList = []
    data = []
    for r in userroles:
        userRoleList.append(r["role_id"])
    for r in allroles:
        if r["id"] not in userRoleList:
            data.append({
                "role_id": r["id"],
                "name": r["name"]
            })

    return json.dumps(data)


@RolesBlueprint.route("/api/Roles/GetAll", methods=["GET"])
@login_required
@require_any_permission(['Manage Roles', 'View Roles'])
def roles_getAll():
    roles = g.uow.roles.get_all_roles()
    data = []
    for r in roles:
        data.append({
            "role_id": r["id"],
            "name": r["name"]
        })

    return json.dumps(data)