from fastapi import APIRouter
from agent.config import agent


router = APIRouter()


@router.get("/ping")
def get_ping():
    pass


@router.get("/process_builds")
def get_process_builds():
    agent.trigger()
    pass
