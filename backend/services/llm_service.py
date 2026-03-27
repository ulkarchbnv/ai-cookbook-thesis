import json
import re

from fastapi import HTTPException, status
from openai import OpenAI

from backend.config import settings
from backend.schemas import RecipeRequest, RecipeResponse
from backend.services.rag_service import (
    find_conflicting_ingredients,
    find_preference_conflicting_ingredients,
    get_generation_restrictions,
    retrieve_recipe_context,
)


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


def _format_retrieved_context(recipes: list[dict]) -> str:
    if not recipes:
        return "No safe retrieved recipe context was available."

    formatted_blocks: list[str] = []
    for index, recipe in enumerate(recipes, start=1):
        ingredients = ", ".join(recipe.get("ingredients", []))
        tags = ", ".join(recipe.get("tags", []))
        key_steps = " | ".join(recipe.get("steps", [])[:3])
        formatted_blocks.append(
            "\n".join(
                [
                    f"Retrieved Recipe {index}",
                    f"Title: {recipe.get('title', '')}",
                    f"Ingredients: {ingredients}",
                    f"Tags: {tags}",
                    f"Summary: {recipe.get('instruction_summary', '')}",
                    f"Key Steps: {key_steps}",
                ]
            )
        )

    return "\n\n".join(formatted_blocks)


def _remove_conflicting_ingredients(
    ingredients: list[str],
    conflicting_ingredients: list[str],
) -> list[str]:
    conflict_lookup = {ingredient.strip().lower() for ingredient in conflicting_ingredients}
    return [
        ingredient
        for ingredient in ingredients
        if ingredient.strip().lower() not in conflict_lookup
    ]


def _find_output_restriction_violations(
    recipe_json: dict,
    restrictions: dict[str, set[str]],
) -> list[str]:
    text_blocks = [recipe_json.get("title", "")]
    text_blocks.extend(recipe_json.get("ingredients", []))
    searchable_text = " || ".join(item.strip().lower() for item in text_blocks if isinstance(item, str))

    violations: list[str] = []
    for restriction_name, keywords in restrictions.items():
        matched_keywords = sorted(keyword for keyword in keywords if keyword in searchable_text)
        if matched_keywords:
            violations.append(f"{restriction_name}: {', '.join(matched_keywords[:5])}")

    return violations


def _build_recipe_prompt(
    request: RecipeRequest,
    context_block: str,
) -> str:
    restriction_notes = []
    restrictions = get_generation_restrictions(request.allergies, request.preferences)
    for restriction_name, keywords in restrictions.items():
        label = restriction_name.replace("preference:", "")
        keyword_list = ", ".join(sorted(keywords))
        restriction_notes.append(f"- Avoid these {label} keyword(s) in the final title and ingredient list: {keyword_list}")

    restriction_block = "\n".join(restriction_notes) if restriction_notes else "- No extra keyword restrictions"

    return f"""
You are generating a new recipe for an AI cookbook application.

User ingredients: {", ".join(request.ingredients)}.
Dietary preferences: {", ".join(request.preferences) if request.preferences else "none"}.
Allergies to avoid: {", ".join(request.allergies) if request.allergies else "none"}.

Retrieved recipe context:
{context_block}

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
- Use the retrieved recipes only as grounding context
- Synthesize a new recipe instead of copying a retrieved recipe verbatim
- If no safe retrieved context is available, still generate a safe recipe from the user input alone
Additional safety restrictions:
{restriction_block}
""".strip()


def generate_structured_recipe(request: RecipeRequest) -> RecipeResponse:
    allergy_conflicts = find_conflicting_ingredients(
        request.ingredients,
        request.allergies,
    )
    preference_conflicts = find_preference_conflicting_ingredients(
        request.ingredients,
        request.preferences,
    )
    conflicting_ingredients = list(
        dict.fromkeys(
            allergy_conflicts
            + [
                ingredient
                for ingredients in preference_conflicts.values()
                for ingredient in ingredients
            ]
        )
    )
    safe_ingredients = _remove_conflicting_ingredients(
        request.ingredients,
        conflicting_ingredients,
    )
    warnings: list[str] = []

    if allergy_conflicts:
        warnings.append(
            "Some provided ingredients conflict with your allergy settings and were excluded: "
            + ", ".join(allergy_conflicts)
        )

    for preference, ingredients in preference_conflicts.items():
        warnings.append(
            f"Some provided ingredients conflict with your '{preference}' preference and were excluded: "
            + ", ".join(ingredients)
        )

    if not safe_ingredients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All provided ingredients conflict with the selected allergies or dietary preferences. Please remove the conflicting ingredients or update the selected constraints.",
        )

    safe_request = RecipeRequest(
        ingredients=safe_ingredients,
        preferences=request.preferences,
        allergies=request.allergies,
    )

    retrieved_context = retrieve_recipe_context(safe_request)
    context_block = _format_retrieved_context(retrieved_context)
    prompt = _build_recipe_prompt(safe_request, context_block)
    restrictions = get_generation_restrictions(
        safe_request.allergies,
        safe_request.preferences,
    )

    client = _get_client()

    try:
        last_violations: list[str] = []
        for _ in range(2):
            response = client.responses.create(model=settings.openai_model, input=prompt)
            recipe_text = _strip_code_fences(response.output_text)
            recipe_json = json.loads(recipe_text)
            last_violations = _find_output_restriction_violations(recipe_json, restrictions)
            if not last_violations:
                recipe_json["warnings"] = warnings
                return RecipeResponse.model_validate(recipe_json)
            prompt += (
                "\n\nThe previous output violated these restrictions and must be corrected: "
                + "; ".join(last_violations)
                + ". Regenerate the recipe and avoid those restricted terms."
            )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recipe generation failed because the generated recipe violated dietary or allergy restrictions.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recipe generation failed because the AI response was invalid.",
        ) from exc
