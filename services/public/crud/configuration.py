from sonja.database import Configuration, Session
from public.schemas.configuration import ConfigurationItem
from sonja.ssh import encode, generate_rsa_key
from secrets import token_hex


def read_configuration(session: Session) -> Configuration:
    return session.query(Configuration).first()


def update_configuration(session: Session, configuration: Configuration, configuration_item: ConfigurationItem)\
        -> Configuration:
    data = configuration_item.data.attributes.dict(exclude_unset=True, by_alias=True)
    for attribute in data:
        if attribute == "public_ssh_key":
            if not data["public_ssh_key"]:
                private, public = generate_rsa_key()
                configuration.ssh_key = encode(private)
                configuration.public_ssh_key = encode(public)
            continue
        elif attribute == "github_secret":
            if not data["github_secret"]:
                configuration.github_secret = token_hex(20)
            continue
        setattr(configuration, attribute, data[attribute])
    session.commit()
    return configuration
