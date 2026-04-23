import base64
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from openai import OpenAI

from backend.config import settings


class RecipeImageProvider(ABC):
    @abstractmethod
    def generate_png(self, prompt: str) -> bytes:
        """Generate a PNG image for the given prompt."""


class OpenAIRecipeImageProvider(RecipeImageProvider):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OPENAI_API_KEY is not configured.",
            )
        self._client = OpenAI(api_key=settings.openai_api_key)

    def generate_png(self, prompt: str) -> bytes:
        try:
            response = self._client.images.generate(
                model=settings.openai_image_model,
                prompt=prompt,
                size="1024x1024",
                quality="low",
                output_format="png",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Recipe image generation failed.",
            ) from exc

        image_data = response.data[0].b64_json if response.data else None
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Recipe image generation returned no image data.",
            )

        return base64.b64decode(image_data)


def get_recipe_image_provider() -> RecipeImageProvider:
    return OpenAIRecipeImageProvider()
