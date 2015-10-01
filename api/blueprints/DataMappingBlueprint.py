import tempfile
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body
from flask import Blueprint, request, jsonify, abort, g, send_file
from flask.ext.login import login_required
import os
from openpyxl import Workbook

DataMappingBlueprint = Blueprint("DataMappingBlueprint", __name__)


@DataMappingBlueprint.route("/api/data_mapping/johnson", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def johnson_get(query_parameters):
    query_result = g.uow.data_mapping.apply_query_parameters(query_parameters, "johnson")
    return jsonify(query_result.to_dict())


@DataMappingBlueprint.route("/api/data_mapping/johnson", methods=["POST"])
@login_required
@from_request_body("model", dict)
def johnson_insert(model):
    try:
        g.uow.data_mapping.insert_mapping(model, "johnson")
        if not model['global']:
            g.uow.data_mapping.remove_unknown_johnson_vendor_point(model["johnson_site_id"], model["johnson_fqr"])
        else:
            g.uow.data_mapping.make_johnson_point_global(model["johnson_site_id"], model["johnson_fqr"])
        return jsonify({"data": [model]})
    except:
        abort(400)


@DataMappingBlueprint.route("/api/data_mapping/johnson/<model_id>", methods=["PUT"])
@login_required
@from_request_body("model", dict)
def johnson_update(model_id, model):
    try:
        g.uow.data_mapping.update_mapping(model_id, model, "johnson")
        return jsonify({"data": [model]})
    except:
        abort(400)


@DataMappingBlueprint.route("/api/data_mapping/johnson/<model_id>", methods=["DELETE"])
@login_required
def johnson_delete(model_id):
    model = g.uow.data_mapping.get_mapping_by_id(model_id)
    unknown_mapping = {
        "johnson_site_id": model["johnson_site_id"],
        "johnson_fqr": model["johnson_fqr"],
        "source": "johnson"
    }
    g.uow.data_mapping.delete_mapping(model_id)
    g.uow.data_mapping.insert_unknown_vendor_points(unknown_mapping)
    return jsonify({})


@DataMappingBlueprint.route("/api/data_mapping/unknownJohnson", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def johnson_get_unknown(query_parameters):
    query_result = g.uow.data_mapping.unknown_johnson_apply_query_parameters(query_parameters)
    return jsonify(query_result.to_dict())


@DataMappingBlueprint.route("/api/data_mapping/unknownJohnson/excel", methods=["GET"])
@login_required
def johnson_get_unknown_excel():
    vendor_points = g.uow.data_mapping.get_unknown_vendor_points_for_johnson()

    wb = Workbook(optimized_write=True)
    ws = wb.create_sheet()
    ws.title = "Unknown Johnson points"

    ws.append(["Johnson Site Id", "Johnson FQR", "Syrx Num"])

    for p in vendor_points:
        ws.append([str(p["johnson_site_id"]), str(p["johnson_fqr"])])


    f_path = tempfile.NamedTemporaryFile().name

    wb.save(f_path)

    return send_file(f_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, attachment_filename="unknown_johnson_points.xlsx")


@DataMappingBlueprint.route("/api/data_mapping/unknownJohnson/upload", methods=["POST"])
@login_required
def johnson_upload_unknown_excel():
    f = request.files["file"]
    if f:
        (fd, newfile_path) = tempfile.mkstemp()
        buf = f.stream.read(1024)
        newfile = open(newfile_path, "wb")
        while len(buf):
            newfile.write(buf)
            buf = f.stream.read(1024)
        f.stream.close()
        newfile.close()

        newfile = open(newfile_path, "rb")
        upload_results = g.uow.data_mapping.upload_johnson_mappings(newfile)
        newfile.close()
        os.close(fd)
        os.remove(newfile_path)
        return jsonify(upload_results.__dict__)
    abort(400)


@DataMappingBlueprint.route("/api/data_mapping/invensys", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def invensys_get(query_parameters):
    query_result = g.uow.data_mapping.apply_query_parameters(query_parameters, "invensys")
    return jsonify(query_result.to_dict())


@DataMappingBlueprint.route("/api/data_mapping/invensys", methods=["POST"])
@login_required
@from_request_body("model", dict)
def invensys_insert(model):
    try:
        g.uow.data_mapping.insert_mapping(model, "invensys")
        if not model['global']:
            g.uow.data_mapping.remove_unknown_invensys_vendor_point(model["invensys_site_name"], model["invensys_equipment_name"], model["invensys_point_name"])
        else:
            g.uow.data_mapping.make_invensys_point_global(model["invensys_site_name"], model["invensys_equipment_name"],
                                                          model["invensys_point_name"])
        return jsonify({"data": [model]})
    except:
        abort(400)


@DataMappingBlueprint.route("/api/data_mapping/invensys/<model_id>", methods=["PUT"])
@login_required
@from_request_body("model", dict)
def invensys_update(model_id, model):
    try:
        g.uow.data_mapping.update_mapping(model_id, model, "invensys")
        return jsonify({"data": [model]})
    except:
        abort(400)


@DataMappingBlueprint.route("/api/data_mapping/invensys/<model_id>", methods=["DELETE"])
@login_required
def invensys_delete(model_id):
    model = g.uow.data_mapping.get_mapping_by_id(model_id)
    unknown_mapping = {
        "invensys_site_name": model["invensys_site_name"],
        "invensys_equipment_name": model["invensys_equipment_name"],
        "invensys_point_name": model["invensys_point_name"],
        "source": "invensys"
    }
    g.uow.data_mapping.delete_mapping(model_id)
    g.uow.data_mapping.insert_unknown_vendor_points(unknown_mapping)
    return jsonify({})


@DataMappingBlueprint.route("/api/data_mapping/unknownInvensys")
@login_required
@from_query_string("query_parameters", QueryParameters)
def invensys_get_unknown(query_parameters):
    query_result = g.uow.data_mapping.unknown_invensys_apply_query_parameters(query_parameters)
    return jsonify(query_result.to_dict())


@DataMappingBlueprint.route("/api/data_mapping/siemens", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def siemens_get(query_parameters):
    query_result = g.uow.data_mapping.apply_query_parameters(query_parameters, "siemens")
    return jsonify(query_result.to_dict())


@DataMappingBlueprint.route("/api/data_mapping/siemens", methods=["POST"])
@login_required
@from_request_body("model", dict)
def siemens_insert(model):
    try:
        g.uow.data_mapping.insert_mapping(model, "siemens")
        if not model['global']:
            g.uow.data_mapping.remove_unknown_siemens_vendor_point(model["siemens_meter_name"])
        else:
            g.uow.data_mapping.make_siemens_point_global(model['siemens_meter_name'])
        return jsonify({"data": [model]})
    except:
        abort(400)


@DataMappingBlueprint.route("/api/data_mapping/siemens/<model_id>", methods=["PUT"])
@login_required
@from_request_body("model", dict)
def siemens_update(model_id, model):
    try:
        g.uow.data_mapping.update_mapping(model_id, model, "siemens")
        return jsonify({"data": [model]})
    except:
        abort(400)


@DataMappingBlueprint.route("/api/data_mapping/siemens/<model_id>", methods=["DELETE"])
@login_required
def siemens_delete(model_id):
    model = g.uow.data_mapping.get_mapping_by_id(model_id)
    unknown_mapping = {
        "siemens_meter_name": model["siemens_meter_name"],
        "source": "siemens"
    }
    g.uow.data_mapping.delete_mapping(model_id)
    g.uow.data_mapping.insert_unknown_vendor_points(unknown_mapping)
    return jsonify({})


@DataMappingBlueprint.route("/api/data_mapping/unknownSiemens")
@login_required
@from_query_string("query_parameters", QueryParameters)
def siemens_get_unknown(query_parameters):
    query_result = g.uow.data_mapping.unknown_siemens_apply_query_parameters(query_parameters)
    return jsonify(query_result.to_dict())


@DataMappingBlueprint.route("/api/data_mapping/fieldserver", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def fieldserver_get(query_parameters):
    query_result = g.uow.data_mapping.apply_query_parameters(query_parameters, "fieldserver")
    return jsonify(query_result.to_dict())


@DataMappingBlueprint.route("/api/data_mapping/fieldserver", methods=["POST"])
@login_required
@from_request_body("model", dict)
def fieldserver_insert(model):
    try:
        g.uow.data_mapping.insert_mapping(model, "fieldserver")
        if not model['global']:
            g.uow.data_mapping.remove_unknown_fieldserver_vendor_point(model["fieldserver_site_id"], model["fieldserver_offset"])
        else:
            g.uow.data_mapping.make_fieldserver_point_global(model["fieldserver_site_id"], model["fieldserver_offset"])
        return jsonify({"data": [model]})
    except:
        abort(400)


@DataMappingBlueprint.route("/api/data_mapping/fieldserver/<model_id>", methods=["PUT"])
@login_required
@from_request_body("model", dict)
def fieldserver_update(model_id, model):
    try:
        g.uow.data_mapping.update_mapping(model_id, model, "fieldserver")
        return jsonify({"data": [model]})
    except:
        abort(400)


@DataMappingBlueprint.route("/api/data_mapping/fieldserver/<model_id>", methods=["DELETE"])
@login_required
def fieldserver_delete(model_id):
    model = g.uow.data_mapping.get_mapping_by_id(model_id)
    unknown_mapping = {
        "fieldserver_site_id": model["fieldserver_site_id"],
        "fieldserver_offset": model["fieldserver_offset"],
        "source": "fieldserver"
    }
    g.uow.data_mapping.delete_mapping(model_id)
    g.uow.data_mapping.insert_unknown_vendor_points(unknown_mapping)
    return jsonify({})


@DataMappingBlueprint.route("/api/data_mapping/unknownFieldserver", methods=["GET"])
@login_required
@from_query_string("query_parameters", QueryParameters)
def fieldserver_get_unknown(query_parameters):
    query_result = g.uow.data_mapping.unknown_fieldserver_apply_query_parameters(query_parameters)
    return jsonify(query_result.to_dict())


def find_global_value(vendor_mapping):
    """
    Finds whether or not the global property for the given mapping should be true or false
    """
    if vendor_mapping['source'] == 'johnson':
        mappings = g.uow.data_mapping.get_mappings_for_johnson_site_id_fqr([[vendor_mapping['johnson_site_id'],
                                                                             vendor_mapping['johnson_fqr']]])
    elif vendor_mapping['source'] == 'fieldserver':
        mappings = g.uow.data_mapping.get_mappings_for_fieldserver_site_id_offset([[vendor_mapping['fieldserver_site_id'],
                                                                                    vendor_mapping['fieldserver_offset']]])
    elif vendor_mapping['source'] == 'invensys':
        mappings = g.uow.data_mapping.get_mappings_for_invensys_site_equipment_point([[vendor_mapping['invensys_site_name'],
                                                                                       vendor_mapping['invensys_equipment_name'],
                                                                                       vendor_mapping['invensys_point_name']]])
    else:
        mappings = g.uow.data_mapping.get_mappings_for_siemens_meter_name([[vendor_mapping['siemens_meter_name']]])

    mappings = list(mappings)

    return len(mappings) > 0


@DataMappingBlueprint.route("/api/data_mapping/<syrx_num>", methods=["DELETE"])
@login_required
def unmap_syrx_number(syrx_num):
    # get the equipment point from the database along with it's mapping
    equipment_point = g.uow.equipment.get_equipment_point_by_syrx_num(syrx_num)

    if not equipment_point:
        abort(400)

    vendor_mapping = g.uow.data_mapping.get_mapping_by_syrx_num(syrx_num)

    if not vendor_mapping:
        abort(400)

    # remove the syrx-vendor mapping
    g.uow.data_mapping.delete_mapping(vendor_mapping['id'])

    # remove id and syrx_num from vendor_mapping
    del vendor_mapping['syrx_num']
    del vendor_mapping['id']

    # remove global property
    del vendor_mapping['global']

    unmapping = {
        "syrx_num": syrx_num,
        "vendor_point": vendor_mapping
    }
    # add syrx_num to unmapped_syrx_nums table
    g.uow.unmapped_syrx_nums.add_syrx_num(unmapping)

    should_be_global = find_global_value(vendor_mapping)

    if not should_be_global:
        # if the point has no other mappings, then restore it's global property to false
        g.uow.data_mapping.remove_global_property(vendor_mapping)

    return ""
