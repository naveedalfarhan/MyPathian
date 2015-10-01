from datetime import datetime
import json
from time import mktime, strptime, strftime
import uuid

from flask import jsonify, Blueprint, abort, g, request, current_app

from PathianExceptions import PathianException
from api.models.Equipment import Equipment
from api.models.EquipmentRaf import EquipmentRaf
from api.models.EquipmentParagraph import EquipmentParagraph
from api.models.EquipmentIssue import EquipmentIssue
from api.models.EquipmentTask import EquipmentTask
from extensions.binding import from_query_string, require_any_permission, require_permissions
from extensions.binding import from_request_body, from_request_body_key_value
from api.models.QueryParameters import QueryParameters, QueryResult
from flask.ext.login import login_required
from parseqs import parseqs
import pytz


EquipmentBlueprint = Blueprint("EquipmentBlueprint", __name__)


@EquipmentBlueprint.route("/api/equipment", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_any_permission(['Manage Equipment', 'View Equipment'])
def get_all(query_parameters):
    query_result = g.uow.equipment.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/equipmentForGroup/<group_id>", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_any_permission(['Manage Equipment', 'View Equipment'])
def get_all_by_group(group_id, query_parameters):
    query_result = g.uow.equipment.get_all_by_group(group_id, query_parameters)
    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/paragraphs/<paragraph_type>")
def get_paragraphs_for_equipment(equipment_id, paragraph_type):
    paragraphs = g.uow.equipment.get_all_paragraphs_for_equipment(equipment_id, paragraph_type)

    return jsonify(results=paragraphs)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>", methods=["GET"])
@login_required
@require_permissions(['Manage Equipment'])
def get_one(equipment_id):
    equipment = g.uow.equipment.get_by_id(equipment_id)
    if equipment is None:
        abort(404)
        return
    return json.dumps(equipment.__dict__)


@EquipmentBlueprint.route("/api/equipment/managerTree", methods=["GET"])
@from_query_string("equipment_id", str, prop_name="id")
@login_required
def manager_tree(equipment_id):
    if equipment_id is None or equipment_id[0:7] == "groups:":
        group_id = equipment_id
        if group_id is not None and group_id[0:7] == "groups:":
            group_id = group_id[7:]
        groups = g.uow.groups.get_child_groups_of(group_id)
        groups = [{"id": "group:" + gr["id"], "type": "group", "group_id": gr["id"],
                   "name": gr["name"], "hasChildren": True} for gr in groups]
        return json.dumps(groups)
    elif equipment_id[0:11] == "equipments:":
        group_id = equipment_id[11:]
        group = g.uow.groups.get_group_by_id(group_id)
        equipments = g.uow.equipment.get_all_by_group(group_id)
        equipments = [{"id": "equipment:" + e["id"], "type": "equipment", "hasChildren": False,
                       "equipment_id": e["id"], "name": e["name"],
                       "group_id": group_id, "group_name": group.name} for e in equipments]
        return json.dumps(equipments)
    elif equipment_id[0:6] == "group:":
        group_id = equipment_id[6:]
        elements = [
            {"id": "groups:" + group_id, "name": "Groups", "hasChildren": True},
            {"id": "equipments:" + group_id, "name": "Equipment", "hasChildren": True}
        ]
        return json.dumps(elements)


@EquipmentBlueprint.route("/api/equipment", methods=["POST"])
@from_request_body("model", Equipment)
@login_required
@require_permissions(['Manage Equipment'])
def insert(model):
    try:
        group_id = model.group_id
        assert group_id is not None
    except:
        raise PathianException('Group Id cannot be null.', status_code=400)

    try:
        g.uow.equipment.insert(group_id, model)
        return ""
    except:
        raise PathianException('Error while inserting equipment.', status_code=500)


@EquipmentBlueprint.route("/api/equipment/<model_id>", methods=["PUT"])
@from_request_body("model", Equipment)
@login_required
@require_permissions(['Manage Equipment'])
def update(model_id, model):
    try:
        model.id = model_id
        g.uow.equipment.update(model)
        return ""
    except Exception as e:
        current_app.logger.error(e.message)
        raise PathianException('Error while saving equipment.', status_code=500)


@EquipmentBlueprint.route("/api/equipment/<model_id>", methods=["DELETE"])
@login_required
@require_permissions(['Manage Equipment'])
def delete(model_id):
    try:
        g.uow.equipment.delete(model_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        abort(400)


@EquipmentBlueprint.route("/api/equipment_points", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_permissions(["Run Point Data Report"])
def get_all_equipment_points(query_parameters=None):
    query_result = g.uow.equipment.get_all_equipment_points_query_result(query_parameters)
    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/vendor_points", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_permissions(["Run Point Data Report"])
def get_all_vendor_points(query_parameters=None):
    query_result = g.uow.equipment.get_all_vendor_points_query_result(query_parameters)
    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/equipment/equipment_point_records", methods=["POST"])
@login_required
@require_permissions(["Run Point Data Report"])
def get_equipment_point_records_for_syrx_num_date():
    data = parseqs.parse(request.get_data())
    query_parameters = QueryParameters(data)

    start_date = int(data["startDate"])
    end_date = int(data["endDate"])

    query_result = g.uow.equipment.get_all_equipment_point_records_query_result(data["syrxNums"], start_date,
                                                                                end_date, query_parameters)

    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/equipment/vendor_records", methods=["POST"])
@login_required
@require_permissions(["Run Point Data Report"])
def get_vendor_records_for_syrx_num_date():
    data = parseqs.parse(request.get_data())
    query_parameters = QueryParameters(data)

    start_date = int(data["startDate"])
    end_date = int(data["endDate"])

    query_result = g.uow.equipment.get_all_vendor_records_query_result(data["points"], start_date,
                                                                       end_date, query_parameters)

    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/points", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
def equipment_points_get_by_equipment_id(query_parameters, equipment_id):
    query_result = g.uow.equipment.get_equipment_points_by_equipment_id(query_parameters, equipment_id)
    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/allPoints", methods=["GET"])
@login_required
def equipment_points_get_all_by_equipment_id(equipment_id):
    points = g.uow.equipment.get_equipment_points_by_equipment_id(None, equipment_id)
    return jsonify({"data": points, "total": len(points)})


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/mapped_points", methods=["GET"])
@login_required
def get_mapped_equipment_points(equipment_id):
    points = g.uow.equipment.get_equipment_points_by_equipment_id(None, equipment_id)
    point_syrx_nums = map(lambda x: x["syrx_num"], points)

    # map the description to each syrx num
    descriptions_by_syrx_num = dict((x['syrx_num'], x['point_description']) for x in points)
    mapped_points = g.uow.data_mapping.get_mappings_by_syrx_nums(point_syrx_nums)

    # update the mapped points with a description
    mapped_points = [{'syrx_num': p['syrx_num'], 'description': descriptions_by_syrx_num[p['syrx_num']]}
                     for p in mapped_points]
    return json.dumps(mapped_points)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/mapped_points_grid", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def get_mapped_equipment_points_grid(equipment_id, query_parameters):
    points = g.uow.equipment.get_equipment_points_by_equipment_id(None, equipment_id)
    point_syrx_nums = map(lambda x: x["syrx_num"], points)
    mapped_points = g.uow.data_mapping.get_mappings_by_syrx_nums(point_syrx_nums)

    start = query_parameters.skip
    end = query_parameters.skip + query_parameters.take
    data = mapped_points[start:end]
    total = len(mapped_points)

    query_result = QueryResult(data, total)
    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/unmapped_points", methods=["GET"])
@login_required
def get_unmapped_equipment_points(equipment_id):
    points = g.uow.equipment.get_equipment_points_by_equipment_id(None, equipment_id)
    point_syrx_nums = map(lambda x: x["syrx_num"], points)
    mapped_points = g.uow.data_mapping.get_mappings_by_syrx_nums(point_syrx_nums)
    mapped_points_by_syrx_num = dict((x["syrx_num"], x) for x in mapped_points)
    unmapped_points = [x for x in points if x["syrx_num"] not in mapped_points_by_syrx_num]
    return json.dumps(unmapped_points)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/unmapped_points_grid", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def get_unmapped_equipment_points_grid(equipment_id, query_parameters):
    points = g.uow.equipment.get_equipment_points_by_equipment_id(None, equipment_id)
    point_syrx_nums = map(lambda x: x["syrx_num"], points)
    mapped_points = g.uow.data_mapping.get_mappings_by_syrx_nums(point_syrx_nums)
    mapped_points_by_syrx_num = dict((x["syrx_num"], x) for x in mapped_points)
    unmapped_points = [x for x in points if x["syrx_num"] not in mapped_points_by_syrx_num
                       and 'point_type' in x and x["point_type"] in ["EP", "BP", "PP"]]

    start = query_parameters.skip
    end = query_parameters.skip + query_parameters.take
    data = unmapped_points[start:end]
    total = len(unmapped_points)

    query_result = QueryResult(data, total)
    return jsonify(query_result.__dict__)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/ci", methods=["GET"])
@login_required
def equipment_issues_get(equipment_id):
    issues = g.uow.equipment.get_equipment_issues(equipment_id)
    return jsonify(results=issues)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/ci", methods=["PUT"])
@from_request_body("model", EquipmentIssue)
@login_required
def equipment_issue_create(equipment_id, model):
    try:
        issue_id = g.uow.equipment.insert_equipment_issue(model)
        return jsonify({"Success": "true", "id": issue_id})
    except Exception as e:
        raise PathianException("Error while inserting equipment issue", status_code=500)


@EquipmentBlueprint.route("/api/equipment/ci/<equipment_issue_id>", methods=["PUT"])
@from_request_body("model", EquipmentIssue)
@login_required
def equipment_issue_update(equipment_issue_id, model):
    try:
        model.id = equipment_issue_id
        g.uow.equipment.update_equipment_issue(model)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while updating equipment issue", status_code=500)


@EquipmentBlueprint.route("/api/equipment/ci/<equipment_issue_id>", methods=["DELETE"])
@login_required
def equipment_issue_delete(equipment_issue_id):
    try:
        g.uow.equipment.delete_equipment_issue(equipment_issue_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while deleting equipment task", status_code=500)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/ct", methods=["GET"])
@login_required
def equipment_tasks_get(equipment_id):
    tasks = g.uow.equipment.get_equipment_tasks(equipment_id)
    return jsonify(results=tasks)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/ct", methods=["PUT"])
@from_request_body("model", EquipmentTask)
@login_required
def equipment_task_create(equipment_id, model):
    try:
        task_id = g.uow.equipment.insert_equipment_task(model)
        return jsonify({"Success": "true", "id": task_id})
    except Exception as e:
        raise PathianException("Error while inserting equipment task", status_code=500)


@EquipmentBlueprint.route("/api/equipment/ct/<equipment_task_id>", methods=["PUT"])
@from_request_body("model", EquipmentTask)
@login_required
def equipment_task_update(equipment_task_id, model):
    try:
        model.id = equipment_task_id
        g.uow.equipment.update_equipment_task(model)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while inserting equipment task", status_code=500)


@EquipmentBlueprint.route("/api/equipment/ct/<equipment_task_id>", methods=["DELETE"])
@login_required
def equipment_task_delete(equipment_task_id):
    try:
        g.uow.equipment.delete_equipment_task(equipment_task_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while deleting equipment task", status_code=500)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/paragraphs/<paragraph_id>/moveup", methods=["POST"])
@login_required
def equipment_paragraph_move_up(equipment_id, paragraph_id):
    try:
        g.uow.equipment.move_paragraph_up(equipment_id, paragraph_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException('Error while updating paragraph.', status_code=500)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/paragraphs/<paragraph_id>/movedown", methods=["POST"])
@login_required
def equipment_paragraph_move_down(equipment_id, paragraph_id):
    try:
        g.uow.equipment.move_paragraph_down(equipment_id, paragraph_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException('Error while updating paragraph.', status_code=500)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/paragraphs/<paragraph_id>/delete", methods=["POST"])
@login_required
def equipment_paragraph_delete(equipment_id, paragraph_id):
    try:
        g.uow.equipment.delete_paragraph(equipment_id, paragraph_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException('Error while deleting paragraph.', status_code=500)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/paragraphs/<paragraph_id>", methods=['PUT'])
@login_required
def add_paragraph(equipment_id, paragraph_id):
    try:
        g.uow.equipment.add_paragraph(equipment_id, paragraph_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while adding paragraph", status_code=500)


@EquipmentBlueprint.route("/api/equipment/paragraphs", methods=['PUT'])
@from_request_body("model", EquipmentParagraph)
@login_required
def insert_paragraph(model):
    try:
        paragraph_id = g.uow.equipment.insert_paragraph(model)
        return jsonify({"Success": "true", "id": paragraph_id})
    except Exception as e:
        raise PathianException("Error while inserting paragraph", status_code=500)


@EquipmentBlueprint.route("/api/equipment/paragraphs/<paragraph_id>", methods=["PUT"])
@from_request_body("model", EquipmentParagraph)
def update_paragraph(paragraph_id, model):
    try:
        model.id = paragraph_id

        # only allow editing title and description
        del model.category_id
        del model.equipment_id
        del model.num
        del model.paragraph_id
        del model.sort_order
        del model.type

        g.uow.equipment.update_paragraph(model)
        return ""
    except:
        raise PathianException('Error while saving paragraph.', status_code=500)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/raf", methods=['GET'])
@login_required
def get_raf(equipment_id):
    return jsonify(results=g.uow.equipment.get_raf(equipment_id))


@EquipmentBlueprint.route("/api/equipment/raf", methods=['PUT'])
@from_request_body("model", EquipmentRaf)
@login_required
def insert_raf(model):
    try:
        raf_id = g.uow.equipment.insert_raf(model)
        return jsonify({"Success": "true", "id": raf_id})
    except Exception as e:
        raise PathianException("Error while inserting raf pressure", status_code=500)


@EquipmentBlueprint.route("/api/equipment/raf/<raf_id>", methods=['DELETE'])
@login_required
def delete_raf(raf_id):
    try:
        g.uow.equipment.delete_raf(raf_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException('Error while deleting raf pressure.', status_code=500)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/rs/<reset_schedule_id>", methods=['PUT'])
@login_required
def add_reset_schedule(equipment_id, reset_schedule_id):
    try:
        g.uow.equipment.add_reset_schedule(equipment_id, reset_schedule_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while inserting reset schedule", status_code=500)


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/rs", methods=['GET'])
@login_required
def get_reset_schedules(equipment_id):
    return jsonify(results=g.uow.equipment.get_reset_schedules(equipment_id))


@EquipmentBlueprint.route("/api/equipment/<equipment_id>/rs/<reset_schedule_id>", methods=['DELETE'])
@login_required
def delete_reset_schedule(equipment_id, reset_schedule_id):
    try:
        g.uow.equipment.delete_reset_schedule(equipment_id, reset_schedule_id)
        return jsonify({"Success": "true"})
    except Exception as e:
        raise PathianException("Error while deleting reset schedule", status_code=500)


@EquipmentBlueprint.route("/api/equipment/numeric_points/<equipment_point_id>/values", methods=['GET'])
@login_required
def get_numeric_point_values(equipment_point_id):
    values = g.uow.equipment.get_values_for_numeric_point(equipment_point_id)
    if values is None:
        return jsonify({"data": [], "length": 0})
    for r in values:
        r["effective_date"] = r["effective_date"].strftime("%Y-%m-%d")
    return jsonify({"data": values, "total": len(values)})


@EquipmentBlueprint.route("/api/equipment/numeric_points/<equipment_point_id>/values", methods=['POST'])
@login_required
def insert_numeric_point_value(equipment_point_id):
    model = request.get_json()
    model["id"] = str(uuid.uuid4())
    model["effective_date"] = pytz.UTC.localize(datetime.fromtimestamp(mktime(strptime(model["effective_date"][:10],
                                                                                       "%Y-%m-%d"))))  # fix datetime
    g.uow.equipment.insert_value_for_numeric_point(equipment_point_id, model)

    model["effective_date"] = model["effective_date"].strftime("%Y-%m-%d")

    return json.dumps({"data": [model]})


@EquipmentBlueprint.route("/api/equipment/numeric_points/<equipment_point_id>/values/<value_id>", methods=['PUT'])
@login_required
def update_numeric_point_value(equipment_point_id, value_id):
    model = request.get_json()
    model["id"] = value_id
    model["effective_date"] = pytz.UTC.localize(datetime.fromtimestamp(mktime(strptime(model["effective_date"][:10],
                                                                                       "%Y-%m-%d"))))  # fix datetime
    g.uow.equipment.update_value_for_numeric_point(equipment_point_id, model)

    model["effective_date"] = model["effective_date"].strftime("%Y-%m-%d")

    return json.dumps({"data": [model]})


@EquipmentBlueprint.route("/api/equipment/numeric_points/<equipment_point_id>/values/<value_id>", methods=['DELETE'])
@login_required
def delete_numeric_point_value(equipment_point_id, value_id):
    g.uow.equipment.delete_value_for_numeric_point(equipment_point_id, value_id)
    return jsonify({"Success": "true"})
