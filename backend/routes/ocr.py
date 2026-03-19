from fastapi import APIRouter

from backend.services.ocr_service import ocr_not_implemented


router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.get("/status")
def get_ocr_status():
    return {"implemented": False, "message": "OCR is planned but not implemented yet."}


@router.post("/extract")
def extract_nutrition_label():
    ocr_not_implemented()
