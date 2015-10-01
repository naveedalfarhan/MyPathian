from config import DefaultConfig
from flask.ext.login import login_required
from pdfgenerator.DataReports import DataReports
from flask import Blueprint, current_app, send_from_directory, send_file, render_template

IndexBlueprint = Blueprint("IndexBlueprint", __name__)

@IndexBlueprint.route("/", methods=["GET"])
def index():
    return render_template("index.html")
    #return current_app.send_static_file("index.html")
