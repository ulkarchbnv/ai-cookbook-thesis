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
    normalized_blocks = [item.strip().lower() for item in text_blocks if isinstance(item, str)]

    violations: list[str] = []
    for restriction_name, keywords in restrictions.items():
        matched_keywords = sorted(
            keyword for keyword in keywords
            if any(
                re.search(rf"\b{re.escape(keyword)}\b", block)
                for block in normalized_blocks
            )
        )
        if matched_keywords:
            violations.append(f"{restriction_name}: {', '.join(matched_keywords[:5])}")

    return violations


PANTRY_STAPLES: frozenset[str] = frozenset({
    "salt", "pepper", "black pepper", "white pepper", "oil", "olive oil",
    "vegetable oil", "cooking oil", "water", "sugar", "flour", "baking powder",
    "baking soda", "vinegar", "soy sauce", "cornstarch",
})


def _is_pantry_staple(ingredient: str) -> bool:
    normalized = " ".join(ingredient.strip().lower().split())
    return any(staple in normalized for staple in PANTRY_STAPLES)


def _find_ingredient_drift(
    recipe_json: dict,
    allowed_ingredients: list[str],
) -> list[str]:
    """Return generated ingredients that are not in the allowed set and not pantry staples."""
    allowed_normalized = {" ".join(i.strip().lower().split()) for i in allowed_ingredients}
    drift: list[str] = []
    for ingredient in recipe_json.get("ingredients", []):
        if not isinstance(ingredient, str):
            continue
        normalized = " ".join(ingredient.strip().lower().split())
        if normalized in allowed_normalized:
            continue
        if _is_pantry_staple(ingredient):
            continue
        if any(allowed.split()[0] in normalized for allowed in allowed_normalized if allowed):
            continue
        drift.append(ingredient)
    return drift


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
    ingredient_list = ", ".join(request.ingredients)

    return f"""
You are generating a new recipe for an AI cookbook application.

User ingredients: {ingredient_list}.
Dietary preferences: {", ".join(request.preferences) if request.preferences else "none"}.
Allergies to avoid: {", ".join(request.allergies) if request.allergies else "none"}.

Retrieved recipe context (use only as structural inspiration, do NOT copy ingredients):
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

STRICT INGREDIENT CONSTRAINT (highest priority):
- The "ingredients" array MUST contain ONLY ingredients from this list: {ingredient_list}
- The ONLY permitted additions are essential pantry staples: salt, pepper, oil, water, sugar, flour, baking powder, vinegar, soy sauce, cornstarch
- You MUST NOT add any other ingredient not in the user's list or the pantry staples above
- Do not add vegetables, proteins, sauces, spices, or any food item not already listed by the user
- If the user's ingredients are limited, work with what is available and simplify the recipe accordingly

Additional rules:
- Do not return markdown
- Do not return explanation text
- Respect dietary preferences and allergies
- Keep the recipe practical for a home cook
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
        messages: list[dict] = [{"role": "user", "content": prompt}]

        for _ in range(2):
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.7,
            )
            recipe_text = _strip_code_fences(
                response.choices[0].message.content or ""
            )
            recipe_json = json.loads(recipe_text)
            last_violations = _find_output_restriction_violations(recipe_json, restrictions)
            drift_violations = _find_ingredient_drift(recipe_json, safe_ingredients)

            all_violations = last_violations[:]
            if drift_violations:
                all_violations.append(
                    "ingredient-drift: these ingredients were not provided by the user and are not pantry staples: "
                    + ", ".join(drift_violations[:8])
                )

            if not all_violations:
                recipe_json["warnings"] = warnings
                return RecipeResponse.model_validate(recipe_json)

            violation_note = (
                "The previous output violated these rules and must be corrected: "
                + "; ".join(all_violations)
                + ". Regenerate the recipe strictly using only the user-provided ingredients "
                + f"({', '.join(safe_ingredients)}) plus allowed pantry staples, and avoid restricted terms."
            )
            messages.append({"role": "assistant", "content": recipe_text})
            messages.append({"role": "user", "content": violation_note})

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
