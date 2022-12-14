from fastapi import APIRouter
from crawler.config import crawler

router = APIRouter()


@router.get("/ping")
def get_ping():
    pass


@router.get("/process_repo/{repo_id}")
def get_process_repo(repo_id: str, sha: str = "", ref: str = ""):
    crawler.process_repo(repo_id, sha, ref)
    crawler.trigger()
