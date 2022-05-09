from fastapi import APIRouter, Depends
from public.auth import get_read
from public.schemas.log_line import LogLineReadList
from public.crud.log_line import read_log_lines
from sonja.database import get_session, Session
from typing import Optional


router = APIRouter()


@router.get("/log_line", response_model=LogLineReadList, response_model_by_alias=False)
def get_log_line_list(run_id: str, page: Optional[int] = None, per_page:  Optional[int] = None,
                      session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    return LogLineReadList.from_db(**read_log_lines(session, run_id, page, per_page))
