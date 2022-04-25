from public.schemas.build import BuildWriteItem, StatusEnum
from aioredis import Redis
from sonja.database import Profile, Build, Session
from sqlalchemy import desc
from typing import List


def read_builds(session: Session, ecosystem_id: str) -> List[Build]:
    return session.query(Build).\
        join(Build.profile).\
        filter(Profile.ecosystem_id == ecosystem_id).\
        order_by(desc(Build.created))\
        .all()


def read_build(session: Session, build_id: str) -> Build:
    return session.query(Build).filter(Build.id == build_id).first()


async def update_build(session: Session, redis: Redis, build: Build, build_item: BuildWriteItem) -> Build:
    data = build_item.data.attributes.dict(exclude_unset=True, by_alias=True)
    for attribute in data:
        setattr(build, attribute, data[attribute])

    if build_item.data.attributes.status == StatusEnum.new:
        build.log.logs = ''
        build.missing_recipes = []
        build.missing_packages = []

    session.commit()
    await redis.publish_json(f"ecosystem:{build.ecosystem.id}:build", {"id": build.id})

    return build
