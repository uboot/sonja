from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_recipe, create_recipe_revision, run_create_operation

client = TestClient(app)


class TestRecipe(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_recipe_revision, dict())

    def test_get_recipe(self):
        recipe_id = run_create_operation(create_recipe, dict())
        response = client.get(f"{api_prefix}/recipe/{recipe_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_recipes(self):
        response = client.get(f"{api_prefix}/ecosystem/1/recipe", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_recipe_revisions(self):
        response = client.get(f"{api_prefix}/recipe/1/revision", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_recipe_revision(self):
        recipe_revision_id = run_create_operation(create_recipe_revision, dict())
        response = client.get(f"{api_prefix}/recipe_revision/{recipe_revision_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
