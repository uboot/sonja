from sonja.database import Configuration, Session
from public.schemas.configuration import ConfigurationItem
from secrets import token_hex


def read_configuration(session: Session) -> Configuration:
    return session.query(Configuration).first()


def update_configuration(session: Session, configuration: Configuration, configuration_item: ConfigurationItem)\
        -> Configuration:
    github_secret = configuration_item.data.attributes.github_secret
    if not github_secret:
        configuration.github_secret = token_hex(20)
    session.commit()
    return configuration
