import json
from api.models.import_thread import ImportThread
from flask import Blueprint, jsonify, abort, g
from extensions.binding import require_permissions
from flask.ext.login import login_required
from energy_imports.bronze_importer import BronzeImporter

BronzeReportingBlueprint = Blueprint("BronzeReportingBlueprint", __name__)

@BronzeReportingBlueprint.route("/api/BronzeReporting", methods=["GET"])
@login_required
@require_permissions(["Run Bronze Reports"])
def bronzereporting_get():
    data = g.uow.bronze_reporting.get_submissions()
    return json.dumps(data)

@BronzeReportingBlueprint.route("/api/BronzeReporting/<submission_id>", methods=["POST"])
@login_required
@require_permissions(["Run Bronze Reports"])
def bronzereporting_process_submission(submission_id):
    try:
        model = g.uow.bronze_reporting.change_submission_state(submission_id, "processing")
        bronze_importer = BronzeImporter(model, submission_id)

        import_thread = ImportThread(bronze_importer)
        import_thread.start()

        return jsonify(model)
    except:
        abort(400)