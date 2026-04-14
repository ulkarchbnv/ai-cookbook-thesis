import json
import math

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import OcrExtraction, User
from backend.schemas import (
    OcrExtractionResponse,
    PaginatedResponse,
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
        image_url=extraction.image_url,
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
        image_path=extraction.image_path,
        image_url=extraction.image_url,
        user_id=current_user.id,
    )
    db.add(db_extraction)
    db.commit()
    db.refresh(db_extraction)
    return _ocr_extraction_to_response(db_extraction)


@router.get("/history", response_model=PaginatedResponse[SavedOcrExtractionResponse])
def list_saved_ocr_extractions(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[SavedOcrExtractionResponse]:
    base_query = db.query(OcrExtraction).filter(OcrExtraction.user_id == current_user.id)
    total = base_query.count()
    rows = (
        base_query
        .order_by(OcrExtraction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[_ocr_extraction_to_response(e) for e in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )
