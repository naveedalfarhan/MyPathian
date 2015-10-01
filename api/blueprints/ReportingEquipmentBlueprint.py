from api.models.ReportingConfiguration import ReportingConfiguration
from extensions.binding import from_request_body
from flask import Blueprint, send_file, g, request, session
from flask.ext.login import login_required
from pdfgenerator.ParagraphReports import generate_paragraph_report
from reporting import SharedReporting

ReportingEquipmentBlueprint = Blueprint("ReportingEquipmentBlueprint", __name__)


@ReportingEquipmentBlueprint.route("/api/ReportingEquipment/ParagraphReport", methods=["POST"])
@login_required
def get_paragraph_report():
    model = request.get_json()
    equipments = [{"equipment": g.uow.equipment.get_by_id(equipment_id).__dict__,
                   "paragraphs": g.uow.equipment.get_all_paragraphs_for_equipment(equipment_id)}
                  for equipment_id in model["equipment_ids"]]

    report_config = {"equipments": equipments}

    submitted_by = g.uow.users.get_user_by_id(session["current_user"]["id"])
    submitted_to = model["submitted_to"]

    # get the submitted by and submitted to
    submitted_by, submitted_to = SharedReporting.get_submitted_contacts(submitted_by, submitted_to, g)

    report_path = generate_paragraph_report(report_config, submitted_to, submitted_by)

    return send_file(report_path, mimetype='application/pdf')