import json

from flask import jsonify, Blueprint, current_app, session, g
from api.models.QueryParameters import QueryParameters
from api.models.Group import Group
from extensions.binding import from_query_string, require_any_permission, require_permissions
from extensions.binding import from_request_body
from flask.ext.login import login_required


GroupsBlueprint = Blueprint("GroupsBlueprint", __name__)


@GroupsBlueprint.route("/api/groups", methods=["GET"], endpoint="groups_get")
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_any_permission(["Manage Groups", "View Groups"])
def get(query_parameters):
    query_result = g.uow.groups.apply_query_parameters(query_parameters)
    return jsonify(query_result.__dict__)


@GroupsBlueprint.route("/api/groups/<group_id>/accounts", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_permissions(["View Accounts"])
def get_accounts_for_group(group_id, query_parameters):
    query_result = g.uow.accounts.get_all_by_group_id(query_parameters, group_id)
    return jsonify(query_result.__dict__)


@GroupsBlueprint.route("/api/groups/getChildrenOf", methods=["GET"], endpoint="groups_get_children_of")
@from_query_string("group_id", str, prop_name="id")
@login_required
@require_any_permission(["Manage Groups", "View Groups"])
def get_children_of(group_id):
    current_app.logger.info('Begin get_children_of')
    groups = g.uow.groups.get_child_groups_of(group_id)
    current_app.logger.info('End get_children_of')
    return json.dumps(groups)


@GroupsBlueprint.route("/api/groups/<group_id>", methods=["GET"], endpoint="groups_get_one")
@login_required
@require_permissions(["Manage Groups"])
def get_one(group_id):
    group = g.uow.groups.get_group_by_id(group_id)
    return json.dumps(group.__dict__)


@GroupsBlueprint.route("/api/groups", methods=["POST"], endpoint="groups_post")
@from_request_body("group", Group)
@login_required
@require_permissions(["Manage Groups"])
def post(group):
    g.uow.groups.insert(group)
    return json.dumps(group.__dict__)


@GroupsBlueprint.route("/api/groups/<group_id>", methods=["POST"], endpoint="groups_post_edit")
@from_request_body("group", Group)
@login_required
@require_permissions(["Manage Groups"])
def post_edit(group_id, group):
    g.uow.groups.update(group)
    return json.dumps(group.__dict__)


@GroupsBlueprint.route("/api/groups/addRoot", methods=["POST"])
@from_request_body("child_id", str, prop_name="childId")
@login_required
@require_permissions(["Manage Groups"])
def add_root(child_id):
    return_obj = g.uow.groups.add_root(child_id)
    return jsonify(return_obj)


@GroupsBlueprint.route("/api/groups/removeRoot", methods=["POST"])
@from_request_body("child_id", str, prop_name="childId")
@login_required
@require_permissions(["Manage Groups"])
def remove_root(child_id):
    return_obj = g.uow.groups.remove_root(child_id)
    return jsonify(return_obj)


@GroupsBlueprint.route("/api/groups/<parent_id>/addChild", methods=["POST"], endpoint="groups_add_child")
@from_request_body("child_id", str, prop_name="childId")
@login_required
@require_permissions(["Manage Groups"])
def add_child(parent_id, child_id):
    return_obj = g.uow.groups.add_child(parent_id, child_id)
    return jsonify(return_obj)


@GroupsBlueprint.route("/api/groups/<parent_id>/removeChild", methods=["POST"], endpoint="groups_remove_child")
@from_request_body("child_id", str, prop_name="childId")
@login_required
@require_permissions(["Manage Groups"])
def remove_child(parent_id, child_id):
    return_obj = g.uow.groups.remove_child(parent_id, child_id)
    return jsonify(return_obj)


@GroupsBlueprint.route("/api/groups/GetAccounts/<group_id>", methods=["GET"])
@login_required
@require_any_permission(['Run Group Reports',
                         'Run NAICS Reports',
                         'Run SIC Reports',
                         'Run Component Reports',
                         'Run Subcomponent Reports'])  # this function is used for reporting methods only
def get_accounts(group_id):
    return_obj = g.uow.groups.get_accounts(group_id)
    return json.dumps(return_obj)


@GroupsBlueprint.route("/api/groups/<group_id>/getDescendants", methods=["GET"])
@login_required
@require_any_permission(["Manage Groups", "View Groups"])
def get_descendants(group_id):
    return_obj = g.uow.groups.get_descendants(group_id)
    return json.dumps(return_obj)


@GroupsBlueprint.route("/api/group/commissioningGroup", methods=["GET"])
@login_required
def get_commissioning_group():
    try:
        group = g.uow.groups.get_group_by_id(session["CommissioningGroup"])
        return jsonify({"group": group.__dict__})
    except:
        return jsonify({"group": None})


@GroupsBlueprint.route("/api/group/commissioningGroup", methods=["PUT"])
@from_request_body("group_id", int)
@login_required
def set_commissioning_group(group_id):
    group = g.uow.groups.get_group_by_id(group_id)
    session['CommissioningGroup'] = group
    return jsonify({"group": group.__dict__})


@GroupsBlueprint.route("/api/group/<group_id>/Tasks", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
def get_tasks(group_id, query_parameters):
    tasks = g.uow.tasks.get_group_tasks(group_id, query_parameters)
    return jsonify(tasks.__dict__)


@GroupsBlueprint.route("/api/groups/<group_id>/equipment", methods=["GET"])
@require_any_permission(["View Equipment", "Manage Equipment"])
@login_required
def get_equipment_for_group(group_id):
    equipment = g.uow.equipment.get_equipment_for_group(group_id)
    return json.dumps(equipment)


@GroupsBlueprint.route("/api/group/<group_id>/issues", methods=["GET"])
@login_required
@require_any_permission(['View Dashboard'])
@from_query_string("query_parameters", QueryParameters)
def get_issues_for_group(group_id, query_parameters):
    issues = g.uow.issues.get_issues_for_group(group_id, query_parameters)
    return jsonify(issues.__dict__)