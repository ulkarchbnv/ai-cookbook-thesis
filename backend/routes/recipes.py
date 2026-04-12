import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user, get_optional_current_user
from backend.models import GeneratedRecipe, User
from backend.schemas import (
    GeneratedRecipeHistoryResponse,
    RecipeRequest,
    RecipeResponse,
    SavedRecipeCreate,
    SavedRecipeResponse,
)
from backend.services.recipe_image_service import ensure_recipe_thumbnail
from backend.services.llm_service import generate_structured_recipe
from backend.utils import build_recipe_fingerprint, load_serialized_value


router = APIRouter()


def _load_nutrition(raw_value: str | None) -> dict[str, str | int]:
    nutrition = load_serialized_value(raw_value, {})
    if not isinstance(nutrition, dict):
        nutrition = {}
    return {
        "calories": nutrition.get("calories", 0),
        "protein": nutrition.get("protein", "0g"),
        "carbs": nutrition.get("carbs", "0g"),
        "fat": nutrition.get("fat", "0g"),
    }

def _build_image_url(image_path: str | None, image_url: str | None) -> str | None:
    if image_url:
        return image_url
    if image_path:
        return image_path.replace("backend/media", "/media").replace("\\", "/")
    return None


def _generated_recipe_to_saved_response(recipe: GeneratedRecipe) -> SavedRecipeResponse:
    return SavedRecipeResponse(
        id=recipe.id,
        title=recipe.title,
        ingredients=load_serialized_value(recipe.ingredients, []),
        preferences=load_serialized_value(recipe.preferences, []),
        allergies=load_serialized_value(recipe.allergies, []),
        steps=load_serialized_value(recipe.steps, []),
        nutrition=_load_nutrition(recipe.nutrition),
        image_url=_build_image_url(recipe.image_path, recipe.image_url),
        image_cache_key=recipe.image_cache_key,
        saved_at=recipe.saved_at,
        created_at=recipe.created_at,
    )


def _generated_recipe_to_history_response(recipe: GeneratedRecipe) -> GeneratedRecipeHistoryResponse:
    return GeneratedRecipeHistoryResponse(
        id=recipe.id,
        fingerprint=recipe.fingerprint,
        title=recipe.title,
        ingredients=load_serialized_value(recipe.ingredients, []),
        preferences=load_serialized_value(recipe.preferences, []),
        allergies=load_serialized_value(recipe.allergies, []),
        steps=load_serialized_value(recipe.steps, []),
        nutrition=_load_nutrition(recipe.nutrition),
        warnings=load_serialized_value(recipe.warnings, []),
        image_url=_build_image_url(recipe.image_path, recipe.image_url),
        image_cache_key=recipe.image_cache_key,
        is_saved=recipe.is_saved,
        saved_at=recipe.saved_at,
        created_at=recipe.created_at,
    )


@router.post("/generate-recipe", response_model=RecipeResponse)
def generate_recipe(
    request: RecipeRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> RecipeResponse:
    recipe = generate_structured_recipe(request)
    image_update: dict[str, str | None] = {
        "image_url": None,
        "image_cache_key": None,
    }
    warnings = list(recipe.warnings)
    image_fields: dict[str, str | None] = {
        "image_url": None,
        "image_path": None,
        "image_cache_key": None,
        "image_prompt": None,
    }

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
        image_fields = image_metadata
    except HTTPException:
        warnings.append("Recipe image could not be generated right now, so no thumbnail was attached.")

    generated_recipe_id: int | None = None
    if current_user:
        fingerprint = build_recipe_fingerprint(
            title=recipe.title,
            ingredients=recipe.ingredients,
            preferences=recipe.preferences,
            allergies=recipe.allergies,
            steps=recipe.steps,
        )
        db_generated_recipe = GeneratedRecipe(
            fingerprint=fingerprint,
            title=recipe.title,
            ingredients=json.dumps(recipe.ingredients),
            preferences=json.dumps(recipe.preferences),
            allergies=json.dumps(recipe.allergies),
            steps=json.dumps(recipe.steps),
            nutrition=json.dumps(recipe.nutrition_estimate.model_dump()),
            warnings=json.dumps(warnings),
            image_url=image_fields["image_url"],
            image_path=image_fields["image_path"],
            image_cache_key=image_fields["image_cache_key"],
            image_prompt=image_fields["image_prompt"],
            is_saved=False,
            user_id=current_user.id,
        )
        db.add(db_generated_recipe)
        db.commit()
        db.refresh(db_generated_recipe)
        generated_recipe_id = db_generated_recipe.id

    return recipe.model_copy(
        update={
            "generated_recipe_id": generated_recipe_id,
            **image_update,
            "warnings": warnings,
        }
    )


@router.post("/recipes", response_model=SavedRecipeResponse, status_code=status.HTTP_201_CREATED)
def save_recipe(
    recipe: SavedRecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedRecipeResponse:
    generated_recipe = (
        db.query(GeneratedRecipe)
        .filter(
            GeneratedRecipe.id == recipe.generated_recipe_id,
            GeneratedRecipe.user_id == current_user.id,
        )
        .first()
    )
    if not generated_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated recipe not found.")

    generated_recipe.is_saved = True
    generated_recipe.saved_at = datetime.now(timezone.utc)
    db.add(generated_recipe)
    db.commit()
    db.refresh(generated_recipe)
    return _generated_recipe_to_saved_response(generated_recipe)


@router.get("/recipes", response_model=list[SavedRecipeResponse])
def list_saved_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SavedRecipeResponse]:
    query = (
        db.query(GeneratedRecipe)
        .filter(
            GeneratedRecipe.user_id == current_user.id,
            GeneratedRecipe.is_saved.is_(True),
        )
        .order_by(GeneratedRecipe.saved_at.desc(), GeneratedRecipe.created_at.desc())
        .all()
    )

    return [_generated_recipe_to_saved_response(recipe) for recipe in query]


@router.get("/recipes/history", response_model=list[GeneratedRecipeHistoryResponse])
def list_generated_recipe_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GeneratedRecipeHistoryResponse]:
    query = (
        db.query(GeneratedRecipe)
        .filter(GeneratedRecipe.user_id == current_user.id)
        .order_by(GeneratedRecipe.created_at.desc())
        .all()
    )

    return [_generated_recipe_to_history_response(recipe) for recipe in query]
