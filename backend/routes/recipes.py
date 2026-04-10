import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import Recipe, User
from backend.schemas import RecipeRequest, RecipeResponse, SavedRecipeCreate, SavedRecipeResponse
from backend.services.recipe_image_service import ensure_recipe_thumbnail
from backend.services.llm_service import generate_structured_recipe
from backend.utils import load_serialized_value


router = APIRouter()

def _recipe_to_response(recipe: Recipe) -> SavedRecipeResponse:
    return SavedRecipeResponse(
        id=recipe.id,
        title=recipe.title,
        ingredients=load_serialized_value(recipe.ingredients, []),
        preferences=load_serialized_value(recipe.preferences, []),
        allergies=load_serialized_value(recipe.allergies, []),
        steps=load_serialized_value(recipe.steps, []),
        nutrition=load_serialized_value(
            recipe.nutrition,
            {"calories": 0, "protein": "0g", "carbs": "0g", "fat": "0g"},
        ),
        image_url=(
            recipe.image_path.replace("backend/media", "/media").replace("\\", "/")
            if recipe.image_path
            else None
        ),
        image_cache_key=recipe.image_cache_key,
        created_at=recipe.created_at,
    )


@router.post("/generate-recipe", response_model=RecipeResponse)
def generate_recipe(request: RecipeRequest) -> RecipeResponse:
    recipe = generate_structured_recipe(request)
    image_update: dict[str, str | None] = {
        "image_url": None,
        "image_cache_key": None,
    }
    warnings = list(recipe.warnings)

    try:
        image_metadata = ensure_recipe_thumbnail(
            title=recipe.title,
            ingredients=recipe.ingredients,
            preferences=recipe.preferences,
            allergies=recipe.allergies,
            cache_ingredients=request.ingredients,
        )
        image_update = {
            "image_url": image_metadata["image_url"],
            "image_cache_key": image_metadata["image_cache_key"],
        }
    except HTTPException:
        warnings.append("Recipe image could not be generated right now, so no thumbnail was attached.")

    return recipe.model_copy(
        update={
            **image_update,
            "warnings": warnings,
        }
    )


@router.post("/recipes", response_model=SavedRecipeResponse, status_code=status.HTTP_201_CREATED)
def save_recipe(
    recipe: SavedRecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Recipe:
    image_fields: dict[str, str | None] = {
        "image_cache_key": None,
        "image_path": None,
        "image_prompt": None,
    }

    try:
        image_metadata = ensure_recipe_thumbnail(
            title=recipe.title,
            ingredients=recipe.ingredients,
            preferences=recipe.preferences,
            allergies=recipe.allergies,
        )
        image_fields = {
            "image_cache_key": image_metadata["image_cache_key"],
            "image_path": image_metadata["image_path"],
            "image_prompt": image_metadata["image_prompt"],
        }
    except HTTPException:
        pass

    db_recipe = Recipe(
        title=recipe.title,
        ingredients=json.dumps(recipe.ingredients),
        preferences=json.dumps(recipe.preferences),
        allergies=json.dumps(recipe.allergies),
        steps=json.dumps(recipe.steps),
        nutrition=json.dumps(recipe.nutrition.model_dump()),
        image_cache_key=image_fields["image_cache_key"],
        image_path=image_fields["image_path"],
        image_prompt=image_fields["image_prompt"],
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
