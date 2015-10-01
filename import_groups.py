import uuid
import pyodbc
from db.uow import UoW


def import_groups():
    uow = UoW(None)
    conn = pyodbc.connect("DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=PathianDBNet;integrated security=True")

    cursor = conn.cursor()

    cursor.execute("SELECT Id FROM Groups")

    id_dict = dict()

    for row in cursor:
        id_dict[row.Id] = uuid.uuid4()

    query = """
    select * from (
        select g.id, g.name, g.naicscodecode, child_groups.childid, null parentid, g.IsEquipmentGroup, g.SicCodeCode
        from Groups g
        inner join GroupGroups child_groups on child_groups.parentid = g.id
        inner join Groups child_group on child_group.id = child_groups.childid
        where child_group.IsEquipmentGroup = 0

        union

        select g.id, g.name, g.naicscodecode, null childid, parent_groups.parentid, g.IsEquipmentGroup, g.SicCodeCode
        from Groups g
        inner join GroupGroups parent_groups on parent_groups.childid = g.id
        inner join Groups parent_group on parent_group.id = parent_groups.parentid
        where parent_group.IsEquipmentGroup = 0
    ) q where q.IsEquipmentGroup = 0
    order by id
    """
    cursor.execute(query)

    max_group_num = 0
    num_inserted = 0
    buffer_list = []
    current_group = None
    for row in cursor:

        if current_group is not None and current_group["old_id"] != row.id:
            buffer_list.append(current_group)
            current_group = None
            if len(buffer_list) == 200:
                uow.groups.insert_many(buffer_list)
                num_inserted += 200
                buffer_list = []
                print(num_inserted)
        if current_group is None:
            current_group = dict(id=str(id_dict[row.id]),
                                 num=str(row.id),
                                 name=row.name,
                                 lower_name=row.name.lower(),
                                 naics_code=row.naicscodecode,
                                 sic_code=row.SicCodeCode,
                                 old_id=row.id,
                                 isRoot=True,
                                 childIds=[],
                                 parentIds=[])
            max_group_num = max(max_group_num, row.id)

        if row.childid is not None:
            current_group["childIds"].append(str(id_dict[row.childid]))
        if row.parentid is not None:
            current_group["isRoot"] = False
            current_group["parentIds"].append(str(id_dict[row.parentid]))

    if current_group is not None and current_group["old_id"] != row.id:
        buffer_list.append(current_group)

    if len(buffer_list) > 0:
        uow.groups.insert_many(buffer_list)
        num_inserted += len(buffer_list)
        print(num_inserted)

    uow.groups.update_next_group_num(max_group_num + 1)

if __name__ == "__main__":
    import_groups()