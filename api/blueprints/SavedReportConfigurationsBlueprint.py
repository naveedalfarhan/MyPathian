import json
from extensions.binding import from_query_string
from flask import Blueprint, session, g, request
from flask.ext.login import login_required

__author__ = 'badams'


SavedReportConfigurationsBlueprint = Blueprint("SavedReportConfigurationsBlueprint", __name__)


@SavedReportConfigurationsBlueprint.route("/api/SavedReportConfigurations", methods=["GET"])
@from_query_string("report_type", str, prop_name="type")
@login_required
def get(report_type):
    # get the user's ID so we can find their configurations only
    user_id = session["current_user"]["id"]
    configs = g.uow.saved_report_configurations.get_configuration_by_type(user_id, report_type)
    return json.dumps({'configs':configs})


@SavedReportConfigurationsBlueprint.route('/api/SavedReportConfigurations', methods=["POST"])
@login_required
def save():
    config = request.get_json()
    config['user_id'] = session['current_user']['id']
    new_id = g.uow.saved_report_configurations.insert_configuration(config)
    config['id'] = new_id
    return json.dumps({'config': config})


@SavedReportConfigurationsBlueprint.route('/api/SavedReportConfigurations/<config_id>', methods=["GET"])
@login_required
def get_report(config_id):
    config = g.uow.saved_report_configurations.get_configuration_by_id(config_id)
    return json.dumps({'config': config})