from concurrent.futures import ThreadPoolExecutor
from time import perf_counter


def _mock_recipe_response():
    return {
        "title": "Fast Tomato Pasta",
        "ingredients": ["200g pasta", "2 tomatoes", "fresh basil"],
        "additional_ingredients": [],
        "preferences": ["vegetarian"],
        "allergies": ["peanut"],
        "steps": ["Boil pasta", "Cook sauce", "Serve"],
        "nutrition_estimate": {
            "calories": 410,
            "protein": "15g",
            "carbs": "58g",
            "fat": "11g",
        },
        "warnings": [],
    }


def test_generate_recipe_remains_fast_and_stable_with_mocked_dependencies(client, auth_headers, monkeypatch):
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
            "image_cache_key": "thumb-fast",
            "image_prompt": "mock prompt",
        },
    )

    durations = []
    responses = []

    for _ in range(5):
        start = perf_counter()
        response = client.post(
            "/generate-recipe",
            headers=auth_headers(),
            json={
                "ingredients": ["pasta", "tomato", "basil"],
                "preferences": ["vegetarian"],
                "allergies": ["peanut"],
            },
        )
        durations.append(perf_counter() - start)
        responses.append(response)

    assert all(response.status_code == 200 for response in responses)
    assert max(durations) < 0.5
    assert sum(durations) / len(durations) < 0.25


def test_generate_recipe_handles_small_concurrent_burst_with_mocked_dependencies(client, auth_headers, monkeypatch):
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
            "image_cache_key": "thumb-fast",
            "image_prompt": "mock prompt",
        },
    )

    headers = auth_headers()

    def send_request():
        return client.post(
            "/generate-recipe",
            headers=headers,
            json={
                "ingredients": ["pasta", "tomato", "basil"],
                "preferences": ["vegetarian"],
                "allergies": ["peanut"],
            },
        )

    start = perf_counter()
    with ThreadPoolExecutor(max_workers=5) as executor:
        responses = list(executor.map(lambda _: send_request(), range(5)))
    duration = perf_counter() - start

    assert all(response.status_code == 200 for response in responses)
    assert all(response.json()["title"] == "Fast Tomato Pasta" for response in responses)
    assert duration < 1.5
