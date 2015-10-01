from flask import request, session, abort, g
from api.models.PermissionCache import PermissionCache
from parseqs import parseqs
from functools import wraps


def from_query_string(arg_name, c, prop_name = None):
    def decorator(f):
        @wraps(f)
        def call(**kwargs):
            query_string_object = parseqs.parse(request.query_string)
            if prop_name is None:
                c_instance = c(query_string_object)
            else:
                if prop_name in query_string_object:
                    c_instance = c(query_string_object[prop_name])
                else:
                    c_instance = None
            kwargs[arg_name] = c_instance
            return f(**kwargs)
        return call
    return decorator


def from_request_body(arg_name, c, prop_name = None):
    def decorator(f):
        @wraps(f)
        def call(**kwargs):
            request_object = request.get_json()
            if prop_name is None:
                c_instance = c(request_object)
            else:
                if prop_name in request_object:
                    c_instance = c(request_object[prop_name])
                else:
                    c_instance = None
            kwargs[arg_name] = c_instance
            return f(**kwargs)
        return call
    return decorator

def from_request_body_key_value(arg_name, c, prop_name=None):
    def decorator(f):
        @wraps(f)
        def call(**kwargs):
            query_string_object = parseqs.parse(request.get_data())
            if prop_name is None:
                c_instance = c(query_string_object)
            else:
                if prop_name in query_string_object:
                    c_instance = c(query_string_object[prop_name])
                else:
                    c_instance = None
            kwargs[arg_name] = c_instance
            return f(**kwargs)
        return call
    return decorator

def require_permissions(permissions):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            current_user = session['current_user']
            if not PermissionCache.user_has_permissions(current_user['id'], permissions, g.uow):
                abort(403)
                return
            return f(*args, **kwargs)
        return wrapped
    return wrapper


def require_any_permission(permissions):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            current_user = session['current_user']
            if not PermissionCache.user_has_any_permission(current_user['id'], permissions, g.uow):
                abort(403)
                return
            return f(*args, **kwargs)
        return wrapped
    return wrapper