from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.config import settings
from backend.schemas import RecipeRequest
from backend.services.embedding_service import create_embeddings
from backend.services.rag_service import (
    _has_allergy_conflict,
    _build_recipe_candidate,
    build_retrieval_query,
    get_generation_restrictions,
)
from backend.services.vector_store_service import get_collection


router = APIRouter(prefix="/rag", tags=["rag-debug"])


class VectorSearchResult(BaseModel):
    rank: int
    recipe_id: str
    title: str
    ingredients: list[str]
    tags: list[str]
    instruction_summary: str
    semantic_score: float
    preference_matches: int
    ranking_score: float
    allergy_conflict: bool
    selected_for_context: bool


class RagDebugResponse(BaseModel):
    query_text: str
    collection_size: int
    candidates_retrieved: int
    candidates_after_allergy_filter: int
    candidates_selected: int
    generation_restrictions: dict[str, list[str]]
    results: list[VectorSearchResult]


@router.post("/debug", response_model=RagDebugResponse)
def rag_debug(request: RecipeRequest) -> RagDebugResponse:
    """
    Debug endpoint that exposes the full RAG retrieval pipeline.
    Shows what the vector store retrieved, similarity scores, allergy
    filtering, and which recipes were ultimately selected as context.
    """
    collection = get_collection()
    collection_size = collection.count()

    if collection_size == 0:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The vector store is empty. Run the indexing script first.",
        )

    # Build the same query the real pipeline uses
    query_text = build_retrieval_query(request)
    query_embedding = create_embeddings([query_text])[0]

    # Fetch raw candidates from ChromaDB
    response = collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.rag_candidate_count,
        include=["metadatas", "distances"],
    )

    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]

    # Build candidates: same logic as the real pipeline
    all_candidates: list[dict] = []
    for metadata, distance in zip(metadatas, distances):
        if not metadata:
            continue
        candidate = _build_recipe_candidate(metadata, distance, request.preferences)
        candidate["allergy_conflict"] = _has_allergy_conflict(candidate, request.allergies)
        all_candidates.append(candidate)

    # Sort by ranking score descending
    all_candidates.sort(key=lambda c: c["ranking_score"], reverse=True)

    # Figure out which ones were actually selected (no allergy conflict, top N)
    selected_ids: set[str] = set()
    selected_count = 0
    for candidate in all_candidates:
        if candidate["allergy_conflict"]:
            continue
        if selected_count >= settings.rag_context_count:
            break
        selected_ids.add(candidate["recipe_id"])
        selected_count += 1

    # Get restriction keywords for display
    restrictions = get_generation_restrictions(request.allergies, request.preferences)
    restrictions_serializable = {
        key: sorted(values) for key, values in restrictions.items()
    }

    results = [
        VectorSearchResult(
            rank=index + 1,
            recipe_id=candidate["recipe_id"],
            title=candidate["title"],
            ingredients=candidate["ingredients"],
            tags=candidate["tags"],
            instruction_summary=candidate["instruction_summary"],
            semantic_score=round(candidate["semantic_score"], 4),
            preference_matches=candidate["preference_matches"],
            ranking_score=round(candidate["ranking_score"], 4),
            allergy_conflict=candidate["allergy_conflict"],
            selected_for_context=candidate["recipe_id"] in selected_ids,
        )
        for index, candidate in enumerate(all_candidates)
    ]

    candidates_after_filter = sum(1 for c in all_candidates if not c["allergy_conflict"])

    return RagDebugResponse(
        query_text=query_text,
        collection_size=collection_size,
        candidates_retrieved=len(all_candidates),
        candidates_after_allergy_filter=candidates_after_filter,
        candidates_selected=selected_count,
        generation_restrictions=restrictions_serializable,
        results=results,
    )


@router.get("/collection-stats")
def rag_collection_stats():
    """
    Returns basic stats about the vector store collection.
    Useful for verifying the index was built correctly.
    """
    collection = get_collection()
    count = collection.count()

    return {
        "collection_name": settings.chroma_collection_name,
        "total_documents": count,
        "embedding_model": settings.openai_embedding_model,
        "rag_candidate_count": settings.rag_candidate_count,
        "rag_context_count": settings.rag_context_count,
        "is_empty": count == 0,
    }