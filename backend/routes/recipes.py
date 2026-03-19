import ast
import json

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import Recipe, User
from backend.schemas import RecipeRequest, RecipeResponse, SavedRecipeCreate, SavedRecipeResponse
from backend.services.llm_service import generate_structured_recipe


router = APIRouter()


def _load_serialized_value(raw_value: str, fallback):
    if raw_value is None:
        return fallback

    try:
        return json.loads(raw_value)
    except (TypeError, json.JSONDecodeError):
        try:
            return ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            return fallback


def _recipe_to_response(recipe: Recipe) -> SavedRecipeResponse:
    return SavedRecipeResponse(
        id=recipe.id,
        title=recipe.title,
        ingredients=_load_serialized_value(recipe.ingredients, []),
        preferences=_load_serialized_value(recipe.preferences, []),
        allergies=_load_serialized_value(recipe.allergies, []),
        steps=_load_serialized_value(recipe.steps, []),
        nutrition=_load_serialized_value(
            recipe.nutrition,
            {"calories": 0, "protein": "0g", "carbs": "0g", "fat": "0g"},
        ),
        created_at=recipe.created_at,
    )


@router.post("/generate-recipe", response_model=RecipeResponse)
def generate_recipe(request: RecipeRequest) -> RecipeResponse:
    return generate_structured_recipe(request)


@router.post("/recipes", response_model=SavedRecipeResponse, status_code=status.HTTP_201_CREATED)
def save_recipe(
    recipe: SavedRecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Recipe:
    db_recipe = Recipe(
        title=recipe.title,
        ingredients=json.dumps(recipe.ingredients),
        preferences=json.dumps(recipe.preferences),
        allergies=json.dumps(recipe.allergies),
        steps=json.dumps(recipe.steps),
        nutrition=json.dumps(recipe.nutrition.model_dump()),
        user_id=current_user.id,
    )

    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return _recipe_to_response(db_recipe)


@router.get("/recipes", response_model=list[SavedRecipeResponse])
def list_saved_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SavedRecipeResponse]:
    query = (
        db.query(Recipe)
        .filter(Recipe.user_id == current_user.id)
        .order_by(Recipe.created_at.desc())
        .all()
    )

    return [_recipe_to_response(recipe) for recipe in query]
