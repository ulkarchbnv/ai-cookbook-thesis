from fastapi import APIRouter, File, UploadFile

from backend.schemas import OcrExtractionResponse
from backend.services.ocr_service import extract_nutrition_label


router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.get("/status")
def get_ocr_status():
    return {
        "implemented": True,
        "message": "OCR upload and extraction endpoint is available.",
    }


@router.post("/extract", response_model=OcrExtractionResponse)
async def extract_nutrition(file: UploadFile = File(...)):
    return await extract_nutrition_label(file)
