from fastapi import APIRouter, Depends, HTTPException, status
from public.auth import get_admin, get_current_user, get_permissions, get_read
from public.schemas.user import PermissionEnum, UserReadItem, UserReadList, UserWriteItem
from public.crud.user import create_user, delete_user, read_users, read_user_by_id, update_user, OperationFailed, NotFound
from sonja.database import get_session, Session, User
from sonja.auth import test_password
from typing import List

router = APIRouter()


@router.get("/user/me", response_model=UserReadItem)
def get_current_user_item(user: User = Depends(get_current_user), authorized: bool = Depends(get_read)):
    return UserReadItem.from_db(user)


@router.get("/user/{user_id}", response_model=UserReadItem)
def get_user_item(user_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    user = read_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserReadItem.from_db(user)


@router.get("/user", response_model=UserReadList)
def get_user_item(session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    users = read_users(session)
    return UserReadList.from_db(users)


@router.post("/user", response_model=UserReadItem, status_code=status.HTTP_201_CREATED)
def post_user_item(user: UserWriteItem, session: Session = Depends(get_session), authorized: bool = Depends(get_admin)):
    new_user = create_user(session, user)
    return UserReadItem.from_db(new_user)


@router.patch("/user/{user_id}", response_model=UserReadItem)
def get_user_item(user_id: str, user_item: UserWriteItem, session: Session = Depends(get_session),
                  current_user: User = Depends(get_current_user),
                  permissions: List[PermissionEnum] = Depends(get_permissions),
                  authorized: bool = Depends(get_read)):
    if int(user_id) != current_user.id and PermissionEnum.admin not in permissions:
        raise HTTPException(status_code=403, detail="Non-admins can only update themselves")

    if int(user_id) == current_user.id and user_item.data.attributes.password:
        if (not user_item.data.attributes.old_password
                or not test_password(user_item.data.attributes.old_password, current_user.password)):
            raise HTTPException(status_code=403, detail="Provided wrong old password")

    user = read_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    patched_user = update_user(session, user, user_item)
    return UserReadItem.from_db(patched_user)


@router.delete("/user/{user_id}", responses={
    400: {"description": "Last user or current users can not be deleted"},
    403: {"description": "Not allowed"},
    404: {"description": "User not found"}
})
def delete_user_item(user_id: str, session: Session = Depends(get_session),
                     current_user: User = Depends(get_current_user),
                     authorized: bool = Depends(get_admin)):
    if int(user_id) == current_user.id:
        raise HTTPException(status_code=400, detail="Current user can not be deleted")

    try:
        delete_user(session, user_id)
    except OperationFailed:
        raise HTTPException(status_code=400, detail="Last user can not be deleted")
    except NotFound:
        raise HTTPException(status_code=404, detail="User not found")
