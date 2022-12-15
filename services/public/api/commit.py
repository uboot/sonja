from fastapi import APIRouter, Depends, HTTPException
from public.auth import get_read
from public.schemas.commit import CommitReadItem, CommitReadList
from public.crud.commit import read_commits, read_commit
from sonja.database import get_session, Session

router = APIRouter()


@router.get("/repo/{repo_id}/commit", response_model=CommitReadList, response_model_by_alias=False,
            dependencies=[Depends(get_read)])
def get_commit_list(repo_id: str, session: Session = Depends(get_session)):
    return CommitReadList.from_db(read_commits(session, repo_id))


@router.get("/commit/{commit_id}", response_model=CommitReadItem, response_model_by_alias=False,
            dependencies=[Depends(get_read)])
def get_commit_item(commit_id: str, session: Session = Depends(get_session)):
    commit = read_commit(session, commit_id)
    if commit is None:
        raise HTTPException(status_code=404, detail="Commit not found")
    return CommitReadItem.from_db(commit)
