from api.models.Issue import Issue
from api.models.QueryParameters import QueryResult

import rethinkdb as r

class IssueRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.issues

    def get_all(self, query_parameters):
        if query_parameters is None:
            issues = self.uow.run(self.table.order_by("name"))
            if issues is None:
                issues = []
            return list(issues)
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        self.uow.run(self.table.insert(model.__dict__))

    def get(self, id):
        issue_raw = self.uow.run(self.table.get(id))
        issue = Issue(issue_raw)
        return issue

    def delete(self, id):
        self.uow.run(self.table.get(id).delete())

    def update(self, model):
        self.uow.run(self.table.update(model.__dict__))

    def get_component_issues(self, component_id, query_parameters):
        component_issues = self.uow.run_list(self.uow.tables.component_issues
                                             .get_all(component_id, index="component_id"))
        if component_issues is None or len(component_issues) == 0:
            return {}

        component_issues_list = list(component_issues)

        issue_ids = [i['issue_id'] for i in component_issues_list]

        if issue_ids is None or len(issue_ids) == 0:
            return {}

        issues = self.uow.apply_query_parameters(self.table.get_all(*issue_ids), query_parameters).to_dict()

        return issues

    def insert_component_issue(self, component_id, issue_id):
        self.uow.run(self.uow.tables.component_issues.insert({"component_id": component_id, "issue_id": issue_id}))

    def delete_component_issue(self, component_id, issue_id):
        self.uow.run(self.uow.tables.component_issues
                     .filter(lambda component_issue: component_issue["component_id"] == component_id and
                                                     component_issue["issue_id"] == issue_id).delete())

    def get_issues_not_mapped_to_component(self, component_id):
        component_issues = self.uow.run_list(self.uow.tables.component_issues
                                             .get_all(component_id, index="component_id"))

        if component_issues is None or len(component_issues) == 0:
            issues = self.uow.run_list(self.table.order_by("name"))
        else:
            mapped_issue_ids = [i['issue_id'] for i in component_issues]

            issue_ids_list = self.uow.run_list(self.table.pluck("id"))
            issue_ids = [issue['id'] for issue in issue_ids_list]

            issue_ids_to_fetch = list(set(issue_ids) - set(mapped_issue_ids))

            if len(issue_ids_to_fetch) is 0:
                return []

            issues = self.uow.run_list(self.table.get_all(*issue_ids_to_fetch).order_by("name"))

        return issues

    def get_issues_for_group(self, group_id, query_params):
        if query_params is None:
            issues = self.uow.run_list(self.table.get_all(group_id, index="group_id"))
            return issues

        # get the group name to prevent slow queries
        group_name = self.uow.run(self.uow.tables.groups.get(group_id))

        if 'name' not in group_name:
            return QueryResult([], 0)

        group_name = group_name['name']

        # manually map all columns to prevent name conflicts and overwriting
        return self.uow.apply_query_parameters(
            self.table.get_all(group_id, index='group_id')
            .filter(r.row.has_fields('equipment_id'))
            .eq_join('equipment_id', self.uow.tables.equipment)
            .map(lambda x: {'id': x['left']['id'],
                            'group': group_name,
                            'equipment': x['right']['name'],
                            'name': x['left']['name'],
                            'description': x['left']['description']})
            .union(self.table.get_all(group_id, index='group_id')
                   .filter(r.not_(r.row.has_fields('equipment_id')))
                   .map(lambda x: {'id': x['id'],
                                   'group': group_name,
                                   'equipment': 'No Equip.',
                                   'name': x['name'],
                                   'description': x['description']})),
            query_params)