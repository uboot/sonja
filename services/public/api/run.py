from fastapi import APIRouter, Depends, HTTPException
from public.auth import get_read
from public.crud.run import read_run, read_runs
from public.schemas.run import RunReadItem, RunReadList
from sonja.database import get_session, Session

router = APIRouter()


@router.get("/build/{build_id}/run", response_model=RunReadList, response_model_by_alias=False)
def get_run_list(build_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    return RunReadList.from_db(read_runs(session, build_id))


@router.get("/run/{run_id}", response_model=RunReadItem, response_model_by_alias=False)
def get_run_item(run_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    run = read_run(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunReadItem.from_db(run)
