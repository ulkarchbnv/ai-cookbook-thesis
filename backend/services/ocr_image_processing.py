from io import BytesIO

from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError

from backend.config import settings


def validate_image_file(file: UploadFile) -> None:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload an image file.",
        )


def validate_image_size(file_bytes: bytes) -> None:
    if len(file_bytes) > settings.max_ocr_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded image is too large.",
        )


def prepare_image_for_ocr(file_bytes: bytes) -> bytes:
    try:
        Image.MAX_IMAGE_PIXELS = settings.max_ocr_image_pixels
        image = Image.open(BytesIO(file_bytes))
        image.load()
    except Image.DecompressionBombError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded image is too large to process safely.",
        ) from exc
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file could not be read as an image.",
        ) from exc

    if image.width * image.height > settings.max_ocr_image_pixels:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded image dimensions are too large.",
        )

    normalized = ImageOps.exif_transpose(image)
    grayscale = ImageOps.grayscale(normalized)
    contrast_ready = ImageOps.autocontrast(grayscale)
    enlarged = contrast_ready.resize(
        (contrast_ready.width * 2, contrast_ready.height * 2)
    )

    buffer = BytesIO()
    enlarged.save(buffer, format="PNG")
    return buffer.getvalue()
