from fastapi import APIRouter

from public.api import ecosystem, general, profile, repo, user

router = APIRouter()
router.include_router(ecosystem.router, tags=["Ecosystem"])
router.include_router(general.router, tags=["General"])
router.include_router(user.router, tags=["User"])
router.include_router(repo.router, tags=["Repo"])
router.include_router(profile.router, tags=["Profile"])