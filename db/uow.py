from copy import copy
from api.models.QueryParameters import QueryResult
from repositories.global_vendor_point_record_repository import GlobalVendorPointRecordRepository
from repositories.compiled_point_record_repository import CompiledPointRecordRepository
from repositories.account_repository import AccountRepository
from repositories.action_item_type_repository import ActionItemTypeRepository
from repositories.action_item_status_repository import ActionItemStatusRepository
from repositories.action_item_priority_repository import ActionItemPriorityRepository
from repositories.bronze_reporting_repository import BronzeReportingRepository
from repositories.category_repository import CategoryRepository
from repositories.committee_repository import CommitteeRepository
from repositories.compiled_energy_record_repository import CompiledEnergyRecordRepository
from repositories.component_point_repository import ComponentPointRepository
from repositories.component_repository import ComponentRepository
from repositories.contact_repository import ContactRepository
from repositories.contract_repository import ContractRepository
from repositories.data_mapping_repository import DataMappingRepository
from repositories.eco_repository import EcoRepository
from repositories.energy_record_repository import EnergyRecordRepository
from repositories.equipment_repository import EquipmentRepository
from repositories.group_repository import GroupRepository
from repositories.issue_repository import IssueRepository
from repositories.issue_priority_repository import IssuePriorityRepository
from repositories.issue_status_repository import IssueStatusRepository
from repositories.issue_type_repository import IssueTypeRepository
from repositories.meeting_repository import MeetingRepository
from repositories.meeting_type_repository import MeetingTypeRepository
from repositories.naics_repository import NaicsRepository
from repositories.paragraph_repository import ParagraphRepository
from repositories.price_normalization_repository import PriceNormalizationRepository
from repositories.project_repository import ProjectRepository
from repositories.role_repository import RoleRepository
from repositories.saved_report_configuration_repository import SavedReportConfigurationRepository
from repositories.sic_repository import SicRepository
from repositories.size_normalization_repository import SizeNormalizationRepository
from repositories.task_repository import TaskRepository
from repositories.task_priority_repository import TaskPriorityRepository
from repositories.task_status_repository import TaskStatusRepository
from repositories.task_type_repository import TaskTypeRepository
from repositories.unmapped_syrx_num_repository import UnmappedSyrxNumRepository
from repositories.unmapped_vendor_point_record_repository import UnmappedVendorPointRecordRepository
from repositories.user_repository import UserRepository
from repositories.utility_company_repository import UtilityCompanyRepository
from repositories.vendor_records_repository import VendorRecordsRepository
from repositories.weather_station_repository import WeatherStationRepository
from repositories.syrx_category_repository import SyrxCategoryRepository
from repositories.reset_schedule_repository import ResetScheduleRepository
import rethinkdb
from pdb import set_trace as trace

class TableContainer:
    def __init__(self, db_name):
        db = rethinkdb.db(db_name)

        self.accounts = db.table("accounts")
        self.action_item_priorities = db.table("actionitempriorities")
        self.action_item_statuses = db.table("actionitemstatuses")
        self.action_item_types = db.table("actionitemtypes")
        self.active_notifications = db.table("active_notifications")
        self.bronze_reporting_requests = db.table("bronze_reporting_requests")
        self.categories = db.table("categories")
        self.committees = db.table("committees")
        self.components = db.table("components")
        self.contacts = db.table("contacts")
        self.contracts = db.table("contracts")
        self.compiled_energy_records = db.table("compiled_energy_records")
        self.compiled_equipment_point_records = db.table("compiled_equipment_point_records")
        self.component_issues = db.table("component_issues")
        self.component_points = db.table("component_points")
        self.component_master_point_mappings = db.table("component_master_point_mappings")
        self.component_tasks = db.table("component_tasks")
        self.data_mapping = db.table("data_mapping")
        self.eco = db.table("eco")
        self.energyrecords = db.table("energyrecords")
        self.equipment = db.table("equipment")
        self.equipment_issues = db.table("equipment_issues")
        self.equipment_paragraphs = db.table("equipment_paragraphs")
        self.equipment_points = db.table("equipment_points")
        self.equipment_point_records = db.table("equipment_point_records")
        self.equipment_raf = db.table("equipment_raf")
        self.equipment_reset_schedule = db.table("equipment_reset_schedule")
        self.equipment_tasks = db.table("equipment_tasks")
        self.flat_components = db.table("flat_components")
        self.flat_groups = db.table("flat_groups")
        self.flat_naics_codes = db.table("flat_naics_codes")
        self.flat_sic_codes = db.table("flat_sic_codes")
        self.global_vendor_point_records = db.table("global_vendor_point_records")
        self.groups = db.table("groups")
        self.imported_equipment_point_records = db.table("imported_equipment_point_records")
        self.imported_vendor_records = db.table("imported_vendor_records")
        self.issues = db.table("issues")
        self.issuepriorities = db.table("issuepriorities")
        self.issuestatuses = db.table("issuestatuses")
        self.issuetypes = db.table("issuetypes")
        self.meetings = db.table("meetings")
        self.meetingtypes = db.table("meetingtypes")
        self.naics_codes = db.table("naics_codes")
        self.naics_groups_mapping = db.table("naics_groups_mapping")
        self.noaa_records = db.table("noaarecords")
        self.next_group_num = db.table("next_group_num")
        self.paragraph_definitions = db.table("paragraph_definitions")
        self.pricenormalizations = db.table("pricenormalizations")
        self.projects = db.table("projects")
        self.reset_schedules = db.table("reset_schedules")
        self.roles = db.table("roles")
        self.saved_report_configurations = db.table('saved_report_configurations')
        self.sic_codes = db.table("sic_codes")
        self.sic_groups_mapping = db.table("sic_groups_mapping")
        self.sizenormalizations = db.table("sizenormalizations")
        self.tasks = db.table("tasks")
        self.taskpriorities = db.table("taskpriorities")
        self.taskstatuses = db.table("taskstatuses")
        self.tasktypes = db.table("tasktypes")
        self.unmapped_syrx_nums = db.table("unmapped_syrx_nums")
        self.users = db.table("users")
        self.users_roles = db.table("users_roles")
        self.utilitycompanies = db.table("utilitycompanies")
        self.unknown_vendor_points = db.table("unknown_vendor_points")
        self.unmapped_vendor_point_records = db.table("unmapped_vendor_point_records")
        self.vendor_points = db.table("vendor_points")
        self.vendor_records = db.table("vendor_records")
        self.weatherstations = db.table("weatherstations")
        self.syrx_categories = db.table("syrxcategories")


class UoW:
    def __init__(self, db_conn, db_name="pathian"):
        if not db_conn:
            # leaving this in for when UoW isn't being used in g
            db_conn = rethinkdb.connect("localhost", 28015)
            #db_conn = rethinkdb.connect("104.236.87.217", 28015)
            #db_conn = rethinkdb.connect("104.236.88.105", 28015)

        self.db_conn = db_conn
        self.db_name = db_name

        self.row_obj = rethinkdb.row

        self._accounts = None
        self._action_item_priorities = None
        self._action_item_statuses = None
        self._action_item_types = None
        self._bronze_reporting = None
        self._categories = None
        self._committees = None
        self._compiled_energy_records = None
        self._compiled_point_records = None
        self._component_points = None
        self._components = None
        self._contacts = None
        self._contracts = None
        self._data_mapping = None
        self._eco = None
        self._energy_records = None
        self._equipment = None
        self._global_vendor_point_records = None
        self._groups = None
        self._issues = None
        self._issue_priorities = None
        self._issue_statuses = None
        self._issue_types = None
        self._meetings = None
        self._meeting_types = None
        self._naics = None
        self._paragraphs = None
        self._price_normalizations = None
        self._projects = None
        self._roles = None
        self._saved_report_configurations = None
        self._sic = None
        self._size_normalizations = None
        self._tasks = None
        self._task_priorities = None
        self._task_statuses = None
        self._task_types = None
        self._unmapped_syrx_nums = None
        self._unmapped_vendor_point_records = None
        self._users = None
        self._utility_companies = None
        self._vendor_records = None
        self._weather_stations = None
        self._syrx_categories = None
        self._reset_schedules = None

        self.tables = TableContainer(db_name)

    def run(self, query):
        return query.run(self.db_conn)

    def run_list(self, query):
        c = query.run(self.db_conn)
        return list(c)

    @property
    def accounts(self):
        if not self._accounts:
            self._accounts = AccountRepository(self)
        return self._accounts

    @property
    def action_item_priorities(self):
        if not self._action_item_priorities:
            self._action_item_priorities = ActionItemPriorityRepository(self)
        return self._action_item_priorities

    @property
    def action_item_statuses(self):
        if not self._action_item_statuses:
            self._action_item_statuses = ActionItemStatusRepository(self)
        return self._action_item_statuses

    @property
    def action_item_types(self):
        if not self._action_item_types:
            self._action_item_types = ActionItemTypeRepository(self)
        return self._action_item_types

    @property
    def bronze_reporting(self):
        if not self._bronze_reporting:
            self._bronze_reporting = BronzeReportingRepository(self)
        return self._bronze_reporting

    @property
    def categories(self):
        if not self._categories:
            self._categories = CategoryRepository(self)
        return self._categories

    @property
    def committees(self):
        if not self._committees:
            self._committees = CommitteeRepository(self)
        return self._committees

    @property
    def compiled_energy_records(self):
        if not self._compiled_energy_records:
            self._compiled_energy_records = CompiledEnergyRecordRepository(self)
        return self._compiled_energy_records

    @property
    def compiled_point_records(self):
        if not self._compiled_point_records:
            self._compiled_point_records = CompiledPointRecordRepository(self)
        return self._compiled_point_records

    @property
    def component_points(self):
        if not self._component_points:
            self._component_points = ComponentPointRepository(self)
        return self._component_points

    @property
    def components(self):
        if not self._components:
            self._components = ComponentRepository(self)
        return self._components

    @property
    def contacts(self):
        if not self._contacts:
            self._contacts = ContactRepository(self)
        return self._contacts

    @property
    def contracts(self):
        if not self._contracts:
            self._contracts = ContractRepository(self)
        return self._contracts

    @property
    def data_mapping(self):

        if not self._data_mapping:
            self._data_mapping = DataMappingRepository(self)
        return self._data_mapping

    @property
    def eco(self):
        if not self._eco:
            self._eco = EcoRepository(self)
        return self._eco

    @property
    def energy_records(self):
        if not self._energy_records:
            self._energy_records = EnergyRecordRepository(self)
        return self._energy_records

    @property
    def equipment(self):
        if not self._equipment:
            self._equipment = EquipmentRepository(self)
        return self._equipment

    @property
    def global_vendor_point_records(self):
        if not self._global_vendor_point_records:
            self._global_vendor_point_records = GlobalVendorPointRecordRepository(self)
        return self._global_vendor_point_records

    @property
    def groups(self):
        if not self._groups:
            self._groups = GroupRepository(self)
        return self._groups

    @property
    def issues(self):
        if not self._issues:
            self._issues = IssueRepository(self)
        return self._issues

    @property
    def issue_priorities(self):
        if not self._issue_priorities:
            self._issue_priorities = IssuePriorityRepository(self)
        return self._issue_priorities

    @property
    def issue_statuses(self):
        if not self._issue_statuses:
            self._issue_statuses = IssueStatusRepository(self)
        return self._issue_statuses

    @property
    def issue_types(self):
        if not self._issue_types:
            self._issue_types = IssueTypeRepository(self)
        return self._issue_types

    @property
    def meetings(self):
        if not self._meetings:
            self._meetings = MeetingRepository(self)
        return self._meetings

    @property
    def meeting_types(self):
        if not self._meeting_types:
            self._meeting_types = MeetingTypeRepository(self)
        return self._meeting_types

    @property
    def naics(self):
        if not self._naics:
            self._naics = NaicsRepository(self)
        return self._naics

    @property
    def paragraphs(self):
        if not self._paragraphs:
            self._paragraphs = ParagraphRepository(self)
        return self._paragraphs

    @property
    def price_normalizations(self):
        if not self._price_normalizations:
            self._price_normalizations = PriceNormalizationRepository(self)
        return self._price_normalizations

    @property
    def projects(self):
        if not self._projects:
            self._projects = ProjectRepository(self)
        return self._projects

    @property
    def reset_schedules(self):
        if not self._reset_schedules:
            self._reset_schedules = ResetScheduleRepository(self)
        return self._reset_schedules

    @property
    def roles(self):
        if not self._roles:
            self._roles = RoleRepository(self)
        return self._roles

    @property
    def saved_report_configurations(self):
        if not self._saved_report_configurations:
            self._saved_report_configurations = SavedReportConfigurationRepository(self)
        return self._saved_report_configurations

    @property
    def sic(self):
        if not self._sic:
            self._sic = SicRepository(self)
        return self._sic

    @property
    def size_normalizations(self):
        if not self._size_normalizations:
            self._size_normalizations = SizeNormalizationRepository(self)
        return self._size_normalizations

    @property
    def tasks(self):
        if not self._tasks:
            self._tasks = TaskRepository(self)
        return self._tasks

    @property
    def task_priorities(self):
        if not self._task_priorities:
            self._task_priorities = TaskPriorityRepository(self)
        return self._task_priorities

    @property
    def task_statuses(self):
        if not self._task_statuses:
            self._task_statuses = TaskStatusRepository(self)
        return self._task_statuses

    @property
    def unmapped_syrx_nums(self):
        if not self._unmapped_syrx_nums:
            self._unmapped_syrx_nums = UnmappedSyrxNumRepository(self)
        return self._unmapped_syrx_nums

    @property
    def unmapped_vendor_point_records(self):
        if not self._unmapped_vendor_point_records:
            self._unmapped_vendor_point_records = UnmappedVendorPointRecordRepository(self)
        return self._unmapped_vendor_point_records

    @property
    def users(self):
        if not self._users:
            self._users = UserRepository(self)
        return self._users

    @property
    def task_types(self):
        if not self._task_types:
            self._task_types = TaskTypeRepository(self)
        return self._task_types

    @property
    def utility_companies(self):
        if not self._utility_companies:
            self._utility_companies = UtilityCompanyRepository(self)
        return self._utility_companies

    @property
    def vendor_records(self):
        if not self._vendor_records:
            self._vendor_records = VendorRecordsRepository(self)
        return self._vendor_records

    @property
    def weather_stations(self):
        if not self._weather_stations:
            self._weather_stations = WeatherStationRepository(self)
        return self._weather_stations

    @property
    def syrx_categories(self):
        if not self._syrx_categories:
            self._syrx_categories = SyrxCategoryRepository(self)
        return self._syrx_categories

    def apply_query_parameters(self, query, query_parameters):
        q = query
        q = self.apply_query_parameter_sorts(q, query_parameters)

        cursor = self.run(q.skip(query_parameters.skip).limit(query_parameters.take))
        data = list(cursor)
        total = self.run(query.count())

        query_result = QueryResult(data, total)
        return query_result

    @classmethod
    def apply_query_parameter_sorts(cls, q, query_parameters):
        if len(query_parameters.sort) == 0:
            q = q.order_by("id")
        else:
            for sort in query_parameters.sort:
                if sort["dir"] == "desc":
                    q = q.order_by(rethinkdb.desc(sort["field"]))
                else:
                    q = q.order_by(rethinkdb.asc(sort["field"]))

        return q