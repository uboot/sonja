from aioredis import Channel, Redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi_plugins import depends_redis
from sse_starlette.sse import EventSourceResponse
from public.auth import get_read
from public.crud.run import read_run, read_runs
from public.schemas.run import RunReadItem, RunReadList
from sonja.database import get_session, Session, session_scope
from sonja.config import logger

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


@router.get("/event/build/{build_id}/run", response_model=RunReadItem, response_model_by_alias=False)
async def get_run_events(build_id: str, redis: Redis = Depends(depends_redis)):
    return EventSourceResponse(subscribe(f"build:{build_id}:run", redis))


async def subscribe(channel: str, redis: Redis):
    (channel_subscription,) = await redis.subscribe(channel=Channel(channel, False))
    while await channel_subscription.wait_message():
        message = await channel_subscription.get_json()
        item_json = None
        with session_scope() as session:
            item_id = str(message["id"])
            item = read_run(session, item_id)
            if item:
                item_json = RunReadItem.from_db(item).json()

        if item_json:
            logger.debug("Send run event '%s' received on '%s'", item_json, channel)
            yield { "event": "update", "data": item_json }
        else:
            logger.warning("Could not read updated run '%s'", item_id)
