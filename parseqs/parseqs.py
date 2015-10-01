import urlparse
import re


def split_param_name(param_name):
    l = re.compile("\]\[|\[|\]").split(param_name)
    if len(l) > 1:
        del l[-1]
    return l


def get_number(s):
    try:
        return int(s)
    except ValueError:
        return False


def convert_list_to_dict(parent, index=None, propName=None):
    v = {}
    if index is not None:
        a = parent[index]
        for i in range(0, len(a)):
            v[i] = a[i]
        parent[index] = v
    else:
        a = parent[propName]
        for i in range(0, len(a)):
            v[i] = a[i]
        parent[propName] = v
    return v


def insert_into_list(list, index, value):
    if index >= len(list):
        for x in range(len(list), index + 1):
            list.append(None)

    list[index] = value


def parse(query_string):
    mydict = {}
    plist = urlparse.parse_qsl(query_string)

    if query_string == "":
        return mydict

    for di in plist:
        (k, v) = di
        key_path = split_param_name(k)

        assignment_location = mydict
        assignment_location_index = None
        assignment_location_propName = None
        parent_assignment_location = None

        for i in range(0, len(key_path)):
            path_segment = key_path[i]

            is_list = isinstance(assignment_location, list)
            is_dict = isinstance(assignment_location, dict)

            if is_list:
                array_index = get_number(path_segment)
                # array_index will be false if path_segment is not a number
                # we then need to convert assignment_location to a dictionary
                if array_index is False:
                    # it is not enough to pass assignment_location to a method, because that will just change the object
                    # that is pointed to by the variable. instead, we pass parent_assignment_location to a method and include
                    # assignment_location_index/assignment_location_propName to set the correct property on the parent object
                    assignment_location = convert_list_to_dict(parent_assignment_location,
                                                               index=assignment_location_index,
                                                               propName=assignment_location_propName)
                    is_dict = True
                else:
                    if i == len(key_path) - 1:
                        # if we're on the last path segment, then save the value of the key/value pair instead of creating
                        # new lists/dictionaries
                        if array_index >= len(assignment_location):
                            insert_into_list(assignment_location, array_index, v)
                        else:
                            assignment_location[array_index] = v
                        break

                    assignment_location_index = array_index
                    assignment_location_propName = None
                    parent_assignment_location = assignment_location

                    if array_index >= len(assignment_location):
                        insert_into_list(assignment_location, array_index, [])
                    assignment_location = assignment_location[array_index]
                    continue
            if is_dict:
                # if we're on the last path segment, then save the value of the key/value pair instead of creating
                # new lists/dictionaries
                if i == len(key_path) - 1:
                    assignment_location[path_segment] = v
                    break
                assignment_location_index = None
                assignment_location_propName = path_segment
                parent_assignment_location = assignment_location

                if path_segment not in assignment_location:
                    assignment_location[path_segment] = []
                assignment_location = assignment_location[path_segment]

    return mydict