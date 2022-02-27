from sonja.database import Recipe, Session, RecipeRevision
from typing import List


def read_recipes(session: Session, ecosystem_id: str) -> List[Recipe]:
    return session.query(Recipe).filter(Recipe.ecosystem_id == ecosystem_id).all()


def read_recipe(session: Session, recipe_id: str) -> Recipe:
    return session.query(Recipe).filter(Recipe.id == recipe_id).first()


def read_recipe_revision(session: Session, recipe_revision_id: str) -> RecipeRevision:
    return session.query(RecipeRevision).filter_by(id=recipe_revision_id).first()


def read_recipe_revisions(session: Session, recipe_id: str) -> List[RecipeRevision]:
    return session.query(RecipeRevision).filter(RecipeRevision.recipe_id == recipe_id)