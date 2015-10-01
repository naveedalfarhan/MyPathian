from api.models.QueryParameters import QueryResult
from constants.component_types import *


class ParagraphRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.paragraph_definitions

    def apply_query_parameters_by_component_id(self, component_id, paragraph_type, query_parameters):
        q = self.table.get_all(component_id, index="component_id")
        if paragraph_type:
            q = q.filter({"type": paragraph_type})
        q = q.order_by("num")
        cursor = q.skip(query_parameters.skip).limit(query_parameters.take)

        data = self.uow.run_list(cursor)
        total = self.uow.run(q.count())
        query_result = QueryResult(data, total)
        return query_result

    def get_paragraphs_for_component_id(self, component_id, paragraph_type=None):
        if paragraph_type is None:
            q = self.table.get_all(component_id, index="component_id")
        else:
            q = self.table.get_all([component_id, paragraph_type], index="component_id_paragraph_type")
        q = q.order_by("num")

        data = self.uow.run_list(q)
        return data

    def insert(self, paragraph):
        try:
            del paragraph.id
        except AttributeError:
            pass

        component_id = paragraph.component_id
        component_type = paragraph.type
        component = self.uow.run(self.uow.tables.components.get(component_id))

        if component_type not in valid_point_types and component_type not in valid_paragraph_types:
            raise Exception('Invalid component type')

        num = component["num"].replace(" ", "") + "-" + component_type

        next_num_field_name = "next_" + component_type

        if next_num_field_name not in component:
            num += "-1"
            component[next_num_field_name] = "2"
        else:
            num += "-" + component[next_num_field_name]
            component[next_num_field_name] = str(int(component[next_num_field_name]) + 1)
        self.uow.run(self.uow.tables.components.update(component))

        component_num = num

        paragraph.num = component_num

        self.uow.run(self.table.insert(paragraph.__dict__))

    def exists(self, paragraph_id):
        cs = self.uow.run(self.table.get(paragraph_id))
        return cs is not None

    def update(self, paragraph):
        self.uow.run(self.table.update(paragraph.__dict__))

    def get(self, paragraph_id):
        sequence = self.uow.run(self.table.get(paragraph_id))
        if not sequence:
            sequence = {}
        return sequence

    def delete(self, paragraph_id):
        self.uow.run(self.table.get(paragraph_id).delete())

    def get_all(self):
        return self.uow.run_list(self.table)

    def insert_bulk(self, paragraphs):
        self.uow.run(self.table.insert(paragraphs))

    def get_paragraphs_by_type_and_category(self, component_ids, paragraph_type, category_id):
        return self.uow.run_list(self.table.get_all(*component_ids, index="component_id").filter({"type": paragraph_type, "category_id": category_id}))