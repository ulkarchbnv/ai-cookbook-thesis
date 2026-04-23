from abc import ABC, abstractmethod
from functools import lru_cache

from fastapi import HTTPException, status

from backend.config import settings
from backend.services.ocr_google_vision_provider import extract_text_with_google_vision


class OcrProvider(ABC):
    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> str:
        """Extract raw OCR text from an image payload."""


class GoogleVisionOcrProvider(OcrProvider):
    def extract_text(self, image_bytes: bytes) -> str:
        return extract_text_with_google_vision(image_bytes)


@lru_cache(maxsize=1)
def get_ocr_provider() -> OcrProvider:
    if settings.ocr_provider == "google_vision":
        return GoogleVisionOcrProvider()

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Unsupported OCR provider: {settings.ocr_provider}",
    )
