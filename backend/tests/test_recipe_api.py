from types import SimpleNamespace


def _mock_recipe_response():
    return {
        "title": "Tomato Basil Pasta",
        "ingredients": ["200g pasta", "2 tomatoes", "fresh basil"],
        "additional_ingredients": ["olive oil"],
        "preferences": ["vegetarian"],
        "allergies": ["peanut"],
        "steps": ["Boil pasta", "Cook tomatoes", "Mix and serve"],
        "nutrition_estimate": {
            "calories": 420,
            "protein": "14g",
            "carbs": "61g",
            "fat": "12g",
        },
        "warnings": ["This recipe suggests a few extra ingredients you may need: olive oil"],
    }


def test_generate_recipe_as_guest_returns_recipe_without_persistence(client, monkeypatch):
    from backend.routes import recipes as recipe_routes
    from backend.schemas import RecipeResponse

    monkeypatch.setattr(
        recipe_routes,
        "generate_structured_recipe",
        lambda request: RecipeResponse.model_validate(_mock_recipe_response()),
    )
    monkeypatch.setattr(
        recipe_routes,
        "ensure_recipe_thumbnail",
        lambda **kwargs: {
            "image_url": "/media/recipe_thumbnails/mock.png",
            "image_path": "backend/media/recipe_thumbnails/mock.png",
            "image_cache_key": "thumb-123",
            "image_prompt": "mock prompt",
        },
    )

    response = client.post(
        "/generate-recipe",
        json={
            "ingredients": ["pasta", "tomato", "basil"],
            "preferences": ["vegetarian"],
            "allergies": ["peanut"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["generated_recipe_id"] is None
    assert payload["image_url"] == "/media/recipe_thumbnails/mock.png"
    assert payload["image_cache_key"] == "thumb-123"
    assert payload["title"] == "Tomato Basil Pasta"


def test_generate_recipe_as_authenticated_user_persists_history(client, auth_headers, monkeypatch):
    from backend.routes import recipes as recipe_routes
    from backend.schemas import RecipeResponse

    monkeypatch.setattr(
        recipe_routes,
        "generate_structured_recipe",
        lambda request: RecipeResponse.model_validate(_mock_recipe_response()),
    )
    monkeypatch.setattr(
        recipe_routes,
        "ensure_recipe_thumbnail",
        lambda **kwargs: {
            "image_url": "/media/recipe_thumbnails/mock.png",
            "image_path": "backend/media/recipe_thumbnails/mock.png",
            "image_cache_key": "thumb-123",
            "image_prompt": "mock prompt",
        },
    )

    generate_response = client.post(
        "/generate-recipe",
        headers=auth_headers(),
        json={
            "ingredients": ["pasta", "tomato", "basil"],
            "preferences": ["vegetarian"],
            "allergies": ["peanut"],
        },
    )

    assert generate_response.status_code == 200
    generated_payload = generate_response.json()
    assert generated_payload["generated_recipe_id"] is not None

    history_response = client.get("/recipes/history", headers=auth_headers())

    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["total"] == 1
    assert history_payload["items"][0]["id"] == generated_payload["generated_recipe_id"]
    assert history_payload["items"][0]["title"] == "Tomato Basil Pasta"
    assert history_payload["items"][0]["is_saved"] is False
    assert history_payload["items"][0]["image_cache_key"] == "thumb-123"


def test_generate_recipe_adds_warning_when_thumbnail_generation_fails(client, auth_headers, monkeypatch):
    from fastapi import HTTPException
    from backend.routes import recipes as recipe_routes
    from backend.schemas import RecipeResponse

    monkeypatch.setattr(
        recipe_routes,
        "generate_structured_recipe",
        lambda request: RecipeResponse.model_validate(_mock_recipe_response()),
    )

    def _raise_thumbnail_error(**kwargs):
        raise HTTPException(status_code=502, detail="Image generation failed.")

    monkeypatch.setattr(recipe_routes, "ensure_recipe_thumbnail", _raise_thumbnail_error)

    response = client.post(
        "/generate-recipe",
        headers=auth_headers(),
        json={
            "ingredients": ["pasta", "tomato", "basil"],
            "preferences": ["vegetarian"],
            "allergies": ["peanut"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["image_url"] is None
    assert payload["image_cache_key"] is None
    assert any("thumbnail" in warning.lower() for warning in payload["warnings"])


def test_save_recipe_marks_generated_recipe_as_saved(client, auth_headers, monkeypatch):
    from backend.routes import recipes as recipe_routes
    from backend.schemas import RecipeResponse

    monkeypatch.setattr(
        recipe_routes,
        "generate_structured_recipe",
        lambda request: RecipeResponse.model_validate(_mock_recipe_response()),
    )
    monkeypatch.setattr(
        recipe_routes,
        "ensure_recipe_thumbnail",
        lambda **kwargs: {
            "image_url": "/media/recipe_thumbnails/mock.png",
            "image_path": "backend/media/recipe_thumbnails/mock.png",
            "image_cache_key": "thumb-123",
            "image_prompt": "mock prompt",
        },
    )

    generate_response = client.post(
        "/generate-recipe",
        headers=auth_headers(),
        json={"ingredients": ["pasta", "tomato"], "preferences": [], "allergies": []},
    )
    generated_recipe_id = generate_response.json()["generated_recipe_id"]

    save_response = client.post(
        "/recipes",
        headers=auth_headers(),
        json={"generated_recipe_id": generated_recipe_id},
    )

    assert save_response.status_code == 201
    saved_payload = save_response.json()
    assert saved_payload["id"] == generated_recipe_id
    assert saved_payload["saved_at"] is not None

    list_response = client.get("/recipes", headers=auth_headers())
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["total"] == 1
    assert list_payload["items"][0]["id"] == generated_recipe_id


def test_save_recipe_rejects_missing_generated_recipe(client, auth_headers):
    response = client.post(
        "/recipes",
        headers=auth_headers(),
        json={"generated_recipe_id": 9999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Generated recipe not found."


def test_recipe_history_and_saved_recipes_are_scoped_to_current_user(client, auth_headers, monkeypatch):
    from backend.routes import recipes as recipe_routes
    from backend.schemas import RecipeResponse

    monkeypatch.setattr(
        recipe_routes,
        "generate_structured_recipe",
        lambda request: RecipeResponse.model_validate(_mock_recipe_response()),
    )
    monkeypatch.setattr(
        recipe_routes,
        "ensure_recipe_thumbnail",
        lambda **kwargs: {
            "image_url": "/media/recipe_thumbnails/mock.png",
            "image_path": "backend/media/recipe_thumbnails/mock.png",
            "image_cache_key": "thumb-123",
            "image_prompt": "mock prompt",
        },
    )

    first_user_headers = auth_headers()
    second_user_headers = auth_headers("second@example.com", "another-strong-password")

    first_generate = client.post(
        "/generate-recipe",
        headers=first_user_headers,
        json={"ingredients": ["pasta"], "preferences": [], "allergies": []},
    )
    first_recipe_id = first_generate.json()["generated_recipe_id"]
    client.post("/recipes", headers=first_user_headers, json={"generated_recipe_id": first_recipe_id})

    second_history = client.get("/recipes/history", headers=second_user_headers)
    second_saved = client.get("/recipes", headers=second_user_headers)

    assert second_history.status_code == 200
    assert second_history.json()["total"] == 0
    assert second_saved.status_code == 200
    assert second_saved.json()["total"] == 0
