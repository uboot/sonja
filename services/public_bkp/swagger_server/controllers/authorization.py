from sonja import database
from flask_login import current_user
from flask import abort
from functools import wraps


def require(permission: database.PermissionLabel):
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if permission not in current_permissions():
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return inner


def current_permissions() -> database.PermissionLabel:
    with database.session_scope() as session:
        record = session.query(database.User).filter_by(id=current_user.id).first()
        if not record:
            abort(401)
        return [p.label for p in record.permissions]


