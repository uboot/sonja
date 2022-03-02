from sonja.database import Package, Session


def read_package(session: Session, package_id: str) -> Package:
    return session.query(Package).filter(Package.id == package_id).first()
