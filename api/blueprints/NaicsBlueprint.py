import json
from extensions.binding import from_query_string
from flask import Blueprint, g
from flask.ext.login import login_required

NaicsBlueprint = Blueprint("NaicsBlueprint", __name__)

@NaicsBlueprint.route("/api/Naics/getChildrenOf")
@from_query_string("naics_code", str, prop_name="id")
@from_query_string("restrict_type", str, prop_name="restrict_type")
@login_required
def get_children_of(naics_code, restrict_type):
    # properly convert restrict_type to a boolean
    if restrict_type and restrict_type.lower() == 'true':
        restrict_type = True
    else:
        restrict_type = False

    # check if it's a NAICS code or if it's actually a group
    if not naics_code or naics_code[:2] != 'g_':
        # it is not a group, so we trim the prefix and continue like normal
        if naics_code:
            naics_code = naics_code[2:]

        children = g.uow.naics.get_children_of(naics_code)
        if naics_code and not restrict_type:
            group_children = g.uow.groups.get_children_of_naics_code(naics_code)
        else:
            group_children = []

        # prefix the id's for naics and groups to be able to identify them later
        children = [{'id': 'n_' + code['id'], 'name': code['name'], 'childIds': code['childIds']} for code in children]
        group_children = [{'id': 'g_' + group['id'], 'name': group['name'], 'childIds': group['childIds']} for group in group_children]

        # combine the lists and sort them based on name
        combined = children + group_children
        combined = sorted(combined, key=lambda x: x['name'])
    else:
        # it is a group, and so there will only be groups underneath it
        group_id = naics_code[2:]
        combined = g.uow.groups.get_child_groups_of(group_id)
        combined = [{'id': 'g_' + group['id'], 'name': group['name'], 'childIds': group['childIds']} for group in combined]
        combined = sorted(combined, key=lambda x: x['name'])
    return json.dumps(combined)

@NaicsBlueprint.route("/api/Naics/getLevelFive", methods=["GET"])
def get():
    codes = g.uow.naics.get_level_five()
    return json.dumps(codes)

@NaicsBlueprint.route("/api/Naics/<naics_code>/getDescendants")
@login_required
def get_descendants(naics_code):
    descendants = g.uow.naics.get_children_of(naics_code)
    return json.dumps(descendants)
