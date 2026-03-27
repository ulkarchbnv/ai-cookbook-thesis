import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status

from backend.config import settings


def _get_chroma_module():
    try:
        import chromadb
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ChromaDB is not installed.",
        ) from exc

    return chromadb


def get_collection():
    chromadb = _get_chroma_module()
    persist_directory = Path(settings.chroma_persist_directory)
    persist_directory.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(persist_directory))
    return client.get_or_create_collection(name=settings.chroma_collection_name)


def build_recipe_document(recipe: dict[str, Any]) -> str:
    ingredients = ", ".join(recipe.get("ingredients", []))
    tags = ", ".join(recipe.get("tags", []))
    summary = recipe.get("instruction_summary", "")

    return "\n".join(
        [
            f"Title: {recipe.get('title', '')}",
            f"Ingredients: {ingredients}",
            f"Tags: {tags}",
            f"Summary: {summary}",
        ]
    )


def build_recipe_metadata(recipe: dict[str, Any]) -> dict[str, str | int | float | bool]:
    return {
        "recipe_id": str(recipe.get("recipe_id", "")),
        "title": recipe.get("title", ""),
        "ingredients_json": json.dumps(recipe.get("ingredients", [])),
        "tags_json": json.dumps(recipe.get("tags", [])),
        "steps_json": json.dumps(recipe.get("steps", [])),
        "instruction_summary": recipe.get("instruction_summary", ""),
        "source": recipe.get("source", ""),
    }

