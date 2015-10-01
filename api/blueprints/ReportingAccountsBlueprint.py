from api.models.QueryParameters import QueryParameters
from flask import Blueprint, request, g, jsonify
from flask.ext.login import login_required
from parseqs import parseqs

__author__ = 'Brian'

ReportingAccountsBlueprint = Blueprint("ReportingAccountsBlueprint", __name__)


@ReportingAccountsBlueprint.route("/api/reporting/accounts/<account_id>")
@login_required
def get_account_data(account_id):
    # parse the query string into parameters
    query_parameters = QueryParameters(parseqs.parse(request.query_string))
    query_result = g.uow.energy_records.get_all_for_account_between_dates(account_id, query_parameters)
    return jsonify(query_result.to_dict())