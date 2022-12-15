from datetime import timedelta
from aioredis import Channel, Redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi_plugins import depends_redis
from sse_starlette.sse import EventSourceResponse
from fastapi.security import OAuth2PasswordRequestForm
from public.auth import get_admin, get_write
from public.schemas.build import BuildReadItem
from public.crud.build import read_build
from public.schemas.run import RunReadItem
from public.crud.run import read_run
from public.client import get_crawler, get_redis_client
from sonja.database import get_session, Session, User, clear_ecosystems, session_scope
from sonja.demo import populate_database, add_build, add_log_line, add_run
from sonja.auth import test_password, create_access_token
from sonja.config import logger
from sonja.client import Crawler
from sonja.redis import RedisClient
from typing import Union

router = APIRouter()


@router.get("/ping")
def get_ping():
    pass


@router.get("/clear_ecosystems", dependencies=[Depends(get_admin)])
def get_clear_ecosystems():
    clear_ecosystems()


@router.get("/populate_database", dependencies=[Depends(get_admin)])
def get_populate_database():
    populate_database()


@router.get("/add_build", dependencies=[Depends(get_admin)])
def get_add_build(redis_client: RedisClient = Depends(get_redis_client)):
    add_build(redis_client)


@router.get("/add_run", dependencies=[Depends(get_admin)])
def get_add_run(redis_client: RedisClient = Depends(get_redis_client)):
    add_run(redis_client)


@router.get("/add_log_line", dependencies=[Depends(get_admin)])
def get_add_log_line(redis_client: RedisClient = Depends(get_redis_client)):
    add_log_line(redis_client)


@router.get("/process_repo/{repo_id}", dependencies=[Depends(get_write)])
def get_process_repo(repo_id: str, crawler: Crawler = Depends(get_crawler)):
    if not crawler.process_repo(repo_id):
        raise HTTPException(status_code=400, detail="Failed")


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    record = session.query(User).filter_by(user_name=form_data.username).first()
    if not record or not record.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not test_password(form_data.password, record.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=240)
    access_token = create_access_token(str(record.id), expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/event/general", response_model=Union[BuildReadItem, RunReadItem], response_model_by_alias=False)
async def get_general_events(redis: Redis = Depends(depends_redis)):
    return EventSourceResponse(subscribe(f"general", redis))


async def subscribe(channel: str, redis: Redis):
    (channel_subscription,) = await redis.subscribe(channel=Channel(channel, False))
    while await channel_subscription.wait_message():
        message = await channel_subscription.get_json()
        item_json = None
        with session_scope() as session:
            item_id = str(message["id"])
            item_type = message["type"]

            if item_type == "build":
                item = read_build(session, item_id)
                if item:
                    item_json = BuildReadItem.from_db(item).json()
            elif item_type == "run":
                item = read_run(session, item_id)
                if item:
                    item_json = RunReadItem.from_db(item).json()
            else:
                logger.warning("Did not send event for unsupported type '%s'", item_type)

        if item_json:
            logger.info("Send event '%s' received on '%s'", item_json, channel)
            yield { "event": "update", "data": item_json }
        else:
            logger.warning("Could not read updated build '%s'", item_id)
