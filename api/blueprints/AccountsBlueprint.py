import json
import sys
from time import mktime, strptime
import uuid
from datetime import datetime

from api.models.DeleteNormalizationThread import DeleteNormalizationThread
from api.models.PriceNormalization import PriceNormalization
from api.models.SizeNormalization import SizeNormalization
from api.models.UpdateNormalizationThread import UpdateNormalizationThread
from flask import jsonify, Blueprint, g
from api.models.Account import Account
from api.models.QueryParameters import QueryParameters
from extensions.binding import from_query_string, from_request_body, require_any_permission, require_permissions
from flask.ext.login import login_required
import pytz


AccountsBlueprint = Blueprint("AccountsBlueprint", __name__)


@AccountsBlueprint.route("/api/accounts", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_any_permission(["Manage Accounts", "View Accounts"])
def get_all(query_parameters):
    query_result = g.uow.accounts.get_all(query_parameters)
    return jsonify(query_result.__dict__)


@AccountsBlueprint.route("/api/accounts/for_group/<group_id>", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_any_permission(["Manage Accounts", "View Accounts"])
def get_all_by_group_id(query_parameters, group_id):
    query_result = g.uow.accounts.get_all_by_group_id(query_parameters, group_id)
    return jsonify(query_result.__dict__)


@AccountsBlueprint.route("/api/accounts/<model_id>", methods=["GET"])
@login_required
@require_permissions(["Manage Accounts"])
def get(model_id):
    ws = g.uow.accounts.get_by_id(model_id)
    return jsonify(ws.__dict__)


@AccountsBlueprint.route("/api/accounts", methods=["POST"])
@from_request_body("model", Account)
@login_required
@require_permissions(["Manage Accounts"])
def insert(model):
    print("insert")
    acct_id = g.uow.accounts.insert(model)

    # extract the price/size normalization, and update their tables
    price_normalization = PriceNormalization()
    price_normalization.account_id = acct_id
    price_normalization.effective_date = pytz.utc.localize(datetime.now()).astimezone(pytz.timezone(model.timezone))
    price_normalization.note = "Initial price normalization."
    price_normalization.value = model.initial_price_normalization
    g.uow.price_normalizations.insert(price_normalization)

    size_normalization = SizeNormalization()
    size_normalization.account_id = acct_id
    size_normalization.effective_date = pytz.utc.localize(datetime.now()).astimezone(pytz.timezone(model.timezone))
    size_normalization.note = "Initial size normalization."
    size_normalization.value = model.initial_size_normalization
    g.uow.size_normalizations.insert(size_normalization)
    return ""


@AccountsBlueprint.route("/api/accounts/<model_id>", methods=["PUT"])
@from_request_body("model", Account)
@login_required
@require_any_permission(["Manage Accounts"])
def update(model_id, model):
    model.id = model_id
    g.uow.accounts.update(model)
    return ""


@AccountsBlueprint.route("/api/accounts/<model_id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Accounts"])
def delete(model_id):
    try:
        g.uow.accounts.delete(model_id)
        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        return jsonify({"Success": "false"})


@AccountsBlueprint.route("/api/accounts/<model_id>/pricenormalizations", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_any_permission(["Manage Accounts", "View Accounts"])
def get_all_pricenormalization(model_id, query_parameters):
    query_result = g.uow.price_normalizations.get_all_by_account(model_id, query_parameters)
    for record in query_result.data:
        record["effective_date"] = record["effective_date"].strftime("%Y-%m-%d")
    return jsonify(query_result.__dict__)


@AccountsBlueprint.route("/api/accounts/<model_id>/pricenormalizations", methods=["POST"])
@from_request_body("pricenormalization", PriceNormalization)
@login_required
@require_permissions(["Manage Accounts"])
def insert_pricenormalization(model_id, pricenormalization):
    print("insert")
    pricenormalization.id = str(uuid.uuid4())  # generate Guid
    origeffectivedate = pricenormalization.effective_date
    pricenormalization.effective_date = pytz.UTC.localize(
        datetime.fromtimestamp(mktime(strptime(pricenormalization.effective_date[:10], "%Y-%m-%d"))))  # fix datetime
    pricenormalization.account_id = model_id

    pricenormalization.id = g.uow.price_normalizations.insert(pricenormalization)

    # make a copy of the normalization to prevent the thread object's value from being changed while this thread continues on
    newnorm = PriceNormalization(pricenormalization.__dict__)

    # send the updating of records and compiling to a separate thread
    update_thread = UpdateNormalizationThread('price', newnorm)
    update_thread.start()



    pricenormalization.effective_date = origeffectivedate[:10]  # zeroing out the time
    return json.dumps({"data": [pricenormalization.__dict__]})


@AccountsBlueprint.route("/api/accounts/<model_id>/pricenormalizations/<pricenormalization_id>", methods=["PUT"])
@from_request_body("pricenormalization", PriceNormalization)
@login_required
@require_permissions(["Manage Accounts"])
def update_pricenormalization(model_id, pricenormalization, pricenormalization_id):
    pricenormalization.id = pricenormalization_id
    pricenormalization.account_id = model_id
    origeffectivedate = pricenormalization.effective_date
    pricenormalization.effective_date = pytz.UTC.localize(
        datetime.fromtimestamp(mktime(strptime(pricenormalization.effective_date[:10], "%Y-%m-%d"))))  # fix datetime

    g.uow.price_normalizations.update(pricenormalization)

    # make a copy of the normalization to prevent the thread object's value from being changed while this thread continues on
    newnorm = PriceNormalization(pricenormalization.__dict__)

    # send the updating of records and compiling to a separate thread
    update_thread = UpdateNormalizationThread('price', newnorm)
    update_thread.start()

    pricenormalization.effective_date = origeffectivedate[:10]  # zeroing out the time
    return json.dumps({"data": [pricenormalization.__dict__]})


@AccountsBlueprint.route("/api/accounts/<model_id>/pricenormalizations/<pricenormalization_id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Accounts"])
def delete_pricenormalization(model_id, pricenormalization_id):
    try:
        model = g.uow.price_normalizations.get_by_id(pricenormalization_id)

        # handle deletion of normalization in another thread
        delete_thread = DeleteNormalizationThread('price', model)
        delete_thread.start()

        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        response = jsonify({"Success": "false"})
        response.status_code = 500
        return response


@AccountsBlueprint.route("/api/accounts/<model_id>/sizenormalizations", methods=["GET"])
@from_query_string("query_parameters", QueryParameters)
@login_required
@require_any_permission(["View Accounts", "Manage Accounts"])
def get_all_sizenormalization(model_id, query_parameters):
    query_result = g.uow.size_normalizations.get_all_by_account(model_id, query_parameters)
    for record in query_result.data:
        record["effective_date"] = record["effective_date"].strftime("%Y-%m-%d")
    return jsonify(query_result.__dict__)


@AccountsBlueprint.route("/api/accounts/<model_id>/sizenormalizations", methods=["POST"])
@from_request_body("sizenormalization", SizeNormalization)
@login_required
@require_permissions(["Manage Accounts"])
def insert_sizenormalization(model_id, sizenormalization):
    print("insert")
    sizenormalization.id = str(uuid.uuid4())  # generate Guid
    origeffectivedate = sizenormalization.effective_date
    sizenormalization.effective_date = pytz.UTC.localize(
        datetime.fromtimestamp(mktime(strptime(sizenormalization.effective_date[:10], "%Y-%m-%d"))))  # fix datetime
    sizenormalization.account_id = model_id

    sizenormalization.id = g.uow.size_normalizations.insert(sizenormalization)

    # make a copy of the normalization to prevent the thread object's value from being changed while this thread continues on
    newnorm = SizeNormalization(sizenormalization.__dict__)

    # send the updating of records and compiling to a separate thread
    update_thread = UpdateNormalizationThread('size', newnorm)
    update_thread.start()

    sizenormalization.effective_date = origeffectivedate[:10]  # zeroing out the time
    return json.dumps({"data": [sizenormalization.__dict__]})


@AccountsBlueprint.route("/api/accounts/<model_id>/sizenormalizations/<sizenormalization_id>", methods=["PUT"])
@from_request_body("sizenormalization", SizeNormalization)
@login_required
@require_permissions(["Manage Accounts"])
def update_sizenormalization(model_id, sizenormalization, sizenormalization_id):
    sizenormalization.id = sizenormalization_id
    sizenormalization.account_id = model_id
    origeffectivedate = sizenormalization.effective_date
    sizenormalization.effective_date = pytz.UTC.localize(
        datetime.fromtimestamp(mktime(strptime(sizenormalization.effective_date[:10], "%Y-%m-%d"))))  # fix datetime

    g.uow.size_normalizations.update(sizenormalization)

    # make a copy of the normalization to prevent the thread object's value from being changed while this thread continues on
    newnorm = SizeNormalization(sizenormalization.__dict__)

    # send the updating of records and compiling to a separate thread
    update_thread = UpdateNormalizationThread('size', newnorm)
    update_thread.start()

    sizenormalization.effective_date = origeffectivedate[:10]  # zeroing out the time
    return json.dumps({"data": [sizenormalization.__dict__]})


@AccountsBlueprint.route("/api/accounts/<model_id>/sizenormalizations/<sizenormalization_id>", methods=["DELETE"])
@login_required
@require_permissions(["Manage Accounts"])
def delete_sizenormalization(model_id, sizenormalization_id):
    try:
        model = g.uow.size_normalizations.get_by_id(sizenormalization_id)

        delete_thread = DeleteNormalizationThread('size', model)
        delete_thread.start()

        return jsonify({"Success": "true"})
    except:
        print "Error: ", sys.exc_info()[0]
        response = jsonify({"Success": "false"})
        response.status_code = 500
        return response


@AccountsBlueprint.route("/api/timezones")
def get_timezones():
    timezone_names = [{"name": tz} for tz in pytz.all_timezones]
    return json.dumps(timezone_names)
