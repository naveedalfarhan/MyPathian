from vendor_data_pipeline.post_handler import PostHandler
#from vendor_data_pipeline.siemens_data_handler import SiemensDataHandler
import os
from flask import Blueprint, request, current_app, jsonify, abort
import datetime
import json
from pdb import set_trace as trace


DataDumpBlueprint = Blueprint("DataDumpBlueprint", __name__)


@DataDumpBlueprint.route("/api/data_dump/test", methods=["GET", "POST"])
def test():
    return jsonify({"test": "test"})


@DataDumpBlueprint.route("/", methods=["POST"])
@DataDumpBlueprint.route("/api/data_dump/fieldserver", methods=["POST"])
def fieldserver_post():
    try:
        current_app.logger.debug("Fieldserver post received")

        post_handler = PostHandler()
        post_handler.handle_fieldserver_post(request.form)

        current_app.logger.info("Fieldserver post successful")
        return jsonify({"success": True})
    except:
        current_app.logger.exception("An error occurred attempting to post fieldserver data")
        abort(500)


@DataDumpBlueprint.route("/api/data_dump/invensys", methods=["POST"])
def invensys_post():
    try:
        current_app.logger.debug("Invensys post received")
        if len(request.files) > 0:
            file_key = request.files.keys()[0]
            uploaded_file = request.files[file_key]
            post_handler = PostHandler()
            post_handler.handle_invensys_post(uploaded_file)

            current_app.logger.info("Invensys post successful")
            return jsonify({"success": True})

        else:
            current_app.logger.warn("Invensys post received without attached file. Now checking for form post")

            post_handler = PostHandler()
            post_handler.handle_invensys_form_post(request.form)

        current_app.logger.info("Invensys post successful")
        return jsonify({"success": True})
    except:
        current_app.logger.exception("An error occurred attempting to post invensys data")
        abort(500)


@DataDumpBlueprint.route("/api/data_dump/johnson", methods=["POST"])
def johnson_post():
    try:
        current_app.logger.debug("Johnson post received")
        if len(request.files) > 0:
            file_key = request.files.keys()[0]

            # read the uploaded file to a string, then split the string by linebreaks to form a list
            # of records. done this way to allow multiple import functions to use the import file
            # (the uploaded file can only be read once)

            uploaded_file = request.files[file_key]
            uploaded_file_string = uploaded_file.read().replace("\r\n", "\n").replace("\r", "\n")
            records = uploaded_file_string.split("\n")

            post_handler = PostHandler()
            post_handler.handle_johnson_post(records)

        else:
            current_app.logger.warn("Johnson post received without attached file")
            abort(500)  # throws an exception

        current_app.logger.info("Johnson post successful")
        return jsonify({"success": True})
    except:
        current_app.logger.exception("An error occurred attempting to post johnson data")
        abort(500)
