# Configuration and file structure based on sample here: https://github.com/imwilsonxu/fbone
from api.blueprints.DataMappingBlueprint import DataMappingBlueprint
from api.blueprints.ReportingEquipmentBlueprint import ReportingEquipmentBlueprint
from api.blueprints.SavedReportConfigurationsBlueprint import SavedReportConfigurationsBlueprint
from db.database_creator import DatabaseCreator
from db.uow import UoW
from flask.ext.assets import Environment, Bundle
from api.blueprints.BronzeReportingBlueprint import BronzeReportingBlueprint
from api.blueprints.NaicsBlueprint import NaicsBlueprint
from api.blueprints.ReportingAccountsBlueprint import ReportingAccountsBlueprint
from api.blueprints.ReportingGroupsBlueprint import ReportingGroupsBlueprint
from api.blueprints.ReportingNaicsBlueprint import ReportingNaicsBlueprint
from api.blueprints.ReportingSicBlueprint import ReportingSicBlueprint
from api.blueprints.ReportingComponentsBlueprint import ReportingComponentsBlueprint
from api.blueprints.ReportingTextBlueprint import ReportingTextBlueprint
from api.blueprints.SicBlueprint import SicBlueprint

import os

import bcrypt
from flask import Flask, jsonify, g, request
from flask.ext.login import LoginManager
from api.blueprints.CategoriesBlueprint import CategoriesBlueprint
from api.blueprints.CommitteesBlueprint import CommitteesBlueprint
from api.blueprints.ContactsBlueprint import ContactsBlueprint
from api.blueprints.ECOBlueprint import EcoBlueprint
from api.blueprints.MeetingsBlueprint import MeetingsBlueprint
from api.blueprints.TasksBlueprint import TasksBlueprint
from api.blueprints.IssuesBlueprint import IssuesBlueprint
from api.blueprints.ProjectsBlueprint import ProjectsBlueprint
from api.models.User import User

from config import DefaultConfig
from api.blueprints.IndexBlueprint import IndexBlueprint
from api.blueprints.GroupsBlueprint import GroupsBlueprint
from api.blueprints.LoginBlueprint import LoginBlueprint
from api.blueprints.UsersBlueprint import UsersBlueprint
from api.blueprints.RolesBlueprint import RolesBlueprint
from api.blueprints.WeatherStationsBlueprint import WeatherStationsBlueprint
from api.blueprints.AccountsBlueprint import AccountsBlueprint
from api.blueprints.MeetingTypesBlueprint import MeetingTypesBlueprint
from api.blueprints.ActionItemPrioritiesBlueprint import ActionItemPrioritiesBlueprint
from api.blueprints.ActionItemStatusesBlueprint import ActionItemStatusesBlueprint
from api.blueprints.ActionItemTypesBlueprint import ActionItemTypesBlueprint
from api.blueprints.ComponentsBlueprint import ComponentsBlueprint
from api.blueprints.UtilityCompaniesBlueprint import UtilityCompaniesBlueprint
from api.blueprints.IssuePrioritiesBlueprint import IssuePrioritiesBlueprint
from api.blueprints.IssueStatusesBlueprint import IssueStatusesBlueprint
from api.blueprints.IssueTypesBlueprint import IssueTypesBlueprint
from api.blueprints.TaskPrioritiesBlueprint import TaskPrioritiesBlueprint
from api.blueprints.TaskStatusesBlueprint import TaskStatusesBlueprint
from api.blueprints.TaskTypesBlueprint import TaskTypesBlueprint
from api.blueprints.EquipmentBlueprint import EquipmentBlueprint
from api.blueprints.UploadsBlueprint import UploadsBlueprint
from api.blueprints.DataDumpBlueprint import DataDumpBlueprint
from api.blueprints.ContractsBlueprint import ContractsBlueprint
from api.blueprints.SyrxCategoriesBlueprint import SyrxCategoriesBlueprint
from api.blueprints.ResetScheduleBlueprint import ResetScheduleBlueprint
from PathianExceptions import PathianException
import rethinkdb
from utils import INSTANCE_FOLDER_PATH


# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    IndexBlueprint,
    LoginBlueprint,
    RolesBlueprint,
    GroupsBlueprint,
    UsersBlueprint,
    WeatherStationsBlueprint,
    AccountsBlueprint,
    ComponentsBlueprint,
    CategoriesBlueprint,
    ContactsBlueprint,
    TasksBlueprint,
    IssuesBlueprint,
    ProjectsBlueprint,
    EcoBlueprint,
    MeetingsBlueprint,
    CommitteesBlueprint,
    MeetingTypesBlueprint,
    UtilityCompaniesBlueprint,
    ActionItemPrioritiesBlueprint,
    ActionItemStatusesBlueprint,
    ActionItemTypesBlueprint,
    IssuePrioritiesBlueprint,
    IssueStatusesBlueprint,
    IssueTypesBlueprint,
    UtilityCompaniesBlueprint,
    TaskPrioritiesBlueprint,
    TaskStatusesBlueprint,
    TaskTypesBlueprint,
    ReportingGroupsBlueprint,
    NaicsBlueprint,
    ReportingAccountsBlueprint,
    ReportingNaicsBlueprint,
    ReportingSicBlueprint,
    ReportingComponentsBlueprint,
    ReportingEquipmentBlueprint,
    ResetScheduleBlueprint,
    SavedReportConfigurationsBlueprint,
    SicBlueprint,
    EquipmentBlueprint,
    ReportingTextBlueprint,
    UploadsBlueprint,
    BronzeReportingBlueprint,
    DataMappingBlueprint,
    DataDumpBlueprint,
    ContractsBlueprint,
    SyrxCategoriesBlueprint
)

session_opts = {
    'session.type': 'ext:memcached',
    'session.url': '127.0.0.1:5000',
    'session.data_dir': './cache',
}


def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name, instance_path=INSTANCE_FOLDER_PATH, instance_relative_config=True, static_url_path='/static',
                static_folder='static')

    app.config['dbname'] = config.DB_NAME
    app.config["dbhost"] = config.DB_HOST
    app.config["dbport"] = config.DB_PORT

    configure_app(app, config)
    configure_bundles(app)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)
    configure_error_handlers(app)
    configure_database(app)
    configure_login_manager(app)

    app.secret_key = r'A88dj\?1f ~!@xjRIYA?,TR'

    @app.before_request
    def before_request():
        if request.path != "/" and request.path[0:8] != "/static/":
            db_conn = rethinkdb.connect(app.config["dbhost"], app.config["dbport"])
            g.uow = UoW(db_conn)

    return app


def configure_app(app, config=None):
    app.config.from_object(DefaultConfig)

    if config:
        app.config.from_object(config)


def get_js_files_in_dir(dirname=""):
    for root, dirs, files in os.walk(dirname):
        for f in files:
            if os.path.splitext(f)[1] == ".js":
                yield os.path.join(root, f)


def configure_bundles(app):
    assets = Environment(app)
    filters = None
    output = None
    if app.config["MINIFY"]:
        filters = "rjsmin"
        output = "app/app.min.js"

    js_file_directory = os.path.join("static", "app")
    js_files = [x for x in get_js_files_in_dir(os.path.join(js_file_directory))]

    # paths in js_files begin with static/, this needs to be stripped
    relative_paths = [os.sep.join(f.split(os.sep)[1:]) for f in js_files]

    # must convert any occurances of the path separator to "/"
    relative_paths = [f.replace(os.sep, "/") for f in relative_paths]

    # remove app/app.js and add it to the front
    relative_paths.remove('app/app.js')
    relative_paths.insert(0, 'app/app.js')

    js_bundle = Bundle(*relative_paths, filters=filters, output=output)
    assets.register("js_bundle", js_bundle)


def configure_extensions(app):
    pass


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    import logging
    from logging.handlers import RotatingFileHandler

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.DEBUG)

    main_log = os.path.join(app.config['LOG_FOLDER'], 'pathian.log')
    log_file = RotatingFileHandler(main_log, maxBytes=100000, backupCount=10)
    log_file.setLevel(logging.DEBUG)
    log_file.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(log_file)


def configure_hook(app):
    pass


def configure_error_handlers(app):
    @app.errorhandler(PathianException)
    def application_exception(error):
        response = jsonify({'Message': error.message})
        response.status_code = error.status_code

        return response

    @app.errorhandler(403)
    def forbidden_page(error):
        return jsonify({'Message': 'You do not have permission to access this resource.'}), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({'Message': 'Resource not found.'}), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return jsonify({'Message': 'Internal Error.'}), 500


def configure_database(app):
    db_conn = rethinkdb.connect(app.config["dbhost"], app.config["dbport"])
    database_creator = DatabaseCreator(db_conn, "pathian")
    database_creator.run()


def configure_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        db_conn = rethinkdb.connect(app.config["dbhost"], app.config["dbport"])
        uow = UoW(db_conn)
        u = uow.users.get_user_by_id(str(userid))
        return User(u)

