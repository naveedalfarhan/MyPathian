import logging
import os
from db.uow import UoW
from utils import get_sys_root_path

__author__ = 'badams'


"""
10/22/2014 - Problem with the components. Some components' structure parent does not have it in the list of
children. This script fixes the referential integrity issues among the components
"""


def set_up_logger():
    logger = logging.getLogger('component_fix')
    hdlr = logging.FileHandler(os.path.join(get_sys_root_path(), 'pathian-logs', 'component_fix.log'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger


def update_parent(uow, component, parent_null_list):
    # get the parent
    parent_component = uow.components.get_by_id(component['structure_parent_id'])

    # check if the parent exists
    if not parent_component.id:
        parent_null_list.append(component['id'])
        return

    if not component['id'] in parent_component.structure_child_ids:
        parent_component.structure_child_ids.append(component['id'])

        # update the parent
        uow.components.update(parent_component)


def run():
    # set up the uow
    uow = UoW(None)

    # set up logging
    logger = set_up_logger()

    parent_null_list = []

    # get the components
    components = uow.components.get_all_as_cursor()

    for component in components:
        # make sure it's not a root
        if not component['structure_parent_id']:
            continue

        update_parent(uow, component, parent_null_list)

    # log all of the parent_null list
    null_parent_string = "These components' parents do not exist:\n"
    for null_item in parent_null_list:
        null_parent_string += null_item + '\n'

    logger.info(null_parent_string)

if __name__ == "__main__":
    run()