from fastapi import APIRouter, Depends, HTTPException
from public.auth import get_read, get_write
from public.schemas.build import BuildReadItem, BuildReadList, BuildWriteItem, StatusEnum
from public.crud.build import read_builds, read_build, update_build
from sonja.database import get_session, Session
from sonja.client import LinuxAgent, WindowsAgent
from sonja.config import logger
from typing import Optional

router = APIRouter()
linux_agent = LinuxAgent()
windows_agent = WindowsAgent()


@router.get("/build", response_model=BuildReadList, response_model_by_alias=False)
def get_build_list(ecosystem_id: str, repo_id: Optional[str] = None, channel_id: Optional[str] = None,
                   profile_id: Optional[str] = None, page: Optional[int] = None, per_page: Optional[int] = None,
                   session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    return BuildReadList.from_db(**read_builds(session, ecosystem_id, repo_id, channel_id, profile_id, page, per_page))


@router.get("/build/{build_id}", response_model=BuildReadItem, response_model_by_alias=False)
def get_build_item(build_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    build = read_build(session, build_id)
    if build is None:
        raise HTTPException(status_code=404, detail="Build not found")
    return BuildReadItem.from_db(build)


@router.patch("/build/{build_id}", response_model=BuildReadItem, response_model_by_alias=False)
def patch_build_item(build_id: str, build_item: BuildWriteItem, session: Session = Depends(get_session),
                           authorized: bool = Depends(get_write)):
    patched_build = update_build(session, build_id, build_item)
    if patched_build is None:
        raise HTTPException(status_code=404, detail="Build not found")

    if build_item.data.attributes.status == StatusEnum.new:
        logger.info('Trigger linux agent: process builds')
        if not linux_agent.process_builds():
            logger.error("Failed to trigger Linux agent")

        logger.info('Trigger windows agent: process builds')
        if not windows_agent.process_builds():
            logger.error("Failed to trigger Windows agent")

    return BuildReadItem.from_db(patched_build)
