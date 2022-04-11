from aioredis import Channel, Redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi_plugins import depends_redis
from sse_starlette.sse import EventSourceResponse
from public.auth import get_read, get_write
from public.schemas.build import BuildReadItem, BuildReadList, BuildWriteItem, StatusEnum, BuildUpdateItem
from public.crud.build import read_builds, read_build, update_build
from sonja.database import get_session, Session, session_scope
from sonja.client import LinuxAgent, WindowsAgent
from sonja.config import logger

router = APIRouter()
linux_agent = LinuxAgent()
windows_agent = WindowsAgent()


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
async def patch_build_item(build_id: str, build_item: BuildWriteItem, session: Session = Depends(get_session),
                  redis: Redis = Depends(depends_redis), authorized: bool = Depends(get_write)):
    build = read_build(session, build_id)
    if build is None:
        raise HTTPException(status_code=404, detail="Build not found")
    patched_build = await update_build(session, redis, build, build_item)

    if build_item.data.attributes.status == StatusEnum.new:
        logger.info('Trigger linux agent: process builds')
        if not linux_agent.process_builds():
            logger.error("Failed to trigger Linux agent")

        logger.info('Trigger windows agent: process builds')
        if not windows_agent.process_builds():
            logger.error("Failed to trigger Windows agent")

    return BuildReadItem.from_db(patched_build)


@router.get("/event/ecosystem/{ecosystem_id}/build", response_model=BuildUpdateItem, response_model_by_alias=False)
async def get(ecosystem_id: str, redis: Redis = Depends(depends_redis)):
    return EventSourceResponse(subscribe(f"ecosystem:{ecosystem_id}:build", redis))


async def subscribe(channel: str, redis: Redis):
    (channel_subscription,) = await redis.subscribe(channel=Channel(channel, False))
    while await channel_subscription.wait_message():
        message = await channel_subscription.get_json()
        with session_scope() as session:
            build_id = str(message["id"])
            build = read_build(session, build_id)
            if build:
                logger.debug("Send build event '%s' received on '%s'", BuildUpdateItem.from_db(build).json(), channel)
                yield { "event": "update", "data": BuildUpdateItem.from_db(build).json() }
            else:
                logger.warning("Could not read updated build '%s'", build_id)
