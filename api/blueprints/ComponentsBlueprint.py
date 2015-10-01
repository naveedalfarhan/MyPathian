import json

from api.models.Paragraph import Paragraph

from flask import jsonify, Blueprint, g, request, Response

from api.models.Component import Component
from api.models.ComponentPoint import ComponentPoint
from extensions.binding import from_query_string, require_any_permission, require_permissions
from extensions.binding import from_request_body
from api.models.QueryParameters import QueryParameters
from flask.ext.login import login_required
from parseqs import parseqs
from function_parser import FunctionParser
from PathianExceptions import PathianException
from api.models.ComponentIssue import ComponentIssue
from api.models.ComponentTask import ComponentTask


ComponentsBlueprint = Blueprint("ComponentsBlueprint", __name__)


@ComponentsBlueprint.route("/api/components/<component_id>/points", methods=["GET"])
@login_required
@require_permissions(['Manage Component Points'])
def component_points_get_by_component_id(component_id):
    queryParameters = QueryParameters(parseqs.parse(request.query_string))
    queryResult = g.uow.component_points.apply_query_parameters_by_component_id(component_id, queryParameters)
    return jsonify(queryResult.to_dict())


@ComponentsBlueprint.route("/api/components/<component_id>/paragraphs", methods=["GET"], defaults={"paragraph_type": None})
@ComponentsBlueprint.route("/api/components/<component_id>/paragraphs/<paragraph_type>", methods=["GET"])
@login_required
@require_any_permission(['View Component Engineering', 'Manage Component Engineering'])
def component_paragraphs_get(component_id, paragraph_type):
    query_parameters = QueryParameters(parseqs.parse(request.query_string))
    query_result = g.uow.paragraphs.apply_query_parameters_by_component_id(component_id, paragraph_type,
                                                                              query_parameters)
    return jsonify(query_result.to_dict())


@ComponentsBlueprint.route("/api/components/<component_id>/pointList", methods=["GET"], defaults={"point_type": None})
@ComponentsBlueprint.route("/api/components/<component_id>/pointList/<point_type>", methods=["GET"])
@login_required
@require_permissions(['Manage Component Points'])
def component_point_list_get_by_component_id(component_id, point_type):
    points = g.uow.component_points.get_points_for_component_id(component_id, point_type)
    return json.dumps(points)


@ComponentsBlueprint.route("/api/components/<component_id>/paragraphList", methods=["GET"], defaults={"paragraph_type": None})
@ComponentsBlueprint.route("/api/components/<component_id>/paragraphList/<paragraph_type>", methods=["GET"])
@login_required
@require_permissions(['Manage Component Points'])
def component_paragraph_list_get_by_component_id(component_id, paragraph_type):
    points = g.uow.paragraphs.get_paragraphs_for_component_id(component_id, paragraph_type)
    return json.dumps(points)


@ComponentsBlueprint.route("/api/components/getPointsByComponentIds", methods=["GET"])
@from_query_string("component_ids", list, prop_name="component_ids")
@login_required
@require_permissions(['Manage Component Points'])
def component_points_get_by_component_ids(component_ids):
    points = g.uow.component_points.get_points_for_component_ids(component_ids)
    return json.dumps(points)


@ComponentsBlueprint.route("/api/components/getAllParagraphs", methods=["GET"])
@from_query_string("component_ids", list, prop_name="component_ids")
@require_permissions(['Manage Component Points'])
def get_all_paragraphs(component_ids):
    paragraphs = g.uow.component_points.get_all_available_paragraphs(component_ids)
    return json.dumps(paragraphs)


@ComponentsBlueprint.route("/api/components/<component_id>", methods=["GET"])
@login_required
@require_any_permission(['Manage Component Structure Tree',
                         'View Component Structure Tree',
                         'Manage Component Mapping Tree',
                         'View Component Mapping Tree',
                         'Manage Component Points',
                         'View Component Points',
                         'Manage Component Engineering',
                         'View Component Engineering'])
def get_one(component_id):
    component = g.uow.components.get_by_id(component_id)
    return json.dumps(component.__dict__)


@ComponentsBlueprint.route("/api/components/getStructureChildrenOf", methods=["GET"])
@from_query_string("component_id", str, prop_name="id")
@login_required
@require_any_permission(['Manage Component Structure Tree', 'View Component Structure Tree'])
def get_structure_children_of(component_id):
    components = g.uow.components.get_structure_children_of(component_id)
    for c in components:
        c["name"] = str(c["num"]) + " " + c["description"]
    return json.dumps(components)


@ComponentsBlueprint.route("/api/components/managerTree", methods=["GET"])
@from_query_string("component_id", str, prop_name="id")
@login_required
def manager_tree(component_id):
    if component_id is None or component_id[0:11] == "components:":
        if component_id is not None:
            component_id = component_id[11:]
        components = g.uow.components.get_structure_children_of(component_id)
        for c in components:
            c["id"] = "component:" + c["id"]
            c["name"] = c["num"] + " " + c["description"]
            c["hasChildren"] = True
        return json.dumps(components)
    elif component_id[0:7] == "points:":
        if component_id[7:12] == "type:":
            point_type = component_id[12:14]
            component_id = component_id[15:]

            points = g.uow.component_points.get_points_for_component_id(component_id, point_type)
            points = [{"id": "point:" + p["id"], "name": p["component_point_num"], "hasChildren": False}
                      for p in points]
            return json.dumps(points)
        else:
            component_id = component_id[7:]
            components = [
                {"id": "points:type:EP:" + component_id, "name": "Energy Points", "hasChildren": True},
                {"id": "points:type:CP:" + component_id, "name": "Calculated Points", "hasChildren": True},
                {"id": "points:type:PP:" + component_id, "name": "Position Points", "hasChildren": True},
                {"id": "points:type:NP:" + component_id, "name": "Numeric Points", "hasChildren": True},
                {"id": "points:type:BP:" + component_id, "name": "Binary Points", "hasChildren": True},
                {"id": "points:type:VP:" + component_id, "name": "Variable Points", "hasChildren": True},
            ]
            return json.dumps(components)
    elif component_id[0:12] == "engineering:":
        if component_id[12:17] == "type:":
            if component_id[18] == ":":
                paragraph_type = component_id[17]
                component_id = component_id[19:]
            else:
                paragraph_type = component_id[17:19]
                component_id = component_id[20:]

            paragraphs = g.uow.paragraphs.get_paragraphs_for_component_id(component_id, paragraph_type)
            paragraphs = [{"id": "paragraph:" + p["id"], "name": p["num"], "hasChildren": False} for p in paragraphs]
            return json.dumps(paragraphs)
        else:
            component_id = component_id[12:]
            components = [
                {"id": "engineering:type:AR:" + component_id, "name": "Acceptance Requirements", "hasChildren": True},
                {"id": "engineering:type:CR:" + component_id, "name": "Commissioning Requirements", "hasChildren": True},
                {"id": "engineering:type:CS:" + component_id, "name": "Control Sequences", "hasChildren": True},
                {"id": "engineering:type:DR:" + component_id, "name": "Demand Response", "hasChildren": True},
                {"id": "engineering:type:FT:" + component_id, "name": "Functional Tests", "hasChildren": True},
                {"id": "engineering:type:LC:" + component_id, "name": "Load Curtailment", "hasChildren": True},
                {"id": "engineering:type:MR:" + component_id, "name": "Maintenance Requirements", "hasChildren": True},
                {"id": "engineering:type:I:" + component_id, "name": "Issues", "hasChildren": True},
                {"id": "engineering:type:PR:" + component_id, "name": "Project Requirements", "hasChildren": True},
                {"id": "engineering:type:RR:" + component_id, "name": "Roles and Responsibilities", "hasChildren": True},
                {"id": "engineering:type:T:" + component_id, "name": "Tasks", "hasChildren": True}
            ]
            return json.dumps(components)
    elif component_id[0:10] == "component:":
        component_id = component_id[10:]
        components = [
            {"id": "components:" + component_id, "name": "Components", "hasChildren": True},
            {"id": "points:" + component_id, "name": "Points", "hasChildren": True},
            {"id": "engineering:" + component_id, "name": "Engineering", "hasChildren": True}
        ]
        return json.dumps(components)


@ComponentsBlueprint.route("/api/components/getMappingChildrenOf", defaults={"root_component_id": None},
                           methods=["GET"])
@ComponentsBlueprint.route("/api/components/getMappingChildrenOf/<root_component_id>", methods=["GET"])
@from_query_string("component_id", str, prop_name="id")
@login_required
@require_any_permission(['Manage Component Mapping Tree', 'View Component Mapping Tree'])
def get_mapping_children_of(component_id, root_component_id):
    if component_id is None and root_component_id is not None:
        component_id = root_component_id

    components = g.uow.components.get_mapping_children_of(component_id)
    for c in components:
        c["name"] = c["num"] + " " + c["description"]
    return json.dumps(components)


@ComponentsBlueprint.route("/api/components/getStructureEquipmentChildrenOf", methods=["GET"])
@from_query_string("component_id", str, prop_name="id")
@login_required
@require_any_permission(['Manage Component Structure Tree', 'View Component Structure Tree'])
@require_any_permission(['View Equipment', 'Manage Equipment'])
def get_structure_equipment_children_of(component_id):
    components = g.uow.components.get_structure_equipment_children_of(component_id)
    return json.dumps(components)


@ComponentsBlueprint.route("/api/components/getAllChildrenOf", methods=["GET"])
@from_query_string("component_id", str, prop_name='id')
@login_required
@require_any_permission(['Manage Component Mapping Tree', 'View Component Mapping Tree'])
def get_all_children_of(component_id):
    components = g.uow.components.get_child_components_and_equipment(component_id)
    return json.dumps(components)


@ComponentsBlueprint.route("/api/components", methods=["POST"])
@from_request_body("component", Component)
@login_required
@require_any_permission(['Manage Component Structure Tree', 'Manage Component Mapping Tree'])
def insert(component):
    g.uow.components.insert(component)
    return json.dumps(component.__dict__)


@ComponentsBlueprint.route("/api/components/<parent_id>/addMappingChild", methods=["POST"])
@from_request_body("child_id", str, prop_name="childId")
@login_required
@require_permissions(['Manage Component Mapping Tree'])
def add_mapping_child(parent_id, child_id):
    return_obj = g.uow.components.add_mapping_child(parent_id, child_id)
    return jsonify(return_obj)


@ComponentsBlueprint.route("/api/components/<parent_id>/removeMappingChild", methods=["POST"])
@from_request_body("child_id", str, prop_name="childId")
@login_required
@require_permissions(['Manage Component Mapping Tree'])
def remove_mapping_child(parent_id, child_id):
    return_obj = g.uow.components.remove_mapping_child(parent_id, child_id)
    return jsonify(return_obj)


@ComponentsBlueprint.route("/api/components/addMappingRoot", methods=["POST"])
@from_request_body("child_id", str, prop_name="childId")
@login_required
@require_permissions(['Manage Component Mapping Tree'])
def add_mapping_root(child_id):
    return_obj = g.uow.components.add_mapping_root(child_id)
    return jsonify(return_obj)


@ComponentsBlueprint.route("/api/components/removeMappingRoot", methods=["POST"])
@from_request_body("child_id", str, prop_name="childId")
@login_required
@require_permissions(['Manage Component Mapping Tree'])
def remove_mapping_root(child_id):
    return_obj = g.uow.components.remove_mapping_root(child_id)
    return jsonify(return_obj)


@ComponentsBlueprint.route("/api/components/<component_id>/points", methods=["POST"])
@from_request_body("component_point", ComponentPoint)
@login_required
@require_permissions(['Manage Component Points'])
def component_point_post(component_id, component_point):
    if not component_point.code:
        response = jsonify({"message": "Code is required."})
        response.status_code = 400
        return response
    g.uow.component_points.insert(component_id, component_point)
    return json.dumps({"data": [component_point.__dict__]})


@ComponentsBlueprint.route("/api/components/<component_id>/points/<point_id>", methods=["PUT"])
@from_request_body("component_point", ComponentPoint)
@login_required
@require_permissions(['Manage Component Points'])
def component_point_put(component_id, point_id, component_point):
    if not component_point.code:
        response = jsonify({"message": "Code is required."})
        response.status_code = 400
        return response
    g.uow.component_points.update(component_point)
    return json.dumps(component_point.__dict__)


@ComponentsBlueprint.route("/api/components/<component_id>/points/<point_id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Component Points'])
def component_point_delete(component_id, point_id):
    g.uow.component_points.delete(point_id)
    return ""


@ComponentsBlueprint.route("/api/components/parseFormula", methods=["POST"])
@from_request_body("formula", dict)
@login_required
@require_any_permission(['Manage Component Structure Tree',
                         'View Component Structure Tree',
                         'Manage Component Mapping Tree',
                         'View Component Mapping Tree',
                         'Manage Component Points',
                         'View Component Points',
                         'Manage Component Engineering',
                         'View Component Engineering', ])
def parse_formula(formula):
    try:
        expression_tree = FunctionParser.parse(formula["formula"])
        return jsonify({
            "identifier_names": expression_tree["identifier_names"],
            "function_names": expression_tree["function_names"],
            "variable_names": expression_tree["variable_names"]
        })
    except Exception as e:
        js = json.dumps(e.__dict__)
        response = Response(js, status=400, mimetype="application/json")
        return response


@ComponentsBlueprint.route("/api/components/paragraphs", methods=["PUT"])
@from_request_body("paragraph", Paragraph)
@login_required
@require_permissions(['Manage Component Engineering'])
def component_paragraph_put(paragraph):
    if g.uow.paragraphs.exists(paragraph.id):
        g.uow.paragraphs.update(paragraph)
    else:
        g.uow.paragraphs.insert(paragraph)
    return ""


@ComponentsBlueprint.route("/api/components/paragraphs/<paragraph_id>", methods=["GET"])
@login_required
@require_any_permission(['View Component Engineering', 'Manage Component Engineering'])
def component_paragraph_get_specific(paragraph_id):
    sequence = g.uow.paragraphs.get(paragraph_id)
    return jsonify(sequence)


@ComponentsBlueprint.route("/api/components/paragraphs/<paragraph_id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Component Engineering'])
def component_paragraph_delete(paragraph_id):
    g.uow.paragraphs.delete(paragraph_id)
    return ""


@ComponentsBlueprint.route("/api/components/<component_id>/issues", methods=["GET"])
@login_required
@require_any_permission(['View Component Engineering', 'Manage Component Engineering'])
def component_issues_get(component_id):
    query_parameters = QueryParameters(parseqs.parse(request.query_string))
    query_result = g.uow.components.get_component_issues_table(component_id, query_parameters)

    return jsonify(query_result.to_dict())


@ComponentsBlueprint.route("/api/components/<component_id>/componentAndAncestorIssues", methods=["GET"])
@login_required
@require_any_permission(['View Component Engineering', 'Manage Component Engineering'])
def component_and_ancestor_issues_get(component_id):
    component_ids = g.uow.components.get_component_and_ancestor_ids(component_id)

    issues = g.uow.components.get_component_issues(component_ids)

    return jsonify(results=issues)


@ComponentsBlueprint.route("/api/components/<component_id>/issues", methods=["PUT"])
@from_request_body("model", ComponentIssue)
@login_required
@require_permissions(['Manage Component Engineering'])
def component_issues_insert(component_id, model):
    try:
        g.uow.components.insert_component_issue(model)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while creating issue", status_code=500)


@ComponentsBlueprint.route("/api/components/<component_id>/issues/<component_issue_id>", methods=["PUT"])
@from_request_body("model", ComponentIssue)
@login_required
@require_permissions(['Manage Component Engineering'])
def component_issues_update(component_id, component_issue_id, model):
    try:
        model.id = component_issue_id
        g.uow.components.update_component_issue(model)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while updating issue", status_code=500)


@ComponentsBlueprint.route("/api/components/issues/<component_issue_id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Component Engineering'])
def component_issues_delete(component_issue_id):
    try:
        g.uow.components.delete_component_issue(component_issue_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while deleting issue", status_code=500)


@ComponentsBlueprint.route("/api/components/<component_id>/tasks", methods=["GET"])
@login_required
@require_any_permission(['View Component Engineering', 'Manage Component Engineering'])
def component_tasks_get(component_id):
    query_parameters = QueryParameters(parseqs.parse(request.query_string))
    query_result = g.uow.components.get_component_tasks_table(component_id, query_parameters)

    return jsonify(query_result.to_dict())


@ComponentsBlueprint.route("/api/components/<component_id>/componentAndAncestorTasks", methods=["GET"])
@login_required
@require_any_permission(['View Component Engineering', 'Manage Component Engineering'])
def component_and_ancestor_tasks_get(component_id):
    component_ids = g.uow.components.get_component_and_ancestor_ids(component_id)

    tasks = g.uow.components.get_component_tasks(component_ids)

    return jsonify(results=tasks)


@ComponentsBlueprint.route("/api/components/<component_id>/tasks", methods=["PUT"])
@from_request_body("model", ComponentTask)
@login_required
@require_permissions(['Manage Component Engineering'])
def component_tasks_insert(component_id, model):
    try:
        g.uow.components.insert_component_task(model)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while creating task", status_code=500)


@ComponentsBlueprint.route("/api/components/<component_id>/tasks/<component_task_id>", methods=["PUT"])
@from_request_body("model", ComponentTask)
@login_required
@require_permissions(['Manage Component Engineering'])
def component_tasks_update(component_id, component_task_id, model):
    try:
        model.id = component_task_id
        g.uow.components.update_component_task(model)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while updating task", status_code=500)


@ComponentsBlueprint.route("/api/components/tasks/<component_task_id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Component Engineering'])
def component_tasks_delete(component_task_id):
    try:
        g.uow.components.delete_component_task(component_task_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while deleting task", status_code=500)

@ComponentsBlueprint.route("/api/components/<component_id>/<paragraph_type>/<category_id>", methods=["GET"])
@login_required
def get_paragraphs_by_type_and_category(component_id, paragraph_type, category_id):
    try:
        component_ids = g.uow.components.get_component_and_ancestor_ids(component_id)
        paragraphs = g.uow.paragraphs.get_paragraphs_by_type_and_category(component_ids, paragraph_type, category_id)
        return jsonify(results=paragraphs)
    except Exception as e:
        raise PathianException("Error while fetching paragraphs", status_code=500)


@ComponentsBlueprint.route("/api/components/<component_id>/master_point", methods=["POST"])
@from_request_body("master_point", ComponentPoint)
@login_required
@require_permissions(['Manage Component Engineering'])
def component_master_point_post(component_id, master_point):
    former_master_point = g.uow.components.get_by_id(component_id).master_point

    # remove the former reporting point
    if former_master_point:
        g.uow.component_points.revoke_master_point(former_master_point["id"])
        g.uow.component_points.delete_component_master_point_mappings_for_point(former_master_point["component_point_num"])

    # set the component's reporting point to the reporting point passed in
    g.uow.components.set_component_master_point(component_id, master_point)
    g.uow.component_points.set_master_point(master_point.id)
    g.uow.components.insert_new_component_master_point_mappings(component_id, master_point.component_point_num)

    return ""


@ComponentsBlueprint.route("/api/components", methods=["PUT"])
@from_request_body("component", Component)
@login_required
def update_component(component):
    # update the component with the new description
    actual_component = g.uow.components.get_by_number(component.num)
    if not actual_component:
        response = jsonify({'message': 'The component was not found.'})
        response.status_code = 400
        return response

    actual_component.description = component.description
    g.uow.components.update(actual_component)
    return json.dumps({"name": actual_component.num + " " + actual_component.description})


@ComponentsBlueprint.route("/api/components/<component_id>", methods=["DELETE"])
@login_required
def delete_component(component_id):
    # delete the component if it has nothing attached to it
    structure_child_components = g.uow.components.get_structure_children_of(component_id)
    if len(structure_child_components) > 0:
        response = jsonify({'message': 'The selected component has structure children.'})
        response.status_code = 405
        return response

    mapping_child_components = g.uow.components.get_mapping_children_of(component_id)
    if len(mapping_child_components) > 0:
        response = jsonify({'message': 'The selected component has mapping children.'})
        response.status_code = 405
        return response

    mapping_parent_components = g.uow.components.get_mapping_parents_of(component_id)
    if len(mapping_parent_components) > 0:
        response = jsonify({'message': 'The selected component is a mapping child of another component.'})
        response.status_code = 405
        return response

    component_equipment = g.uow.equipment.get_equipment_for_component(component_id)
    if len(component_equipment) > 0:
        response = jsonify({'message': 'The selected component is the component for an equipment.'})
        response.status_code = 405
        return response

    subcomponent_equipment = g.uow.equipment.get_equipment_for_subcomponent(component_id)
    if len(subcomponent_equipment) > 0:
        response = jsonify({'message': 'The selected component is a subcomponent for an equipment.'})
        response.status_code = 405
        return response

    component_points = g.uow.component_points.get_points_for_component_id(component_id)
    if len(component_points) > 0:
        response = jsonify({'message': 'The selected component has component points.'})
        response.status_code = 405
        return response

    # the component can be deleted
    g.uow.components.delete(component_id)
    return ""