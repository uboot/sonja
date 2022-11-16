from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from public.crud.user import read_user_by_id
from public.crud.configuration import read_configuration
from public.schemas.user import PermissionEnum
from sonja.auth import decode_access_token, ExpiredSignatureError
from sonja.database import get_session, Session, User
from typing import List
from hmac import HMAC, compare_digest
from hashlib import sha256


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    try:
        user_id = decode_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
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


async def get_github(request: Request, session: Session = Depends(get_session)):
    configuration = read_configuration(session)
    provided_signature = request.headers["X-Hub-Signature-256"].split('sha256=')[-1].strip()
    body = await request.body()
    data_signature = HMAC(key=configuration.github_secret.encode(), msg=body, digestmod=sha256).hexdigest()
    if not compare_digest(provided_signature, data_signature):
        raise HTTPException(status_code=403, detail="Signature is not valid")