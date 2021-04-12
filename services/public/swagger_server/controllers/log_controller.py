import connexion

from conanci import database
from flask import abort
from swagger_server import models


def __create_log(record: database.Log):
    return models.Log(
        id=record.id,
        type="logs",
        attributes=models.LogAttributes(
            logs=record.logs
        )
    )


def get_log(log_id):
    with database.session_scope() as session:
        record = session.query(database.Log).filter_by(id=log_id).first()
        if not record:
            abort(404)
        return models.LogData(data=__create_log(record))
