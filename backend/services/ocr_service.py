import json

from fastapi import HTTPException, UploadFile, status
from openai import OpenAI

from backend.config import settings
from backend.schemas import NutritionLabelData, OcrExtractionResponse
from backend.services.ocr_google_vision_provider import extract_text_with_google_vision
from backend.services.ocr_image_processing import (
    prepare_image_for_ocr,
    validate_image_file,
    validate_image_size,
)


def _structure_nutrition_text(raw_text: str) -> NutritionLabelData:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured.",
        )

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
{raw_text}
""".strip()

    client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.responses.create(model=settings.openai_model, input=prompt)
        structured_text = (
            response.output_text.strip()
            .removeprefix("```json")
            .removesuffix("```")
            .strip()
        )
        return NutritionLabelData.model_validate(json.loads(structured_text))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to convert OCR text into structured nutrition data.",
        ) from exc


async def extract_nutrition_label(file: UploadFile) -> OcrExtractionResponse:
    if settings.ocr_provider != "google_vision":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unsupported OCR provider: {settings.ocr_provider}",
        )

    validate_image_file(file)
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    validate_image_size(file_bytes)
    prepared_image = prepare_image_for_ocr(file_bytes)
    raw_text = extract_text_with_google_vision(prepared_image)
    structured_nutrition = _structure_nutrition_text(raw_text)

    return OcrExtractionResponse(
        raw_text=raw_text,
        structured_nutrition=structured_nutrition,
    )
