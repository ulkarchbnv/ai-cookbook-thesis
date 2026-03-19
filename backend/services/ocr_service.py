import json
from io import BytesIO

from fastapi import HTTPException, UploadFile, status
from openai import OpenAI
from PIL import Image, ImageOps
import pytesseract

from backend.config import settings
from backend.schemas import NutritionLabelData, OcrExtractionResponse


def _validate_image_file(file: UploadFile) -> None:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload an image file.",
        )


def _prepare_image_for_ocr(file_bytes: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(file_bytes))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file could not be read as an image.",
        ) from exc

    grayscale = ImageOps.grayscale(image)
    contrast_ready = ImageOps.autocontrast(grayscale)
    enlarged = contrast_ready.resize(
        (contrast_ready.width * 2, contrast_ready.height * 2)
    )
    return enlarged


def _extract_text_with_tesseract(file_bytes: bytes) -> str:
    if not settings.tesseract_cmd:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tesseract path is not configured.",
        )

    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    image = _prepare_image_for_ocr(file_bytes)

    try:
        raw_text = pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Tesseract executable was not found. Check TESSERACT_CMD.",
        ) from exc
    except pytesseract.TesseractError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Tesseract OCR failed to process the image.",
        )

    cleaned_text = raw_text.strip()
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text was detected in the uploaded image.",
        )

    return cleaned_text


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
        structured_text = response.output_text.strip().removeprefix("```json").removesuffix("```").strip()
        return NutritionLabelData.model_validate(json.loads(structured_text))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to convert OCR text into structured nutrition data.",
        ) from exc


async def extract_nutrition_label(file: UploadFile) -> OcrExtractionResponse:
    _validate_image_file(file)
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    raw_text = _extract_text_with_tesseract(file_bytes)
    structured_nutrition = _structure_nutrition_text(raw_text)

    return OcrExtractionResponse(
        raw_text=raw_text,
        structured_nutrition=structured_nutrition,
    )
