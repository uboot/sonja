import connexion

from sonja import database
from flask import abort
from swagger_server import models
from swagger_server.controllers.authorization import require


def __create_log(record: database.Log):
    return models.Log(
        id=str(record.id),
        type="logs",
        attributes=models.LogAttributes(
            logs=record.logs
        )
    )


@require(database.PermissionLabel.read)
def get_log(log_id):
    with database.session_scope() as session:
        record = session.query(database.Log).filter_by(id=log_id).first()
        if not record:
            abort(404)
        return models.LogData(data=__create_log(record))
