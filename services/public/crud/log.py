from sonja.database import Log, Session


def read_log(session: Session, log_id: str) -> Log:
    return session.query(Log).filter(Log.id == log_id).first()
