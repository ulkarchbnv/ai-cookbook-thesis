import hashlib
import json
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from openai import OpenAI
import re
from backend.config import settings
from backend.schemas import NutritionLabelData, OcrExtractionResponse
from backend.services.ocr_google_vision_provider import extract_text_with_google_vision
from backend.services.ocr_image_processing import (
    prepare_image_for_ocr,
    validate_image_file,
    validate_image_size,
)

_ALLOWED_OCR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def _save_ocr_upload(file_bytes: bytes, original_filename: str) -> dict[str, str]:
    content_hash = hashlib.sha256(file_bytes).hexdigest()[:24]
    raw_ext = Path(original_filename).suffix.lower()
    ext = raw_ext if raw_ext in _ALLOWED_OCR_EXTENSIONS else ".jpg"
    stored_filename = f"{content_hash}{ext}"

    upload_dir = Path(settings.ocr_upload_directory)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / stored_filename
    if not file_path.exists():
        file_path.write_bytes(file_bytes)

    return {
        "image_path": str(file_path.as_posix()),
        "image_url": f"/media/ocr_uploads/{stored_filename}",
    }

def _strip_nutrition_fences(raw_text: str) -> str:
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


_MAX_OCR_TEXT_CHARS = 2000


def _sanitize_ocr_text(raw_text: str) -> str:
    """Truncate and strip control characters from OCR output before prompt injection."""
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", raw_text)
    return sanitized[:_MAX_OCR_TEXT_CHARS]


def _structure_nutrition_text(raw_text: str) -> NutritionLabelData:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured.",
        )

    safe_text = _sanitize_ocr_text(raw_text)

    prompt = f"""
You are given OCR text from a food nutrition label.
Extract only the nutrition information you can confidently identify.

Return only valid JSON in this exact structure:
{{
  "product_name": "string or null",
  "serving_size": "string or null",
  "calories": 0,
  "protein_g": 0,
  "carbs_g": 0,
  "fat_g": 0,
  "sugar_g": 0,
  "sodium_mg": 0,
  "fiber_g": 0
}}

Rules:
- Use null when a value is missing or unclear
- Keep units out of numeric fields
- Do not guess values that are not visible in the OCR text
- Return only JSON

OCR text:
{safe_text}
""".strip()

    client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        structured_text = _strip_nutrition_fences(
            response.choices[0].message.content or ""
        )
        return NutritionLabelData.model_validate(json.loads(structured_text))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to convert OCR text into structured nutrition data.",
        ) from exc


def extract_nutrition_label(file: UploadFile) -> OcrExtractionResponse:
    if settings.ocr_provider != "google_vision":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unsupported OCR provider: {settings.ocr_provider}",
        )

    validate_image_file(file)
    file_bytes = file.file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    validate_image_size(file_bytes)

    image_fields: dict[str, str | None] = {"image_path": None, "image_url": None}
    try:
        image_fields = _save_ocr_upload(file_bytes, file.filename or "upload.jpg")
    except Exception:
        pass

    prepared_image = prepare_image_for_ocr(file_bytes)
    raw_text = extract_text_with_google_vision(prepared_image)
    structured_nutrition = _structure_nutrition_text(raw_text)

    return OcrExtractionResponse(
        raw_text=raw_text,
        structured_nutrition=structured_nutrition,
        image_url=image_fields["image_url"],
        image_path=image_fields["image_path"],
    )
