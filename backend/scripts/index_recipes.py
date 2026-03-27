import json
from pathlib import Path

from backend.config import settings
from backend.services.embedding_service import create_embeddings
from backend.services.vector_store_service import (
    build_recipe_document,
    build_recipe_metadata,
    get_collection,
)


def load_recipe_corpus(corpus_path: Path) -> list[dict]:
    with corpus_path.open("r", encoding="utf-8") as corpus_file:
        data = json.load(corpus_file)
    return data if isinstance(data, list) else []


def index_recipe_corpus() -> None:
    corpus_path = Path(settings.recipe_corpus_path)
    recipes = load_recipe_corpus(corpus_path)
    collection = get_collection()
    existing = collection.get(include=[])
    existing_ids = existing.get("ids", [])
    if existing_ids:
        collection.delete(ids=existing_ids)

    batch_size = settings.embedding_batch_size

    for start in range(0, len(recipes), batch_size):
        batch = recipes[start : start + batch_size]
        documents = [build_recipe_document(recipe) for recipe in batch]
        embeddings = create_embeddings(documents)
        ids = [str(recipe["recipe_id"]) for recipe in batch]
        metadatas = [build_recipe_metadata(recipe) for recipe in batch]

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(
            f"Indexed recipes {start + 1}-{start + len(batch)} "
            f"of {len(recipes)}"
        )


if __name__ == "__main__":
    index_recipe_corpus()
