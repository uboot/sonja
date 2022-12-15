from public.schemas.github import PushPayload
from sonja.client import Crawler
from sonja.database import Session
from sonja.model import Repo


def process_push(session: Session, crawler: Crawler, payload: PushPayload):
    if not payload.after or not payload.ref:
        return

    repos = session.query(Repo).filter(Repo.url.like(f"%/{payload.repository.full_name}.git")).all()
    for repo in repos:
        crawler.process_repo(str(repo.id), payload.after, payload.ref)
