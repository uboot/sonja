from fastapi import APIRouter, Depends, HTTPException
from public.auth import get_read
from public.schemas.log import LogReadItem
from public.crud.log import read_log
from sonja.database import get_session, Session

router = APIRouter()


@router.get("/log/{log_id}", response_model=LogReadItem, response_model_by_alias=False)
def get_log_item(log_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    log = read_log(session, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return LogReadItem.from_db(log)
