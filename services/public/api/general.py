from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sonja.database import Session
from sonja.database import get_session
from sonja.database import User
from sonja.auth import test_password, create_access_token

router = APIRouter()


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
