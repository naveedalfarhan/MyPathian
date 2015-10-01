import json
from extensions.binding import from_query_string
from flask import Blueprint, g
from flask.ext.login import login_required

SicBlueprint = Blueprint("SicBlueprint", __name__)

@SicBlueprint.route("/api/Sic/getChildrenOf")
@from_query_string("sic_code", str, prop_name="id")
@from_query_string("restrict_type", str, prop_name="restrict_type")
@login_required
def get_children_of(sic_code, restrict_type):
    # properly conver restrict_type to a boolean
    if restrict_type and restrict_type.lower() == 'true':
        restrict_type = True
    else:
        restrict_type = False

    # check if it's a SIC code or if it's actually a group
    if not sic_code or sic_code[:2] != 'g_':
        # it is not a group, so we trim the prefix and continue like normal
        if sic_code:
            sic_code = sic_code[2:]

        children = g.uow.sic.get_children_of(sic_code)
        if sic_code and not restrict_type:
            group_children = g.uow.groups.get_children_of_sic_code(sic_code)
        else:
            group_children = []

        # prefix the id's for sic to be able to identify them later
        children = [{'id': 's_' + code['id'], 'name': code['name'], 'childIds': code['childIds']} for code in children]
        group_children = [{'id': 'g_' + group['id'], 'name': group['name'], 'childIds': group['childIds']} for group in group_children]

        # combine the lists and sort them based on name
        combined = children + group_children
        combined = sorted(combined, key=lambda x: x['name'])
    else:
        # it is a group, and so there will be only groups underneath it
        group_id = sic_code[2:]
        combined = g.uow.groups.get_child_groups_of(group_id)
        combined = [{'id': 'g_' + group['id'], 'name': group['name'], 'childIds': group['childIds']} for group in combined]
        combined = sorted(combined, key=lambda x: x['name'])

    return json.dumps(combined)

@SicBlueprint.route("/api/Sic/getLevelTwo", methods=["GET"])
def get_level_two():
    codes = g.uow.sic.get_level_two()
    return json.dumps(codes)

@SicBlueprint.route("/api/Sic/<sic_code>/getDescendants")
@login_required
def get_descendants(sic_code):
    descendants = g.uow.sic.get_children_of(sic_code)
    return json.dumps(descendants)