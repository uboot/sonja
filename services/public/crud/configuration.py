from sonja.database import Configuration, Session
from public.schemas.configuration import ConfigurationItem


def read_configuration(session: Session) -> Configuration:
    return session.query(Configuration).first()


def update_configuration(session: Session, configuration: Configuration, configuration_item: ConfigurationItem)\
        -> Configuration:
    data = configuration_item.data.attributes.dict(exclude_unset=True, by_alias=True)
    for attribute in data:
        setattr(configuration, attribute, data[attribute])
    session.commit()
    return configuration
