# coding: utf-8

from __future__ import absolute_import

from conanci import database
from conanci.test import util
from flask import json
from swagger_server import models
from swagger_server.test import BaseTestCase


class TestProfileController(BaseTestCase):
    """ProfileController integration test stubs"""

    def setUp(self):
        with database.session_scope() as session:
            profile = util.create_profile()
            session.add(profile)

    def test_add_profile(self):
        """Test case for add_profile

        add a new profile
        """
        body = self.__create_profile("Linux", "conanio/gcc9")
        response = self.client.open(
            '/profile',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert201(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_profile(self):
        """Test case for delete_profile

        delete a profile
        """
        response = self.client.open(
            '/profile/{profile_id}'.format(profile_id=1),
            method='DELETE')
        self.assert204(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_profile(self):
        """Test case for get_profile

        get a profile
        """
        response = self.client.open(
            '/profile/{profile_id}'.format(profile_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_profile(self):
        """Test case for update_profile

        update a profile
        """
        body = self.__create_profile("Linux", "conanio/gcc9")
        response = self.client.open(
            '/profile/{profile_id}'.format(profile_id=1),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def __create_profile(self, name, container):
        return models.ProfileData(
            data=models.Profile(
                type="profiles",
                attributes=models.ProfileAttributes(
                    name=name,
                    container=container,
                    settings=[models.ProfileAttributesSettings("os", "Linux")]
                ),
                relationships=models.ProfileRelationships(
                    ecosystem=models.RepoRelationshipsEcosystem(
                        data=models.RepoRelationshipsEcosystemData(
                            type="ecosystems",
                            id=1
                        )
                    )
                )
            )
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
