from config import ProdServerConfig, BaseConfig
from db.uow import UoW
import rethinkdb

__author__ = 'Brian'


def update_equipment_points(config):
    """
    Adds a description to each equipment point based on the component id of the equipment point
    :param config: configuration
    :return: None
    """
    db_conn = rethinkdb.connect(config.DB_HOST, config.DB_PORT)
    uow = UoW(db_conn)
    equipment_point_list = uow.equipment.get_all_equipment_points()
    for equipment_point in equipment_point_list:
        # check to see if it already has a description
        if 'point_description' in equipment_point:
            continue

        # get the component point description
        component_point_description = uow.component_points.get_by_component_point_id(equipment_point['component_point_id'])['description']
        equipment_point['point_description'] = component_point_description
        uow.equipment.update_equipment_point(equipment_point)


if __name__ == "__main__":
    update_equipment_points(ProdServerConfig)