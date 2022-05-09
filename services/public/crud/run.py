from sonja.model import Run
from sonja.database import Session
from typing import List


def read_runs(session: Session, build_id: str) -> List[Run]:
    return session.query(Run).filter(Run.build_id == build_id).all()


def read_run(session: Session, run_id: str) -> Run:
    return session.query(Run).filter(Run.id == run_id).first()
