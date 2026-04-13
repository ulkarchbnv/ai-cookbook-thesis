import json

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import OcrExtraction, User
from backend.schemas import (
    OcrExtractionResponse,
    SavedOcrExtractionCreate,
    SavedOcrExtractionResponse,
)
from backend.services.ocr_service import extract_nutrition_label
from backend.utils import load_serialized_value


router = APIRouter(prefix="/ocr", tags=["ocr"])

def _ocr_extraction_to_response(extraction: OcrExtraction) -> SavedOcrExtractionResponse:
    return SavedOcrExtractionResponse(
        id=extraction.id,
        source_filename=extraction.source_filename,
        raw_text=extraction.raw_text,
        structured_nutrition=load_serialized_value(extraction.structured_nutrition, {}),
        created_at=extraction.created_at,
    )


@router.get("/status")
def get_ocr_status():
    return {
        "implemented": True,
        "message": "OCR upload and extraction endpoint is available.",
    }


@router.post("/extract", response_model=OcrExtractionResponse)
def extract_nutrition(
    file: UploadFile = File(...),
):
    return extract_nutrition_label(file)


@router.post("/save", response_model=SavedOcrExtractionResponse, status_code=status.HTTP_201_CREATED)
def save_ocr_extraction(
    extraction: SavedOcrExtractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedOcrExtractionResponse:
    db_extraction = OcrExtraction(
        source_filename=extraction.source_filename,
        raw_text=extraction.raw_text,
        structured_nutrition=json.dumps(extraction.structured_nutrition.model_dump()),
        user_id=current_user.id,
    )
    db.add(db_extraction)
    db.commit()
    db.refresh(db_extraction)
    return _ocr_extraction_to_response(db_extraction)


@router.get("/history", response_model=list[SavedOcrExtractionResponse])
def list_saved_ocr_extractions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SavedOcrExtractionResponse]:
    query = (
        db.query(OcrExtraction)
        .filter(OcrExtraction.user_id == current_user.id)
        .order_by(OcrExtraction.created_at.desc())
        .all()
    )

    return [_ocr_extraction_to_response(extraction) for extraction in query]
