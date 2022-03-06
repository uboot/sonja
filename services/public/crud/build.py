from public.schemas.build import BuildWriteItem, StatusEnum
from sonja.database import Profile, Build, Session
from typing import List


def read_builds(session: Session, ecosystem_id: str) -> List[Build]:
    return session.query(Build).\
        join(Build.profile).\
        filter(Profile.ecosystem_id == ecosystem_id).all()


def read_build(session: Session, build_id: str) -> Build:
    return session.query(Build).filter(Build.id == build_id).first()


def update_build(session: Session, build: Build, build_item: BuildWriteItem) -> Build:
    data = build_item.data.attributes.dict(exclude_unset=True, by_alias=True)
    for attribute in data:
        setattr(build, attribute, data[attribute])

    if build_item.data.attributes.status == StatusEnum.new:
        build.log.logs = ''

    session.commit()
    return build
