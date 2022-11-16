from fastapi import APIRouter, Depends, status
from public.schemas.github import PushPayload
from public.auth import get_github
from sonja.config import logger

router = APIRouter()


@router.post("/github/push", status_code=status.HTTP_202_ACCEPTED)
def post_push_item(payload: PushPayload, authorized: bool = Depends(get_github)):
    logger.info("Received push event %s", payload.json())
