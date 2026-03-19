import json
import re

from fastapi import HTTPException, status
from openai import OpenAI

from backend.config import settings
from backend.schemas import RecipeRequest, RecipeResponse


def _get_client() -> OpenAI:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured.",
        )
    return OpenAI(api_key=settings.openai_api_key)


def _strip_code_fences(raw_text: str) -> str:
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def generate_structured_recipe(request: RecipeRequest) -> RecipeResponse:
    prompt = f"""
Create one recipe using these ingredients: {", ".join(request.ingredients)}.
Dietary preferences: {", ".join(request.preferences) if request.preferences else "none"}.
Allergies to avoid: {", ".join(request.allergies) if request.allergies else "none"}.

Return only valid JSON with this exact structure:
{{
  "title": "string",
  "ingredients": ["string", "string"],
  "preferences": ["string"],
  "allergies": ["string"],
  "steps": ["string", "string", "string"],
  "nutrition_estimate": {{
    "calories": 0,
    "protein": "string",
    "carbs": "string",
    "fat": "string"
  }}
}}

Rules:
- Do not return markdown
- Do not return explanation text
- Respect dietary preferences and allergies
- Keep the recipe practical for a home cook
""".strip()

    client = _get_client()

    try:
        response = client.responses.create(model=settings.openai_model, input=prompt)
        recipe_text = _strip_code_fences(response.output_text)
        recipe_json = json.loads(recipe_text)
        return RecipeResponse.model_validate(recipe_json)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recipe generation failed because the AI response was invalid.",
        ) from exc
