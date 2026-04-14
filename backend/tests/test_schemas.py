import pytest
from pydantic import ValidationError

from backend.schemas import RecipeRequest
from backend.utils import build_recipe_fingerprint


def test_recipe_request_trims_and_filters_blank_values():
    payload = RecipeRequest(
        ingredients=[" tomato  ", " ", "basil"],
        preferences=[" vegan ", ""],
        allergies=[" nuts "],
    )

    assert payload.ingredients == ["tomato", "basil"]
    assert payload.preferences == ["vegan"]
    assert payload.allergies == ["nuts"]


def test_recipe_request_rejects_more_than_ten_preferences():
    with pytest.raises(ValidationError):
        RecipeRequest(
            ingredients=["pasta"],
            preferences=[f"preference-{index}" for index in range(11)],
            allergies=[],
        )


def test_recipe_fingerprint_is_stable_for_whitespace_and_order_changes():
    first_fingerprint = build_recipe_fingerprint(
        title="Spicy Tomato Pasta",
        ingredients=["Tomato", "Basil", "Olive Oil"],
        preferences=["Vegetarian"],
        allergies=["Peanuts"],
        steps=["Boil pasta", "Mix sauce"],
    )
    second_fingerprint = build_recipe_fingerprint(
        title="  spicy   tomato pasta ",
        ingredients=["olive oil", " basil ", "tomato"],
        preferences=[" vegetarian "],
        allergies=["peanuts"],
        steps=["Boil pasta", "Mix sauce"],
    )

    assert first_fingerprint == second_fingerprint
