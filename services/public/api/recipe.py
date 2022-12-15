from fastapi import APIRouter, Depends, HTTPException
from public.auth import get_read
from public.schemas.recipe import RecipeReadItem, RecipeReadList, RecipeRevisionReadList, RecipeRevisionReadItem
from public.crud.recipe import read_recipes, read_recipe, read_recipe_revisions, read_recipe_revision
from sonja.database import get_session, Session

router = APIRouter()


@router.get("/ecosystem/{ecosystem_id}/recipe", response_model=RecipeReadList, response_model_by_alias=False,
            dependencies=[Depends(get_read)])
def get_recipe_list(ecosystem_id: str, session: Session = Depends(get_session)):
    return RecipeReadList.from_db(read_recipes(session, ecosystem_id))


@router.get("/recipe/{recipe_id}", response_model=RecipeReadItem, response_model_by_alias=False,
            dependencies=[Depends(get_read)])
def get_recipe_item(recipe_id: str, session: Session = Depends(get_session)):
    recipe = read_recipe(session, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RecipeReadItem.from_db(recipe)


@router.get("/recipe/{recipe_id}/revision", response_model=RecipeRevisionReadList, response_model_by_alias=False,
            dependencies=[Depends(get_read)])
def get_recipe_revision_list(recipe_id: str, session: Session = Depends(get_session)):
    return RecipeRevisionReadList.from_db(read_recipe_revisions(session, recipe_id))


@router.get("/recipe_revision/{recipe_revision_id}", response_model=RecipeRevisionReadItem,
            response_model_by_alias=False, dependencies=[Depends(get_read)])
def get_recipe_revision_item(recipe_revision_id: str, session: Session = Depends(get_session)):
    recipe_revision = read_recipe_revision(session, recipe_revision_id)
    if recipe_revision is None:
        raise HTTPException(status_code=404, detail="Recipe revision not found")
    return RecipeRevisionReadItem.from_db(recipe_revision)
