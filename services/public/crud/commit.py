from sonja.database import Commit, Session
from typing import List


def read_commits(session: Session, repo_id: str) -> List[Commit]:
    return session.query(Commit).filter(Commit.repo_id == repo_id).all()


def read_commit(session: Session, commit_id: str) -> Commit:
    return session.query(Commit).filter(Commit.id == commit_id).first()
