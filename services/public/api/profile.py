from fastapi import APIRouter, Depends, HTTPException, status
from public.auth import get_read, get_write
from public.schemas.profile import ProfileReadItem, ProfileWriteItem
from public.crud.profile import create_profile, delete_profile, read_profile, update_profile
from sonja.database import get_session, Session

router = APIRouter()


@router.post("/profile", response_model=ProfileReadItem, response_model_by_alias=False,
             status_code=status.HTTP_201_CREATED)
def post_profile_item(profile: ProfileWriteItem, session: Session = Depends(get_session),
                   authorized: bool = Depends(get_write)):
    new_profile = create_profile(session, profile)
    return ProfileReadItem.from_db(new_profile)


@router.get("/profile/{profile_id}", response_model=ProfileReadItem, response_model_by_alias=False)
def get_profile_item(profile_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_read)):
    profile = read_profile(session, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileReadItem.from_db(profile)


@router.patch("/profile/{profile_id}", response_model=ProfileReadItem, response_model_by_alias=False)
def get_profile_item(profile_id: str, profile_item: ProfileWriteItem, session: Session = Depends(get_session),
                  authorized: bool = Depends(get_write)):
    profile = read_profile(session, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    patched_profile = update_profile(session, profile, profile_item)
    return ProfileReadItem.from_db(patched_profile)


@router.delete("/profile/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile_item(profile_id: str, session: Session = Depends(get_session), authorized: bool = Depends(get_write)):
    profile = read_profile(session, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    delete_profile(session, profile)
