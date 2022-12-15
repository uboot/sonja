from fastapi import APIRouter, Depends, status
from public.schemas.github import PushPayload
from public.auth import get_github
from public.crud.github import process_push
from public.client import get_crawler
from sonja.config import logger
from sonja.client import Crawler
from sonja.database import get_session, Session

router = APIRouter()


@router.post("/github/push", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(get_github)])
def post_push_item(payload: PushPayload, session: Session = Depends(get_session),
                   crawler: Crawler = Depends(get_crawler)):
    logger.info("Received push event %s", payload.json())
    process_push(session, crawler, payload)

