def test_extract_nutrition_endpoint_returns_mocked_structured_response(client, monkeypatch):
    from backend.routes import ocr as ocr_routes
    from backend.schemas import NutritionLabelData, OcrExtractionResponse

    monkeypatch.setattr(
        ocr_routes,
        "extract_nutrition_label",
        lambda file: OcrExtractionResponse(
            raw_text="Calories 120\nProtein 5g",
            structured_nutrition=NutritionLabelData(
                product_name="Test Yogurt",
                serving_size="100g",
                calories=120,
                protein_g=5,
                carbs_g=10,
                fat_g=2,
                sugar_g=8,
                sodium_mg=90,
                fiber_g=0,
            ),
            image_url="/media/ocr_uploads/mock.png",
            image_path="backend/media/ocr_uploads/mock.png",
        ),
    )

    response = client.post(
        "/ocr/extract",
        files={"file": ("label.png", b"fake-image-content", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["raw_text"] == "Calories 120\nProtein 5g"
    assert payload["structured_nutrition"]["product_name"] == "Test Yogurt"
    assert payload["structured_nutrition"]["calories"] == 120
    assert payload["image_url"] == "/media/ocr_uploads/mock.png"


def test_save_ocr_extraction_persists_and_appears_in_history(client, auth_headers):
    response = client.post(
        "/ocr/save",
        headers=auth_headers(),
        json={
            "source_filename": "label.png",
            "raw_text": "Calories 250",
            "structured_nutrition": {
                "product_name": "Protein Bar",
                "serving_size": "1 bar",
                "calories": 250,
                "protein_g": 20,
                "carbs_g": 18,
                "fat_g": 8,
                "sugar_g": 6,
                "sodium_mg": 140,
                "fiber_g": 4,
            },
            "image_url": "/media/ocr_uploads/label.png",
            "image_path": "backend/media/ocr_uploads/label.png",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["source_filename"] == "label.png"
    assert payload["structured_nutrition"]["product_name"] == "Protein Bar"

    history_response = client.get("/ocr/history", headers=auth_headers())

    assert history_response.status_code == 200
    history_payload = history_response.json()
    assert history_payload["total"] == 1
    assert history_payload["items"][0]["source_filename"] == "label.png"
    assert history_payload["items"][0]["structured_nutrition"]["calories"] == 250


def test_ocr_history_is_scoped_to_current_user(client, auth_headers):
    first_user_headers = auth_headers()
    second_user_headers = auth_headers("second@example.com", "another-strong-password")

    client.post(
        "/ocr/save",
        headers=first_user_headers,
        json={
            "source_filename": "label.png",
            "raw_text": "Calories 250",
            "structured_nutrition": {
                "product_name": "Protein Bar",
                "serving_size": "1 bar",
                "calories": 250,
                "protein_g": 20,
                "carbs_g": 18,
                "fat_g": 8,
                "sugar_g": 6,
                "sodium_mg": 140,
                "fiber_g": 4,
            },
            "image_url": "/media/ocr_uploads/label.png",
            "image_path": "backend/media/ocr_uploads/label.png",
        },
    )

    second_history = client.get("/ocr/history", headers=second_user_headers)

    assert second_history.status_code == 200
    assert second_history.json()["total"] == 0
