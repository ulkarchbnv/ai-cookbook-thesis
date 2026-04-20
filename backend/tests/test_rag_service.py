from backend.schemas import RecipeRequest
from backend.services.rag_service import (
    _build_recipe_candidate,
    build_retrieval_query,
    find_conflicting_ingredients,
    find_preference_conflicting_ingredients,
    get_generation_restrictions,
    retrieve_recipe_context,
)


def test_build_retrieval_query_includes_ingredients_and_preferences():
    request = RecipeRequest(
        ingredients=["tomato", "basil"],
        preferences=["vegetarian"],
        allergies=[],
    )

    query = build_retrieval_query(request)

    assert "tomato, basil" in query
    assert "vegetarian" in query


def test_find_conflicting_ingredients_matches_allergy_aliases():
    conflicts = find_conflicting_ingredients(
        ["peanut butter", "tomato", "milk"],
        ["peanut", "dairy"],
    )

    assert conflicts == ["peanut butter", "milk"]


def test_find_preference_conflicting_ingredients_detects_non_vegan_items():
    conflicts = find_preference_conflicting_ingredients(
        ["chicken breast", "tofu", "egg noodles"],
        ["vegan"],
    )

    assert conflicts == {"vegan": ["chicken breast", "egg noodles"]}


def test_get_generation_restrictions_combines_allergies_and_preferences():
    restrictions = get_generation_restrictions(
        allergies=["peanut"],
        preferences=["vegetarian"],
    )

    assert "allergies" in restrictions
    assert "peanut" in restrictions["allergies"]
    assert "preference:vegetarian" in restrictions
    assert "chicken" in restrictions["preference:vegetarian"]


def test_build_recipe_candidate_combines_similarity_and_preference_score():
    candidate = _build_recipe_candidate(
        metadata={
            "recipe_id": "recipe-1",
            "title": "Tomato Pasta",
            "ingredients_json": '["tomato", "pasta"]',
            "tags_json": '["vegetarian", "quick"]',
            "steps_json": '["Boil", "Serve"]',
            "instruction_summary": "A quick tomato pasta.",
            "source": "dataset",
        },
        distance=0.25,
        preferences=["vegetarian"],
    )

    assert candidate["recipe_id"] == "recipe-1"
    assert candidate["semantic_score"] > 0
    assert candidate["preference_matches"] == 1
    assert candidate["ranking_score"] > candidate["semantic_score"]


def test_retrieve_recipe_context_filters_allergy_conflicts_and_sorts_by_rank(monkeypatch):
    class FakeCollection:
        def count(self):
            return 2

        def query(self, **kwargs):
            return {
                "metadatas": [[
                    {
                        "recipe_id": "safe-1",
                        "title": "Tomato Pasta",
                        "ingredients_json": '["tomato", "pasta"]',
                        "tags_json": '["vegetarian"]',
                        "steps_json": '["Boil", "Serve"]',
                        "instruction_summary": "Safe recipe.",
                        "source": "dataset",
                    },
                    {
                        "recipe_id": "unsafe-1",
                        "title": "Shrimp Pasta",
                        "ingredients_json": '["shrimp", "pasta"]',
                        "tags_json": '["seafood"]',
                        "steps_json": '["Boil", "Serve"]',
                        "instruction_summary": "Unsafe recipe.",
                        "source": "dataset",
                    },
                ]],
                "distances": [[0.2, 0.1]],
            }

    monkeypatch.setattr("backend.services.rag_service.get_collection", lambda: FakeCollection())
    monkeypatch.setattr("backend.services.rag_service.create_embeddings", lambda texts: [[0.1, 0.2, 0.3]])

    context = retrieve_recipe_context(
        RecipeRequest(
            ingredients=["tomato", "pasta"],
            preferences=["vegetarian"],
            allergies=["shellfish"],
        )
    )

    assert len(context) == 1
    assert context[0]["recipe_id"] == "safe-1"
    assert context[0]["title"] == "Tomato Pasta"
