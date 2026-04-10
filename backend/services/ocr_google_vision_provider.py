from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException, status
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import vision
from google.oauth2 import service_account

from backend.config import settings


@lru_cache(maxsize=1)
def get_google_vision_client() -> vision.ImageAnnotatorClient:
    credentials_path = settings.google_application_credentials

    try:
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                Path(credentials_path)
            )
            return vision.ImageAnnotatorClient(credentials=credentials)

        return vision.ImageAnnotatorClient()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GOOGLE_APPLICATION_CREDENTIALS points to a missing file.",
        ) from exc
    except DefaultCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Google Vision credentials are not configured. "
                "Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON file."
            ),
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to initialize the Google Vision client.",
        ) from exc


def extract_text_with_google_vision(image_bytes: bytes) -> str:
    client = get_google_vision_client()
    image = vision.Image(content=image_bytes)

    try:
        response = client.document_text_detection(image=image)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google Vision OCR failed to process the image.",
        ) from exc

    if response.error.message:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Vision OCR failed: {response.error.message}",
        )

    raw_text = response.full_text_annotation.text.strip()
    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text was detected in the uploaded image.",
        )

    return raw_text
