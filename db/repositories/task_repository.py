from api.models.QueryParameters import QueryResult
from api.models.Task import Task


class TaskRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.tasks
        self.task_priorities = uow.tables.taskpriorities
        self.task_types = uow.tables.tasktypes
        self.task_status = uow.tables.taskstatuses

    def get_all(self, query_parameters):
        if query_parameters is None:
            tasks = self.uow.run_list(self.table.order_by('name'))
            return tasks

        return self.uow.apply_query_parameters(
            self.table
            .eq_join('priority_id', self.task_priorities)
            .map(lambda task: task.merge({"right": {"priority": task["right"]["name"]}}))
            .without({'right': ['name', 'id']})
            .zip()
            .eq_join('type_id', self.task_types)
            .map(lambda task: task.merge({"right": {"task_type":task["right"]["name"]}}))
            .without({'right': ['name', 'id']})
            .zip()
            .eq_join('status_id', self.task_status)
            .map(lambda task: task.merge({"right": {"status": task["right"]["name"]}}))
            .without({'right': ['name', 'id']})
            .zip(), query_parameters)

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        self.uow.run(self.table.insert(model.__dict__))

    def update(self, model):
        self.uow.run(self.table.update(model.__dict__))

    def get(self, id):
        model_raw = self.uow.run(self.table.get(id))
        model = Task(model_raw)
        return model

    def delete(self, id):
        self.uow.run(self.table.get(id).delete())

    def get_component_tasks(self, component_id, query_parameters):
        component_tasks = self.uow.run_list(self.uow.tables.component_tasks
                                            .get_all(component_id, index="component_id"))

        task_ids = [i['task_id'] for i in component_tasks]

        if task_ids is None or len(task_ids) == 0:
            return {}

        tasks = self.uow.apply_query_parameters(self.table.get_all(*task_ids), query_parameters).to_dict()

        return tasks

    def insert_component_task(self, component_id, task_id):
        self.uow.run(self.uow.tables.component_tasks.insert({"component_id": component_id, "task_id": task_id}))

    def delete_component_task(self, component_id, task_id):
        self.uow.run(self.uow.tables.component_tasks
                     .filter(lambda component_task: component_task["component_id"] == component_id and
                                                    component_task["task_id"] == task_id)
                     .delete())

    def get_tasks_not_mapped_to_component(self, component_id):
        component_tasks = self.uow.run_list(self.uow.tables.component_tasks
                                            .get_all(component_id, index="component_id"))

        if component_tasks is None or len(component_tasks) == 0:
            tasks = self.uow.run_list(self.table.order_by("name"))
        else:
            component_tasks_list = list(component_tasks)
            mapped_task_ids = [t['task_id'] for t in component_tasks_list]

            task_ids_list = self.uow.run_list(self.table.pluck("id"))
            task_ids = [task['id'] for task in task_ids_list]

            task_ids_to_fetch = list(set(task_ids) - set(mapped_task_ids))

            if len(task_ids_to_fetch) is 0:
                return []

            tasks = self.uow.run_list(self.table.get_all(*task_ids_to_fetch).order_by("name"))

        if tasks is None or len(tasks) == 0:
            return []

        return tasks

    def get_group_tasks(self, group_id, query_params):
        if query_params is None:
            tasks = self.uow.run_list(self.table.get_all(group_id, index="group_id"))
            return tasks
        # get the group name to prevent slow queries
        group_name = self.uow.run(self.uow.tables.groups.get(group_id))

        if 'name' not in group_name:
            return QueryResult([], 0)

        group_name = group_name['name']
        # manually merge the tables in the next query to avoid name conflicts and overwriting
        return self.uow.apply_query_parameters(
            self.table.get_all(group_id, index="group_id")
            .eq_join('assigned_to_id', self.uow.tables.contacts)
            .map(lambda row: {'id': row['left']['id'], 'name': row['left']['name'],
                              'full_name': row['right']['full_name'], 'description': row['left']['description'],
                              'equipment_id': row['left']['equipment_id'], 'group': group_name}), query_params)