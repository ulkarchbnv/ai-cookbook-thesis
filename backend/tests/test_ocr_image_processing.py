from io import BytesIO

import pytest
from fastapi import UploadFile
from PIL import Image

from backend.services.ocr_image_processing import (
    prepare_image_for_ocr,
    validate_image_file,
    validate_image_size,
)


def _make_png_bytes(width: int = 40, height: int = 20, color: str = "white") -> bytes:
    image = Image.new("RGB", (width, height), color=color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_validate_image_file_accepts_image_content_type():
    upload = UploadFile(filename="label.png", file=BytesIO(b"data"), headers={"content-type": "image/png"})

    validate_image_file(upload)


def test_validate_image_file_rejects_non_image_content_type():
    upload = UploadFile(filename="notes.txt", file=BytesIO(b"data"), headers={"content-type": "text/plain"})

    with pytest.raises(Exception) as exc_info:
        validate_image_file(upload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Please upload an image file."


def test_validate_image_size_rejects_oversized_payload(monkeypatch):
    monkeypatch.setattr("backend.services.ocr_image_processing.settings.max_ocr_upload_bytes", 3)

    with pytest.raises(Exception) as exc_info:
        validate_image_size(b"1234")

    assert exc_info.value.status_code == 413
    assert exc_info.value.detail == "The uploaded image is too large."


def test_prepare_image_for_ocr_returns_non_empty_png_bytes():
    prepared_bytes = prepare_image_for_ocr(_make_png_bytes())

    assert isinstance(prepared_bytes, bytes)
    assert prepared_bytes.startswith(b"\x89PNG")
    assert len(prepared_bytes) > 0


def test_prepare_image_for_ocr_rejects_invalid_image_bytes():
    with pytest.raises(Exception) as exc_info:
        prepare_image_for_ocr(b"not-a-real-image")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "The uploaded file could not be read as an image."
