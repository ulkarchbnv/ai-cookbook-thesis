def test_root_endpoint_returns_status_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "AI Cookbook backend is running"}


def test_protected_profile_requires_authentication(client):
    response = client.get("/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_saved_recipes_requires_authentication(client):
    response = client.get("/recipes")

    assert response.status_code == 401


def test_recipe_history_requires_authentication(client):
    response = client.get("/recipes/history")

    assert response.status_code == 401


def test_ocr_history_requires_authentication(client):
    response = client.get("/ocr/history")

    assert response.status_code == 401
