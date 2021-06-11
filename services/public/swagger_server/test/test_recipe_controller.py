# coding: utf-8

from __future__ import absolute_import

from conanci import database
from conanci.test import util
from swagger_server.test import BaseTestCase


class TestRecipeController(BaseTestCase):
    """RecipeController integration test stubs"""

    def setUp(self):
        super().setUp()
        self.login()
        with database.session_scope() as session:
            ecosystem = util.create_recipe_revision(dict())
            session.add(ecosystem)

    def test_get_recipe(self):
        """Test case for get_recipe

        get a recipe
        """
        response = self.client.open(
            '/api/v1/recipe/{recipe_id}'.format(recipe_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_recipes(self):
        """Test case for get_recipes

        get all recipes
        """
        response = self.client.open(
            '/api/v1/ecosystem/{ecosystem_id}/recipe'.format(ecosystem_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_recipe_revision(self):
        """Test case for get_recipe_revision

        get a recipe revision
        """
        response = self.client.open(
            '/api/v1/recipe_revision/{recipe_revision_id}'.format(recipe_revision_id='1'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_recipe_revisions(self):
        """Test case for get_recipe_revisions

        get all recipe revision
        """
        response = self.client.open(
            '/api/v1/recipe/{recipe_id}/revision'.format(recipe_id='1'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

if __name__ == '__main__':
    import unittest
    unittest.main()
