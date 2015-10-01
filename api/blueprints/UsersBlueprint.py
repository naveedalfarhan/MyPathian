from datetime import datetime
import json
from time import mktime, strptime
from api.models.PermissionCache import PermissionCache
from api.models.ReportingGroupCache import ReportingGroupCache
import pytz
import unicodedata

from api.models.User import User
import bcrypt
from extensions.binding import from_request_body, require_permissions, require_any_permission
from flask import request, jsonify, Blueprint, session, g
from flask.ext.login import login_required

from api.models.QueryParameters import QueryParameters
from parseqs import parseqs


UsersBlueprint = Blueprint("UsersBlueprint", __name__)


@UsersBlueprint.route("/api/Users", methods=["GET"])
@login_required
@require_any_permission(['View Users', 'Manage Users'])
def users_get():
    if not PermissionCache.user_has_permissions(session['current_user']['id'], ['View Users'], g.uow) and \
            not PermissionCache.user_has_permissions(session['current_user']['id'], ['Manage Users'], g.uow):
        return ""
    query_parameters = QueryParameters(parseqs.parse(request.query_string))
    query_result = g.uow.users.get_all(query_parameters)
    return jsonify(query_result.to_dict())


@UsersBlueprint.route("/api/Users", methods=["POST"])
@login_required
@require_permissions(['Manage Users'])
@from_request_body("model", User)
def users_post(model):
    if not model.username:
        response = jsonify({"message": "Username is required."})
        response.status_code = 400
        return response

    if not model.primary_group_id:
        response = jsonify({"message": "Primary group is required."})
        response.status_code = 400
        return response

    if not model.password:
        response = jsonify({"message": "Password is required."})
        response.status_code = 400
        return response

    # check if user exists
    if g.uow.users.user_exists(model.username):
        response = jsonify({"message": "A user with the specified username already exists."})
        response.status_code = 409
        return response

    # hash the password
    salt = bcrypt.gensalt()
    model.password = bcrypt.hashpw(str(model.password), salt)

    # try to parse the expiration date
    if model.expiration_date:
        try:
            model.expiration_date = pytz.UTC.localize(
                datetime.fromtimestamp(mktime(strptime(model.expiration_date[:10], "%Y-%m-%d"))))
        except:
            response = jsonify({"message": "There was an error parsing the expiration date."})
            response.status_code = 500
            return response
    else:
        response = jsonify({"message": "The expiration date is required."})
        response.status_code = 400
        return response

    # insert data
    current_user = session['current_user']
    insert = g.uow.users.add_user(model, current_user['id'])

    return ""


@UsersBlueprint.route("/api/Users/<id>", methods=["GET"])
@require_permissions(['Manage Users'])
@login_required
def user_get(id):
    roles = g.uow.users.get_users_roles(id)
    data = []
    for r in roles:
        data.append(r)

    u = g.uow.users.get_user_by_id(id)
    user = User(u)
    # hide the password
    del user.password

    user.roles = data

    if user.primary_group_id:
        user.primary_group = g.uow.groups.get_group_by_id(user.primary_group_id).__dict__
    else:
        user.primary_group = None

    if user.group_ids:
        user.groups = g.uow.groups.get_all(user.group_ids)
    else:
        user.groups = []
    return json.dumps(user.__dict__)


@UsersBlueprint.route("/api/Users/<id>", methods=["PUT"])
@login_required
@from_request_body("model", User)
@require_permissions(['Manage Users'])
def user_put(id, model):
    model.id = id
    if not model.username:
        response = jsonify({"message": "Username is required."})
        response.status_code = 400
        return response

    if not model.primary_group_id:
        response = jsonify({"message": "Primary group is required."})
        response.status_code = 400
        return response

    # check duplicate username
    if g.uow.users.user_exists_with_id(model.username, model.id):
        response = jsonify({"message": "The specified username is already taken."})
        response.status_code = 409
        return response

    if model.password:
        # password has changed
        salt = bcrypt.gensalt()
        model.password = bcrypt.hashpw(str(model.password), salt)

    # try to parse the expiration date
    if model.expiration_date:
        try:
            model.expiration_date = pytz.UTC.localize(
                datetime.fromtimestamp(mktime(strptime(model.expiration_date[:10], "%Y-%m-%d"))))
        except:
            response = jsonify({"message": "There was an error parsing the expiration date."})
            response.status_code = 500
            return response
    else:
        response = jsonify({"message": "The expiration date is required."})
        response.status_code = 400
        return response

    # update user
    current_user = session['current_user']
    g.uow.users.update_user(current_user['id'], model)

    roles = g.uow.users.get_users_roles(model.id)
    permission_list = map(lambda record: record['permissions'], roles)
    # flatten out permission_list by going through all sublists of permission_list and returning the item
    permissions = list(set([item for sublist in permission_list for item in sublist]))

    # check the users permissions against the PermissionCache
    if permissions != PermissionCache.get_permissions_for_user(model.id, g.uow):
        # rebuild permission cache for user
        PermissionCache.update_user_permission_cache(model.id, g.uow)
    return ""


@UsersBlueprint.route("/api/Users/<id>", methods=["DELETE"])
@require_permissions(['Manage Users'])
@login_required
def user_delete(id):
    try:
        g.uow.users.delete_user(id)
        # Remove user from the permission cache
        PermissionCache.remove_user_from_cache(id)
        return ""
    except:
        raise


@UsersBlueprint.route("/api/Users/<id>/Notifications", methods=["GET"])
@login_required
def user_alarms(id):
    # check for any active notifications
    notifications = g.uow.users.get_notifications_for_user(id)
    return json.dumps(notifications)


@UsersBlueprint.route("/api/Users/<id>/Notifications/<notificationId>", methods=['DELETE'])
@login_required
def delete_notification(id, notificationId):
    g.uow.users.delete_notification(notificationId)
    return ""

@UsersBlueprint.route("/api/Users/<user_id>/Permissions", methods=['GET'])
@login_required
def get_permissions(user_id):
    perms = PermissionCache.get_permissions_for_user(user_id, g.uow)
    return json.dumps(perms)


@UsersBlueprint.route("/api/Users/ReportingGroup", methods=["POST"])
@from_request_body("group_id", str, "group_id")
@login_required
def update_reporting_group(group_id):
    user_id = session['current_user']['id']
    ReportingGroupCache.change_reporting_group(user_id, group_id, g.uow)
    return ""