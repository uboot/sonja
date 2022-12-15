from public.schemas.github import PushPayload
from sonja.client import Crawler
from sonja.database import Session
from sonja.model import Repo


def process_push(session: Session, crawler: Crawler, payload: PushPayload):
    repos = session.query(Repo).filter(Repo.url.like(f"%/{payload.repository}")).all()
    crawler.process_repo("1", payload.after, payload.ref)
