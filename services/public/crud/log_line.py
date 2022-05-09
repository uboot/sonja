from sonja.database import Session
from sonja.model import LogLine, Run
from typing import Optional


def read_log_lines(session: Session, run_id: str, page: Optional[int] = None, per_page:  Optional[int] = None)\
        -> dict:
    if page is not None and per_page is not None:
        objs = session.query(LogLine).\
            join(Run).\
            filter(Run.id == run_id).\
            order_by(LogLine.number, LogLine.id)\
            .limit(per_page)\
            .offset(per_page * (page - 1))
        count = session.query(LogLine).\
            join(Run).\
            filter(Run.id == run_id).\
            count()

        total_pages = count // per_page
        if count % per_page:
            total_pages += 1

        return {
            "objs": objs,
            "total_pages": total_pages
        }
    else:
        return {
            "objs": session.query(LogLine).
                join(Run).
                filter(Run.id == run_id).
                order_by(LogLine.number, LogLine.id)
                .all()
        }
