import connexion

from conanci import database
from flask import abort
from swagger_server.models import ProfileAttributes, ProfileRelationships, RepoRelationshipsEcosystem, \
    RepoRelationshipsEcosystemData, ProfileAttributesSettings
from swagger_server.models.inline_response2003 import InlineResponse2003  # noqa: E501
from swagger_server.models.inline_response2004 import InlineResponse2004  # noqa: E501
from swagger_server.models.profile import Profile  # noqa: E501


def __create_profile(record: database.Profile):
    return Profile(
        id=record.id,
        type="profile",
        attributes=ProfileAttributes(
            name=record.name,
            container=record.container,
            settings=[ProfileAttributesSettings(key=r.key, value=r.value) for r in record.settings]
        ),
        relationships=ProfileRelationships(
            ecosystem=RepoRelationshipsEcosystem(
                data=RepoRelationshipsEcosystemData(
                    id=record.ecosystem_id,
                    type="ecosystem"
                )
            )
        )
    )

def add_profile(body=None):  # noqa: E501
    """add a new profile

     # noqa: E501

    :param body: profile to add
    :type body: dict | bytes

    :rtype: Profile
    """
    if connexion.request.is_json:
        body = Profile.from_dict(connexion.request.get_json())  # noqa: E501
        with database.session_scope() as session:
            ecosystem = session.query(database.Ecosystem)\
                .filter_by(id=body.relationships.ecosystem.data.id)\
                .first()
            if not ecosystem:
                abort(400)
            record = database.Profile()
            record.name = body.attributes.name
            record.ecosystem = ecosystem
            record.container = body.attributes.container
            record.settings = [database.Setting(s.key, s.value) for s in body.attributes.settings]
            session.add(record)
            session.commit()
            return __create_profile(record)


def delete_profile(profile_id):  # noqa: E501
    """delete a profile

     # noqa: E501

    :param profile_id: profile id to delete
    :type profile_id: int

    :rtype: None
    """
    with database.session_scope() as session:
        record = session.query(database.Profile).filter_by(id=profile_id).first()
        if not record:
            abort(404)
        session.delete(record)
    return None


def get_profile(profile_id):  # noqa: E501
    """get a profile

     # noqa: E501

    :param profile_id: profile ID
    :type profile_id: int

    :rtype: InlineResponse2004
    """
    with database.session_scope() as session:
        record = session.query(database.Profile).filter_by(id=profile_id).first()
        if not record:
            abort(404)
        return InlineResponse2004(data=__create_profile(record))


def get_profiles(ecosystem_id):  # noqa: E501
    """get all active profiles

     # noqa: E501

    :param ecosystem_id: ecosystem
    :type ecosystem_id: int

    :rtype: InlineResponse2003
    """
    with database.session_scope() as session:
        return InlineResponse2003(
            data=[__create_profile(record) for record in
                  session.query(database.Profile).filter_by(ecosystem_id=ecosystem_id).all()]
        )
