from public.schemas.user import UserWriteItem
from sonja.database import Session, User, remove_but_last_user, OperationFailed, NotFound
from typing import List


def read_user_by_id(session: Session, user_id: str) -> User:
    return session.query(User).filter(User.id == user_id).first()


def read_users(session: Session) -> List[User]:
    return session.query(User).all()


def create_user(session: Session, user_item: UserWriteItem) -> User:
    user = User(**user_item.data.attributes.dict(exclude_unset=True, exclude={"old_password"}, by_alias=True))
    session.add(user)
    session.commit()
    return user


def update_user(session: Session, user: User, user_item: UserWriteItem) -> User:
    data = user_item.data.attributes.dict(exclude_unset=True, exclude={"old_password"}, by_alias=True)
    for attribute in data:
        setattr(user, attribute, data[attribute])
    session.commit()
    return user


def delete_user(session: Session, user_id: str):
    remove_but_last_user(session, user_id)
