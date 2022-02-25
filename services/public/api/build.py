from fastapi import APIRouter, Depends, HTTPException, status
from public.auth import get_read, get_write
from public.schemas.build import BuildReadItem, BuildReadList, BuildWriteItem
from public.crud.build import read_builds, read_build, update_build
from sonja.database import get_session, Session

router = APIRouter()


@router.get("/ecosystem/{ecosystem_id}/build", response_model=BuildReadList, response_model_by_alias=False)
def get_build_list(ecosystem_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    return BuildReadList.from_db(read_builds(session, ecosystem_id))


@router.get("/build/{build_id}", response_model=BuildReadItem, response_model_by_alias=False)
def get_build_item(build_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    build = read_build(session, build_id)
    if build is None:
        raise HTTPException(status_code=404, detail="Build not found")
    return BuildReadItem.from_db(build)


@router.patch("/build/{build_id}", response_model=BuildReadItem, response_model_by_alias=False)
def patch_build_item(build_id: str, build_item: BuildWriteItem, session: Session = Depends(get_session),
                  authorized: bool = Depends(get_write)):
    build = read_build(session, build_id)
    if build is None:
        raise HTTPException(status_code=404, detail="Build not found")
    patched_build = update_build(session, build, build_item)
    t = BuildReadItem.from_db(patched_build)
    return t
