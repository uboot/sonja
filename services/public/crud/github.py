from public.schemas.github import PushPayload
from sonja.client import Crawler
from sonja.database import Session
from sonja.model import Repo


def process_push(session: Session, crawler: Crawler, payload: PushPayload):
    if not payload.after or not payload.ref:
        return

    https_repos = session.query(Repo)\
        .filter_by(url=f"https://github.com/{payload.repository.full_name}.git")\
        .all()

    ssh_repos = session.query(Repo)\
        .filter_by(url=f"git@github.com:{payload.repository.full_name}.git")\
        .all()

    for repo in https_repos + ssh_repos:
        crawler.process_repo(str(repo.id), payload.after, payload.ref)
