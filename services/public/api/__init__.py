from fastapi import APIRouter

from public.api import general, user

router = APIRouter()
router.include_router(general.router, tags=["General"])
router.include_router(user.router, tags=["User"])