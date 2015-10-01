from collections import defaultdict
import json
from api.models.ConsumptionTextReport import ConsumptionTextReport
import locale
from api.models.ReportingConfiguration import ReportingConfiguration
from api.models.NaicsReportingConfiguration import NaicsReportingConfiguration
from api.models.SicReportingConfiguration import SicReportingConfiguration
from extensions.binding import from_request_body, require_permissions
from flask import Blueprint, g
from flask.ext.login import login_required
from reporting import SharedReporting

ReportingTextBlueprint = Blueprint("ReportingTextBlueprint", __name__)


@ReportingTextBlueprint.route("/api/TextReports/GroupsReport", methods=["POST"])
@from_request_body("config", ReportingConfiguration)
@login_required
@require_permissions(['Run Group Reports'])
def generate_group_text_report(config):
    return json.dumps(SharedReporting.generate_consumptiontext_report(config, 'groups', g))


@ReportingTextBlueprint.route("/api/TextReports/NaicsReport", methods=["POST"])
@from_request_body("config", ReportingConfiguration)
@login_required
@require_permissions(['Run NAICS Reports'])
def generate_naics_report(config):
    return json.dumps(SharedReporting.generate_consumptiontext_report(config, 'naics', g))


@ReportingTextBlueprint.route("/api/TextReports/SicReport", methods=["POST"])
@from_request_body("config", SicReportingConfiguration)
@login_required
@require_permissions(['Run SIC Reports'])
def generate_sic_report(config):
    return json.dumps(SharedReporting.generate_consumptiontext_report(config, 'sic', g))