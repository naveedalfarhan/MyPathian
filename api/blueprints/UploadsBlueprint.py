from extensions.binding import require_permissions
import import_from_master_spreadsheet
import mandrill
import json
import tempfile
import config
from flask.ext.login import login_required
import os
import uuid

from flask import jsonify, Blueprint, request, current_app, abort, g

from db.UploadsRepository import UploadsRepository


UploadsBlueprint = Blueprint("UploadsBlueprint", __name__)


@UploadsBlueprint.route("/api/uploadForAccount/<account_id>", methods=["POST"])
@login_required
@require_permissions(['Upload Group Data'])
def upload_for_account(account_id):
    f = request.files["file"]
    if f:
        try:
            newfile = tempfile.TemporaryFile()
            buf = f.stream.read(1024)
            while len(buf):
                newfile.write(buf)
                buf = f.stream.read(1024)
            f.stream.close()
            newfile.seek(0)
            import_id = UploadsRepository.start_import(account_id, newfile, "duke")
            return jsonify({"id": import_id})
        except Exception as e:
            abort(500)
    else:
        abort(400)


@UploadsBlueprint.route("/api/energy_imports", methods=["get"])
@login_required
def get_energy_imports():
    data = map(lambda x: {
        "id": str(x["id"]),
        "current_progress_point": x["thread"].importer.current_progress_point,
        "total_progress_points": x["thread"].importer.total_progress_points,
        "complete": x["thread"].importer.complete,
        "message": x["thread"].importer.message,
        "error": x["thread"].importer.error
    }, UploadsRepository.get_all())
    return json.dumps(data)


@UploadsBlueprint.route("/api/uploadBronzeReporting", methods=["POST"])
def upload_bronze_reporting():
    model = json.loads(request.form["model"])

    if model is None:
        abort(400)

    if not model["electricAccount"]["enabled"] and not model["gasAccount"]["enabled"]:
        abort(400)

    if model["electricAccount"]["enabled"] and model["electricAccount"]["uploadFormat"] == "energyStar" \
            and not "electricFile" in request.files:
        abort(400)
    if model["electricAccount"]["enabled"] and model["electricAccount"]["uploadFormat"] == "grid" \
            and not model["electricAccount"]["manualData"]:
        abort(400)

    if model["gasAccount"]["enabled"] and model["gasAccount"]["uploadFormat"] == "energyStar" \
            and not "gasFile" in request.files:
        abort(400)
    if model["gasAccount"]["enabled"] and model["gasAccount"]["uploadFormat"] == "grid" \
            and not model["gasAccount"]["manualData"]:
        abort(400)

    electric_file_contents = None
    gas_file_contents = None

    if model["electricAccount"]["enabled"]:
        if model["electricAccount"]["uploadFormat"] == "energyStar":
            file_handle = request.files["electricFile"]

            electric_file_contents = os.path.join(config.BaseConfig.BRONZE_REPORTING_FOLDER, str(uuid.uuid4()) + ".xls")
            newfile = open(electric_file_contents, 'wb+')
            newfile.write(file_handle.read())
            newfile.close()

    if model["gasAccount"]["enabled"]:
        if model["gasAccount"]["uploadFormat"] == "energyStar":
            file_handle = request.files["gasFile"]

            gas_file_contents = os.path.join(config.BaseConfig.BRONZE_REPORTING_FOLDER, str(uuid.uuid4()) + ".xls")
            newfile = open(gas_file_contents, 'wb+')
            newfile.write(file_handle.read())
            newfile.close()

    g.uow.bronze_reporting.save_submission(model, electric_file_contents, gas_file_contents)

    mandrill_client = mandrill.Mandrill(current_app.config.get("MANDRILL_API_KEY"))
    client_message = {
        "from_email": "do-not-reply@pathian.com",
        "from_name": "Pathian",
        "subject": "Your Bronze Reporting request was received",
        "text": "You have successfully sent a bronze reporting request. A Pathian representative will be in contact "
                "with you regarding your report results.",
        "to": [{
            "email": model["email"],
            "name": model["contact_name"],
            "type": "to"
        }]
    }

    electric_format = "Not provided"
    if model["electricAccount"]["enabled"]:
        if model["electricAccount"]["uploadFormat"] == "energyStar":
            electric_format = "Energy Star"
        elif model["electricAccount"]["uploadFormat"] == "grid":
            electric_format = "Grid"

    gas_format = "Not provided"
    if model["gasAccount"]["enabled"]:
        if model["gasAccount"]["uploadFormat"] == "energyStar":
            gas_format = "Energy Star"
        elif model["gasAccount"]["uploadFormat"] == "grid":
            gas_format = "Grid"

    dan_message = {
        "from_email": "do-not-reply@pathian.com",
        "from_name": "Pathian",
        "subject": "A Bronze Reporting request has been submitted",
        "text": "A bronze reporting request has been submitted.\n\n" +
                "Contact Name: " + model["contact_name"] + "\n" +
                "Organization Name: " + model["name"] + "\n" +
                "Title: " + model["title"] + "\n" +
                "Address: " + model["address"] + "\n" +
                "City: " + model["city"] + "\n" +
                "State: " + model["state"] + "\n" +
                "Zip: " + model["zip"] + "\n" +
                "Phone: " + model["address"] + "\n" +
                "Email: " + model["email"] + "\n" +
                "NAICS: " + model["naics"] + "\n" +
                "SIC: " + model["sic"] + "\n" +
                "Electric upload format: " + electric_format + "\n" +
                "Gas upload format: " + gas_format + "\n",
        "to": [{
            "email": "dbuchanan@pathian.com",
            "name": "Dan Buchanan",
            "type": "to"
        }]
    }

    result = mandrill_client.messages.send(message=client_message, async=True)
    result = mandrill_client.messages.send(message=dan_message, async=True)

    return json.dumps(True)

@UploadsBlueprint.route("/api/uploadDryComponents", methods=["POST"])
@login_required
def upload_dry_components():
    f = request.files["file"]
    if f:
        upload_id = uuid.uuid4()
        file_path = os.path.join(current_app.config["SPREADSHEET_UPLOAD_FOLDER"], str(upload_id))

        with open(file_path, "wb") as newfile:
            buf = f.stream.read(1024)
            while len(buf):
                newfile.write(buf)
                buf = f.stream.read(1024)
        f.close()

        import_from_master_spreadsheet.MasterSpreadsheetImporter.create(file_path, upload_id, dry=True)
        import_from_master_spreadsheet.MasterSpreadsheetImporter.start_dry(upload_id)

        return jsonify({"upload_id": upload_id})

@UploadsBlueprint.route("/api/uploadDryComponents/<upload_id>/progress", methods=["GET"])
@login_required
def upload_dry_components_progress(upload_id):
    try:
        upload_id = uuid.UUID(upload_id)
        upload_thread = import_from_master_spreadsheet.MasterSpreadsheetImporter.get_dry_thread(upload_id)
        return_obj = {
            "upload_id": upload_id,
            "current_progress_point": upload_thread.current_progress_point,
            "total_progress_points": upload_thread.total_progress_points,
            "running": upload_thread.running,
            "finished": upload_thread.finished,
            "error": upload_thread.error
        }
        return jsonify(return_obj)
    except:
        abort(404)

@UploadsBlueprint.route("/api/uploadDryComponents/<upload_id>/results", methods=["GET"])
@login_required
def upload_dry_components_results(upload_id):
    try:
        upload_id = uuid.UUID(upload_id)
        upload_thread = import_from_master_spreadsheet.MasterSpreadsheetImporter.get_dry_thread(upload_id)
        return_obj = {
            "upload_id": upload_id,
            "results": upload_thread.results
        }
        return jsonify(return_obj)
    except:
        abort(404)

@UploadsBlueprint.route("/api/uploadComponents/<upload_id>", methods=["POST"])
@login_required
def upload_components(upload_id):
    try:
        file_path = os.path.join(current_app.config["SPREADSHEET_UPLOAD_FOLDER"], str(upload_id))
        upload_id = uuid.UUID(upload_id)
        import_from_master_spreadsheet.MasterSpreadsheetImporter.create(file_path, upload_id, dry=False)
        import_from_master_spreadsheet.MasterSpreadsheetImporter.start_wet(upload_id)
        return jsonify({"status": "success"})
    except:
        current_app.logger.exception("An error occured uploading components")
        return jsonify({"status": "error"})

@UploadsBlueprint.route("/api/uploadComponents/<upload_id>/progress", methods=["GET"])
@login_required
def upload_components_progress(upload_id):
    try:
        upload_id = uuid.UUID(upload_id)
        upload_thread = import_from_master_spreadsheet.MasterSpreadsheetImporter.get_wet_thread(upload_id)
        return_obj = {
            "upload_id": upload_id,
            "current_progress_point": upload_thread.current_progress_point,
            "total_progress_points": upload_thread.total_progress_points,
            "running": upload_thread.running,
            "finished": upload_thread.finished,
            "error": upload_thread.error
        }
        return jsonify(return_obj)
    except:
        abort(404)