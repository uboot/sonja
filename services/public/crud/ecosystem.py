from public.schemas.ecosystem import EcosystemWriteItem
from sonja.database import Session, Ecosystem
from sonja.ssh import encode, generate_rsa_key
from typing import List


def read_ecosystems(session: Session) -> List[Ecosystem]:
    return session.query(Ecosystem).all()


def read_ecosystem(session: Session, ecosystem_id: str) -> Ecosystem:
    return session.query(Ecosystem).filter(Ecosystem.id == ecosystem_id).first()


def create_ecosystem(session: Session, ecosystem_item: EcosystemWriteItem) -> Ecosystem:
    ecosystem = Ecosystem(**ecosystem_item.data.attributes.dict(exclude_unset=True, by_alias=True))
    private, public = generate_rsa_key()
    ecosystem.ssh_key = encode(private)
    ecosystem.public_ssh_key = encode(public)
    session.add(ecosystem)
    session.commit()
    return ecosystem


def update_ecosystem(session: Session, ecosystem: Ecosystem, ecosystem_item: EcosystemWriteItem) -> Ecosystem:
    data = ecosystem_item.data.attributes.dict(exclude_unset=True, by_alias=True)
    for attribute in data:
        setattr(ecosystem, attribute, data[attribute])
    session.commit()
    return ecosystem


def delete_ecosystem(session: Session, ecosystem: Ecosystem) -> None:
    session.delete(ecosystem)
