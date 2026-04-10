import base64
import hashlib
import re
from pathlib import Path

from fastapi import HTTPException, status
from openai import OpenAI

from backend.config import settings


def _get_client() -> OpenAI:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured.",
        )
    return OpenAI(api_key=settings.openai_api_key)


def _normalize_text(value: str) -> str:
    return " ".join(re.sub(r"\s+", " ", value.strip().lower()).split())


VISUAL_IMPACT_PREFERENCES = {
    "vegetarian",
    "vegan",
    "pescatarian",
}


def _get_visual_impact_preferences(preferences: list[str]) -> list[str]:
    normalized_preferences = [
        _normalize_text(preference)
        for preference in preferences
        if _normalize_text(preference) in VISUAL_IMPACT_PREFERENCES
    ]
    return sorted(set(normalized_preferences))


def build_recipe_image_cache_key(
    title: str,
    ingredients: list[str],
    preferences: list[str],
    allergies: list[str],
) -> str:
    normalized_ingredients = sorted(_normalize_text(item) for item in ingredients if item.strip())
    visual_preferences = _get_visual_impact_preferences(preferences)
    digest_source = "||".join(
        [
            ",".join(normalized_ingredients),
            ",".join(visual_preferences),
        ]
    )
    return hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:24]


def build_recipe_image_prompt(
    title: str,
    ingredients: list[str],
    preferences: list[str],
    allergies: list[str],
) -> str:
    preference_text = ", ".join(preferences) if preferences else "none"
    allergy_text = ", ".join(allergies) if allergies else "none"
    ingredient_text = ", ".join(ingredients[:8])

    return (
        f"A clean, appetizing food thumbnail for the dish '{title}'. "
        f"Main visible ingredients: {ingredient_text}. "
        f"Dietary preferences to respect: {preference_text}. "
        f"Allergies to avoid showing: {allergy_text}. "
        "Styled as a realistic plated meal photo, centered composition, soft natural lighting, "
        "simple background, suitable as a small recipe thumbnail, no text, no labels, no collage."
    )


def _get_thumbnail_directory() -> Path:
    thumbnail_directory = Path(settings.recipe_thumbnail_directory)
    thumbnail_directory.mkdir(parents=True, exist_ok=True)
    return thumbnail_directory


def _get_thumbnail_path(cache_key: str) -> Path:
    return _get_thumbnail_directory() / f"{cache_key}.png"


def _to_public_image_url(cache_key: str) -> str:
    return f"/media/recipe_thumbnails/{cache_key}.png"


def ensure_recipe_thumbnail(
    title: str,
    ingredients: list[str],
    preferences: list[str],
    allergies: list[str],
    cache_ingredients: list[str] | None = None,
) -> dict[str, str]:
    cache_key = build_recipe_image_cache_key(
        title,
        cache_ingredients if cache_ingredients is not None else ingredients,
        preferences,
        allergies,
    )
    prompt = build_recipe_image_prompt(title, ingredients, preferences, allergies)
    thumbnail_path = _get_thumbnail_path(cache_key)

    if thumbnail_path.exists():
        return {
            "image_cache_key": cache_key,
            "image_path": str(thumbnail_path.as_posix()),
            "image_url": _to_public_image_url(cache_key),
            "image_prompt": prompt,
        }

    client = _get_client()

    try:
        response = client.images.generate(
            model=settings.openai_image_model,
            prompt=prompt,
            size="1024x1024",
            quality="low",
            output_format="png",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recipe image generation failed.",
        ) from exc

    image_data = response.data[0].b64_json if response.data else None
    if not image_data:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recipe image generation returned no image data.",
        )

    thumbnail_path.write_bytes(base64.b64decode(image_data))

    return {
        "image_cache_key": cache_key,
        "image_path": str(thumbnail_path.as_posix()),
        "image_url": _to_public_image_url(cache_key),
        "image_prompt": prompt,
    }
