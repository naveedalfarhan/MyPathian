from api.models.ReportingGroupCache import ReportingGroupCache
from flask import request, abort, jsonify, make_response, Blueprint, current_app, session, g

from api.models.PermissionCache import PermissionCache
import bcrypt
from flask.ext.login import login_user, logout_user


LoginBlueprint = Blueprint("LoginBlueprint", __name__)


@LoginBlueprint.route("/api/Login", methods=["GET"])
def login_get():

    if 'current_user' not in session:
        abort(403)
        return

    user = session['current_user']
    user['reporting_group'] = ReportingGroupCache.get_user_group(user['id'], g.uow)

    if user is None:
        abort(403)
        return

    return jsonify(user)


@LoginBlueprint.route("/api/Login", methods=["POST"])
def login_post():
    post = request.get_json()
    if not "username" in post or not "password" in post:
        abort(400)

    user = g.uow.users.get_user_by_username(post["username"])

    if user is None:
        abort(400)

    if not bcrypt.hashpw(str(post["password"]), str(user.password)) == user.password:
        abort(401)

    login_user(user)

    g.uow.users.update_user_login_time(user.id)

    try:
        primary_group_object = g.uow.groups.get_group_by_id(user.primary_group_id)
        primary_group = {'id': primary_group_object.id, 'name': primary_group_object.name}

        groups = g.uow.groups.get_all(user.group_ids)

    except:
        primary_group = None
        groups = []

    # update the user permission cache
    PermissionCache.update_user_permission_cache(user.id, g.uow)

    # get a combined list of groups for the user
    users_groups = groups
    if primary_group is not None:
        users_groups = list(users_groups + [primary_group])

    # since we are passing the entire dictionary of each group back, we must create a unique list of dictionaries
    # this can be done by creating a new list keyed by id, then taking the values of that list
    # More information: http://stackoverflow.com/questions/11092511/python-list-of-unique-dictionaries
    users_groups = {gr['id']:gr for gr in users_groups}.values()

    # return user info for global user variable in Angular
    login_info = dict(username=user.username, id=user.id, primary_group=primary_group,
                      groups=users_groups,
                      permissions=PermissionCache.get_permissions_for_user(user.id, g.uow),
                      reporting_group=ReportingGroupCache.get_user_group(user.id, g.uow))

    session['current_user'] = login_info

    resp = make_response(jsonify(login_info))

    resp.set_cookie('username', user.username)
    return resp


@LoginBlueprint.route("/api/Login", methods=["DELETE"])
def login_delete():
    logout_user()
    session.pop('current_user', None)
    resp = make_response()
    resp.set_cookie('username', '', expires=0)
    return resp