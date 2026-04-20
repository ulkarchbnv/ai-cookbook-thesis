import json
from typing import Any
import re
from backend.config import settings
from backend.schemas import RecipeRequest
from backend.services.embedding_service import create_embeddings
from backend.services.vector_store_service import get_collection


ALLERGY_ALIASES: dict[str, set[str]] = {
    "milk": {"milk", "dairy", "cheese", "butter", "cream", "yogurt", "milk powder"},
    "dairy": {"milk", "dairy", "cheese", "butter", "cream", "yogurt", "milk powder"},
    "peanut": {"peanut", "peanuts", "peanut butter"},
    "egg": {"egg", "eggs", "mayonnaise"},
    "gluten": {"gluten", "wheat", "flour", "barley", "rye", "breadcrumbs"},
    "soy": {"soy", "soybean", "soy sauce", "tofu", "edamame", "miso"},
    "tree nut": {
        "tree nut",
        "almond",
        "walnut",
        "cashew",
        "pecan",
        "pistachio",
        "hazelnut",
    },
    "shellfish": {"shellfish", "shrimp", "prawn", "crab", "lobster", "clam", "mussel", "oyster", "oysters", "oyster sauce"},
    "seafood": {
        "seafood",
        "fish",
        "shellfish",
        "shrimp",
        "prawn",
        "crab",
        "lobster",
        "clam",
        "mussel",
        "salmon",
        "tuna",
        "cod",
    },
}

PREFERENCE_CONFLICT_KEYWORDS: dict[str, set[str]] = {
    "halal": {"pork", "bacon", "ham", "prosciutto", "pancetta", "lard"},
    "kosher": {
        "pork",
        "bacon",
        "ham",
        "prosciutto",
        "pancetta",
        "lard",
        "shellfish",
        "shrimp",
        "prawn",
        "crab",
        "lobster",
        "clam",
        "mussel",
    },
    "vegetarian": {
        "chicken",
        "beef",
        "pork",
        "bacon",
        "ham",
        "fish",
        "seafood",
        "shrimp",
        "prawn",
        "crab",
        "lobster",
        "gelatin",
    },
    "vegan": {
        "chicken",
        "beef",
        "pork",
        "bacon",
        "ham",
        "fish",
        "seafood",
        "shrimp",
        "prawn",
        "crab",
        "lobster",
        "gelatin",
        "milk",
        "dairy",
        "cheese",
        "butter",
        "cream",
        "yogurt",
        "egg",
        "eggs",
        "honey",
    },
}


def _normalize_keyword(value: str) -> str:
    return " ".join(value.strip().lower().split())


def build_retrieval_query(request: RecipeRequest) -> str:
    ingredients_text = ", ".join(request.ingredients)
    preferences_text = ", ".join(request.preferences) if request.preferences else "none"
    return (
        f"Ingredients: {ingredients_text}\n"
        f"Preferred dietary attributes: {preferences_text}"
    )


def _load_json_list(raw_value: str) -> list[str]:
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    return value if isinstance(value, list) else []


def _expand_allergy_keywords(allergies: list[str]) -> set[str]:
    expanded: set[str] = set()
    for allergy in allergies:
        normalized = _normalize_keyword(allergy)
        if not normalized:
            continue
        expanded.add(normalized)
        expanded.update(ALLERGY_ALIASES.get(normalized, set()))
    return expanded


def get_preference_conflict_keywords(preferences: list[str]) -> dict[str, set[str]]:
    expanded: dict[str, set[str]] = {}
    for preference in preferences:
        normalized_preference = _normalize_keyword(preference)
        keywords = PREFERENCE_CONFLICT_KEYWORDS.get(normalized_preference, set())
        if keywords:
            expanded[normalized_preference] = keywords
    return expanded


def _matches_any_keyword(text: str, keywords: set[str]) -> bool:
    normalized_text = _normalize_keyword(text)
    return any(
        re.search(rf"\b{re.escape(keyword)}\b", normalized_text)
        for keyword in keywords
    )


def find_conflicting_ingredients(ingredients: list[str], allergies: list[str]) -> list[str]:
    if not ingredients or not allergies:
        return []

    allergy_keywords = _expand_allergy_keywords(allergies)
    conflicts: list[str] = []

    for ingredient in ingredients:
        if _matches_any_keyword(ingredient, allergy_keywords):
            conflicts.append(ingredient)

    return conflicts


def find_preference_conflicting_ingredients(
    ingredients: list[str],
    preferences: list[str],
) -> dict[str, list[str]]:
    if not ingredients or not preferences:
        return {}

    conflicts: dict[str, list[str]] = {}

    for preference in preferences:
        normalized_preference = _normalize_keyword(preference)
        preference_keywords = get_preference_conflict_keywords([normalized_preference]).get(
            normalized_preference,
            set(),
        )
        if not preference_keywords:
            continue

        matched_ingredients = [
            ingredient
            for ingredient in ingredients
            if _matches_any_keyword(ingredient, preference_keywords)
        ]
        if matched_ingredients:
            conflicts[normalized_preference] = matched_ingredients

    return conflicts


def get_generation_restrictions(
    allergies: list[str],
    preferences: list[str],
) -> dict[str, set[str]]:
    restrictions: dict[str, set[str]] = {}
    allergy_keywords = _expand_allergy_keywords(allergies)
    if allergy_keywords:
        restrictions["allergies"] = allergy_keywords

    preference_keywords = get_preference_conflict_keywords(preferences)
    for preference, keywords in preference_keywords.items():
        restrictions[f"preference:{preference}"] = keywords

    return restrictions


def _has_allergy_conflict(recipe: dict[str, Any], allergies: list[str]) -> bool:
    if not allergies:
        return False

    haystacks = recipe.get("ingredients", []) + recipe.get("tags", [])
    allergy_keywords = _expand_allergy_keywords(allergies)
    return any(_matches_any_keyword(item, allergy_keywords) for item in haystacks)


def _count_preference_matches(recipe: dict[str, Any], preferences: list[str]) -> int:
    if not preferences:
        return 0

    tags = [_normalize_keyword(tag) for tag in recipe.get("tags", [])]
    match_count = 0

    for preference in preferences:
        keyword = _normalize_keyword(preference)
        if keyword and any(keyword in tag for tag in tags):
            match_count += 1

    return match_count


def _distance_to_similarity(distance: float | int | None) -> float:
    if distance is None:
        return 0.0
    return 1.0 / (1.0 + float(distance))


def _build_recipe_candidate(
    metadata: dict[str, Any],
    distance: float | int | None,
    preferences: list[str],
) -> dict[str, Any]:
    recipe = {
        "recipe_id": metadata.get("recipe_id", ""),
        "title": metadata.get("title", ""),
        "ingredients": _load_json_list(metadata.get("ingredients_json", "[]")),
        "tags": _load_json_list(metadata.get("tags_json", "[]")),
        "steps": _load_json_list(metadata.get("steps_json", "[]")),
        "instruction_summary": metadata.get("instruction_summary", ""),
        "source": metadata.get("source", ""),
    }
    semantic_score = _distance_to_similarity(distance)
    preference_matches = _count_preference_matches(recipe, preferences)
    recipe["semantic_score"] = semantic_score
    recipe["preference_matches"] = preference_matches
    recipe["ranking_score"] = semantic_score + (0.05 * preference_matches)
    return recipe


def retrieve_recipe_context(request: RecipeRequest) -> list[dict[str, Any]]:
    collection = get_collection()
    if collection.count() == 0:
        return []

    query_text = build_retrieval_query(request)
    query_embedding = create_embeddings([query_text])[0]
    response = collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.rag_candidate_count,
        include=["metadatas", "distances"],
    )

    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]

    candidates: list[dict[str, Any]] = []
    for metadata, distance in zip(metadatas, distances):
        if not metadata:
            continue
        candidate = _build_recipe_candidate(metadata, distance, request.preferences)
        if _has_allergy_conflict(candidate, request.allergies):
            continue
        candidates.append(candidate)

    candidates.sort(key=lambda item: item["ranking_score"], reverse=True)
    return candidates[: settings.rag_context_count]
