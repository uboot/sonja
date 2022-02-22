from public.schemas.profile import ProfileWriteItem
from sonja.database import Ecosystem, Profile, Session


def read_profile(session: Session, profile_id: str) -> Profile:
    return session.query(Profile).filter(Profile.id == profile_id).first()


def create_profile(session: Session, profile_item: ProfileWriteItem) -> Profile:
    profile = Profile(**profile_item.data.attributes.dict(exclude_unset=True, by_alias=True))
    ecosystem = session.query(Ecosystem).filter(Ecosystem.id == profile_item.data.relationships.ecosystem.data.id).first()
    profile.ecosystem = ecosystem
    session.add(profile)
    session.commit()
    return profile


def update_profile(session: Session, profile: Profile, profile_item: ProfileWriteItem) -> Profile:
    data = profile_item.data.attributes.dict(exclude_unset=True, by_alias=True)
    for attribute in data:
        setattr(profile, attribute, data[attribute])
    session.commit()
    return profile


def delete_profile(session: Session, profile: Profile) -> None:
    session.delete(profile)
