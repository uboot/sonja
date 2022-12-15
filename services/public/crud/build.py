from public.schemas.build import BuildWriteItem, StatusEnum
from sonja.database import Build, Channel, Commit, Profile, Repo, Session
from sqlalchemy import desc
from typing import Optional

from sonja.model import BuildStatus
from sonja.redis import RedisClient


def read_builds(session: Session, ecosystem_id: str, repo_id: Optional[str] = None, channel_id: Optional[str] = None,
                profile_id: Optional[str] = None, page: Optional[int] = None, per_page:  Optional[int] = None)\
        -> dict:
    objs = session.query(Build)\
        .join(Build.profile)\
        .join(Build.commit)\
        .join(Commit.channel)\
        .join(Commit.repo)\
        .filter(Profile.ecosystem_id == ecosystem_id)

    if repo_id:
        objs = objs.filter(Repo.id == repo_id)

    if profile_id:
        objs = objs.filter(Profile.id == profile_id)

    if channel_id:
        objs = objs.filter(Channel.id == channel_id)

    objs = objs.order_by(desc(Build.created), Build.id)

    if page is not None and per_page is not None:
        count = objs.count()

        objs = objs\
            .limit(per_page)\
            .offset(per_page * (page - 1))

        total_pages = count // per_page
        if count % per_page:
            total_pages += 1

        return {
            "objs": objs,
            "total_pages": total_pages
        }
    else:

        return {
            "objs": objs.all()
        }


def read_build(session: Session, build_id: str) -> Build:
    return session.query(Build).filter(Build.id == build_id).first()


def update_build(session: Session, redis_client: RedisClient, build_id: str, build_item: BuildWriteItem) -> Build:
    build = session.query(Build).filter(Build.id == build_id).with_for_update().first()

    if build_item.data.attributes.status == StatusEnum.stopping:
        if build.status == BuildStatus.new:
            build.status = BuildStatus.stopped
        elif build.status == BuildStatus.active:
            build.status = BuildStatus.stopping
    elif build_item.data.attributes.status == StatusEnum.new:
        if build.status == BuildStatus.active:
            pass
        elif build.status == BuildStatus.stopping:
            pass
        else:
            build.status = BuildStatus.new
            build.missing_recipes = []
            build.missing_packages = []

    session.commit()
    redis_client.publish_build_update(build)

    return build
