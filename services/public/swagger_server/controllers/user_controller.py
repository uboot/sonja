import connexion
import sqlalchemy.exc

from sonja import database
from sonja.ssh import hash_password, test_password
from flask import abort
from flask_login import current_user
from swagger_server import models
from swagger_server.controllers.authorization import current_permissions, require

permission_label_table = {
    "read": database.PermissionLabel.read,
    "write": database.PermissionLabel.write,
    "admin": database.PermissionLabel.admin
}


def __create_user(record: database.User):
    return models.User(
        id=str(record.id),
        type="users",
        attributes=models.UserAttributes(
            user_name=record.user_name,
            last_name=record.last_name,
            first_name=record.first_name,
            email=record.email,
            permissions=[models.UserAttributesPermissions(p.label.name) for p in record.permissions]
        )
    )


@require(database.PermissionLabel.admin)
def add_user(body=None):
    if connexion.request.is_json:
        body = models.UserData.from_dict(connexion.request.get_json())  # noqa: E501

    if not body.data.attributes.user_name:
        abort(400)

    record = database.User()
    record.user_name = body.data.attributes.user_name
    record.last_name = body.data.attributes.last_name
    record.first_name = body.data.attributes.first_name
    record.email = body.data.attributes.email
    if body.data.attributes.password:
        record.password = hash_password(body.data.attributes.password)
    record.permissions.clear()
    if body.data.attributes.permissions:
        for p in body.data.attributes.permissions:
            permission = database.Permission()
            permission.label = permission_label_table[p.permission]
            record.permissions.append(permission)
    try:
        with database.session_scope() as session:
            session.add(record)
            session.commit()
            return models.UserData(data=__create_user(record)), 201
    except sqlalchemy.exc.IntegrityError as e:
        if e.orig.args[0] == database.ErrorCodes.DUPLICATE_ENTRY:
            abort(409)
        abort(400)


@require(database.PermissionLabel.admin)
def delete_user(user_id):
    with database.session_scope() as session:
        try:
            database.remove_but_last_user(user_id)
        except database.OperationFailed:
            abort(400)
        except database.NotFound:
            abort(404)
    return None


def get_user(user_id):
    user_is_admin = database.PermissionLabel.admin in current_permissions()

    # only admins can get other users
    if user_id != current_user.id and not user_is_admin:
        abort(403)

    with database.session_scope() as session:
        record = session.query(database.User).filter_by(id=user_id).first()
        if not record:
            abort(404)
        return models.UserData(data=__create_user(record))


@require(database.PermissionLabel.admin)
def get_users():
    with database.session_scope() as session:
        return models.UserList(
            data=[__create_user(record) for record in session.query(database.User).all()]
        )


def update_user(user_id, body=None):
    if connexion.request.is_json:
        body = models.UserData.from_dict(connexion.request.get_json())  # noqa: E501

    try:
        user_is_admin = database.PermissionLabel.admin in current_permissions()
        with database.session_scope() as session:
            record = session.query(database.User).filter_by(id=user_id).first()
            if not record:
                abort(404)

            # only admins can change other users
            if user_id != current_user.id and not user_is_admin:
                abort(403)

            # the password of the current user can only be changed if the old password is provided
            if body.data.attributes.password and user_id == current_user.id:
                if not body.data.attributes.old_password:
                    abort(403)
                if not test_password(body.data.attributes.old_password, record.password):
                    abort(403)

            if body.data.attributes.password:
                record.password = hash_password(body.data.attributes.password)

            record.user_name = body.data.attributes.user_name
            record.last_name = body.data.attributes.last_name
            record.first_name = body.data.attributes.first_name
            record.email = body.data.attributes.email

            # a user can not change her permissions
            if user_id != current_user.id:
                record.permissions.clear()
                if body.data.attributes.permissions:
                    for p in body.data.attributes.permissions:
                        permission = database.Permission()
                        permission.label = permission_label_table[p.permission]
                        record.permissions.append(permission)

            return models.EcosystemData(data=__create_user(record))

    except sqlalchemy.exc.IntegrityError as e:
        if e.orig.args[0] == database.ErrorCodes.DUPLICATE_ENTRY:
            abort(409)
        abort(400)

