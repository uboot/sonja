from fastapi import APIRouter, Depends, HTTPException, status
from public.auth import get_read, get_write
from public.schemas.repo import RepoReadItem, RepoReadList, RepoWriteItem
from public.crud.repo import create_repo, delete_repo, read_repos, read_repo, update_repo
from sonja.database import get_session, Session
from sonja.client import Crawler

router = APIRouter()
crawler = Crawler()


@router.post("/repo", response_model=RepoReadItem, response_model_by_alias=False, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_write)])
def post_repo_item(repo: RepoWriteItem, session: Session = Depends(get_session)):
    new_repo = create_repo(session, repo)
    crawler.process_repo(new_repo.id)
    return RepoReadItem.from_db(new_repo)


@router.get("/ecosystem/{ecosystem_id}/repo", response_model=RepoReadList, response_model_by_alias=False,
            dependencies=[Depends(get_read)])
def get_repo_list(ecosystem_id: str, session: Session = Depends(get_session)):
    return RepoReadList.from_db(read_repos(session, ecosystem_id))


@router.get("/repo/{repo_id}", response_model=RepoReadItem, response_model_by_alias=False,
            dependencies=[Depends(get_read)])
def get_repo_item(repo_id: str, session: Session = Depends(get_session)):
    repo = read_repo(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    return RepoReadItem.from_db(repo)


@router.patch("/repo/{repo_id}", response_model=RepoReadItem, response_model_by_alias=False,
              dependencies=[Depends(get_write)])
def patch_repo_item(repo_id: str, repo_item: RepoWriteItem, session: Session = Depends(get_session)):
    repo = read_repo(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    patched_repo = update_repo(session, repo, repo_item)
    t = RepoReadItem.from_db(patched_repo)
    return t


@router.delete("/repo/{repo_id}", dependencies=[Depends(get_write)])
def delete_repo_item(repo_id: str, session: Session = Depends(get_session)):
    repo = read_repo(session, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    delete_repo(session, repo)
