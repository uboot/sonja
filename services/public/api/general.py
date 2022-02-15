from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from public.auth import get_admin, get_write
from sonja.database import get_session, Session, User, populate_database, reset_database, clear_ecosystems
from sonja.auth import test_password, create_access_token
from sonja.client import Crawler

router = APIRouter()
crawler = Crawler()


@router.get("/ping")
def get_ping():
    pass


@router.get("/clear_ecosystems")
def get_clear_ecosystems(authorized: bool = Depends(get_admin)):
    clear_ecosystems()


@router.get("/populate_database")
def get_populate_database(authorized: bool = Depends(get_admin)):
    populate_database()


@router.get("/process_repo/{repo_id}")
def get_process_repo(repo_id: str, authorized: bool = Depends(get_write)):
    if not crawler.process_repo(repo_id):
        raise HTTPException(status_code=400, detail="Failed")


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    record = session.query(User).filter_by(user_name=form_data.username).first()
    if not record or not record.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not test_password(form_data.password, record.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(str(record.id), expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
