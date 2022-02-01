from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from public.crud.user import read_user_by_id
from public.schemas.user import PermissionEnum
from sonja.auth import decode_access_token
from sonja.database import get_session, Session, User
from typing import List


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    user_id = decode_access_token(token)
    return read_user_by_id(session, user_id)


def get_permissions(user: User = Depends(get_current_user)) -> List[PermissionEnum]:
    return [PermissionEnum(p.label.name) for p in user.permissions]


def get_read(permissions: List[PermissionEnum] = Depends(get_permissions)) -> bool:
    if PermissionEnum.read not in permissions:
        raise HTTPException(status_code=403, detail="Operation not allowed")
    return True


def get_write(permissions: List[PermissionEnum] = Depends(get_permissions)) -> bool:
    if PermissionEnum.write not in permissions:
        raise HTTPException(status_code=403, detail="Operation not allowed")
    return True


def get_admin(permissions: List[PermissionEnum] = Depends(get_permissions)) -> bool:
    if PermissionEnum.admin not in permissions:
        raise HTTPException(status_code=403, detail="Operation not allowed")
    return True
