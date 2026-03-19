from fastapi import HTTPException, status


def ocr_not_implemented() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OCR processing is planned but not implemented yet.",
    )
