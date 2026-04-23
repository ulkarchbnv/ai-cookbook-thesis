import pytest
from fastapi import HTTPException


def test_get_ocr_provider_returns_google_vision_provider(monkeypatch):
    from backend.services import ocr_provider

    ocr_provider.get_ocr_provider.cache_clear()
    monkeypatch.setattr(ocr_provider.settings, "ocr_provider", "google_vision")

    provider = ocr_provider.get_ocr_provider()

    assert isinstance(provider, ocr_provider.GoogleVisionOcrProvider)


def test_get_ocr_provider_rejects_unknown_provider(monkeypatch):
    from backend.services import ocr_provider

    ocr_provider.get_ocr_provider.cache_clear()
    monkeypatch.setattr(ocr_provider.settings, "ocr_provider", "unknown_provider")

    with pytest.raises(HTTPException) as exc_info:
        ocr_provider.get_ocr_provider()

    assert exc_info.value.status_code == 503
    assert "Unsupported OCR provider" in exc_info.value.detail


def test_get_recipe_image_provider_returns_openai_provider():
    from backend.services import recipe_image_provider

    class FakeProvider:
        pass

    original_provider = recipe_image_provider.OpenAIRecipeImageProvider
    recipe_image_provider.OpenAIRecipeImageProvider = FakeProvider
    try:
        provider = recipe_image_provider.get_recipe_image_provider()
    finally:
        recipe_image_provider.OpenAIRecipeImageProvider = original_provider

    assert isinstance(provider, FakeProvider)
