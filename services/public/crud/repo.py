from public.schemas.repo import RepoWriteItem
from sonja.database import Ecosystem, Repo, Session
from typing import List


def read_repos(session: Session, ecosystem_id: str) -> List[Repo]:
    return session.query(Repo).filter(Repo.ecosystem_id == ecosystem_id).all()


def read_repo(session: Session, repo_id: str) -> Repo:
    return session.query(Repo).filter(Repo.id == repo_id).first()


def create_repo(session: Session, repo_item: RepoWriteItem) -> Repo:
    repo = Repo(**repo_item.data.attributes.dict(exclude_unset=True, by_alias=True))
    ecosystem = session.query(Ecosystem).filter(Ecosystem.id == repo_item.data.relationships.ecosystem.data.id).first()
    repo.ecosystem = ecosystem
    session.add(repo)
    session.commit()
    return repo


def update_repo(session: Session, repo: Repo, repo_item: RepoWriteItem) -> Repo:
    data = repo_item.data.attributes.dict(exclude_unset=True, by_alias=True)
    for attribute in data:
        setattr(repo, attribute, data[attribute])
    session.commit()
    return repo


def delete_repo(session: Session, repo: Repo) -> None:
    session.delete(repo)
