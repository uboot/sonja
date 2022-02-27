from fastapi import APIRouter

from public.api import build, channel, ecosystem, general, profile, repo, user, recipe

router = APIRouter()
router.include_router(ecosystem.router, tags=["Ecosystem"])
router.include_router(general.router, tags=["General"])
router.include_router(user.router, tags=["User"])
router.include_router(repo.router, tags=["Repo"])
router.include_router(profile.router, tags=["Profile"])
router.include_router(channel.router, tags=["Channel"])
router.include_router(build.router, tags=["Build"])
router.include_router(recipe.router, tags=["Recipe"])