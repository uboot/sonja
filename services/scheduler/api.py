from fastapi import APIRouter
from scheduler.config import scheduler


router = APIRouter()


@router.get("/ping")
def get_ping():
    pass


@router.get("/process_commits")
def get_process_commits():
    scheduler.trigger()
