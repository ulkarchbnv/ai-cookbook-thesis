from fastapi import HTTPException, status
from openai import OpenAI

from backend.config import settings


def _get_client() -> OpenAI:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured.",
        )
    return OpenAI(api_key=settings.openai_api_key)


def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = _get_client()

    try:
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding generation failed.",
        ) from exc

    return [item.embedding for item in response.data]
