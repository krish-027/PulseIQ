from fastapi import APIRouter, HTTPException

from backend.models.search_models import (
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from backend.services.retriever_service import get_retriever_service


router = APIRouter(
    prefix="/api/search",
    tags=["Search"],
)


def _cosine_similarity_from_squared_l2(distance: float) -> float:
    """Convert normalized-vector squared L2 distance to cosine similarity."""

    # The embedding service normalizes every vector before FAISS indexes it.
    # For normalized vectors: squared_l2 = 2 - (2 * cosine_similarity).
    similarity = 1.0 - (float(distance) / 2.0)
    return max(-1.0, min(1.0, similarity))


@router.get("/status")
def search_status():
    return {
        "message": "Search route is ready",
    }


@router.post(
    "",
    response_model=SearchResponse,
)
def search_feedback(
    request: SearchRequest,
):
    try:
        retriever_service = get_retriever_service()

        documents_with_scores = (
            retriever_service.similarity_search_with_score(
                query=request.query,
                k=request.k,
            )
        )

        results = []

        for document, score in documents_with_scores:
            metadata = document.metadata

            results.append(
                SearchResult(
                    feedback_id=metadata["feedback_id"],
                    filename=metadata["filename"],
                    category=metadata["category"],
                    split=metadata["split"],
                    feedback=document.page_content.strip(),
                    similarity=_cosine_similarity_from_squared_l2(score),
                    score=float(score),
                )
            )

        return SearchResponse(
            query=request.query,
            results=results,
            result_count=len(results),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Feedback search failed: {str(exc)}",
        ) from exc
