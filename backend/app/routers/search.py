"""
Search API Router for Swali-AI

🎓 LEARNING NOTE: API Design for RAG
=====================================
This router exposes our vector search capability via REST API.

The flow:
    User Query → API → EmbeddingService → VectorStore → Results
    
Why an API layer?
1. Separates frontend from backend
2. Easy to test with curl/Postman
3. Can add authentication, rate limiting, caching later
4. Frontend doesn't need to know about embeddings
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.vectorstore import VectorStore

# Create router with prefix
router = APIRouter(prefix="/api/search", tags=["search"])


# =============================================================================
# Response Models
# =============================================================================

class SearchResult(BaseModel):
    """
    A single search result.
    
    🎓 LEARNING NOTE: Response Models
    Using Pydantic models for API responses gives us:
    - Automatic JSON serialization
    - Type validation
    - OpenAPI documentation
    - IDE autocomplete on frontend
    """
    id: str
    title: str
    score: float  # Similarity score (higher = more similar)
    type: str     # "coding_problem", "concept", or "design_question"
    difficulty: str | None = None
    pattern: str | None = None
    source: str | None = None


class SearchResponse(BaseModel):
    """Response containing search results."""
    query: str
    results: list[SearchResult]
    total: int


# =============================================================================
# Endpoints
# =============================================================================

# Initialize vector store (shared across requests)
_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """
    Get or create the vector store instance.
    
    🎓 LEARNING NOTE: Lazy Initialization
    We don't create the vector store until first use.
    This prevents errors if ChromaDB isn't available at startup.
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore("problems")
    return _vector_store


@router.get("/", response_model=SearchResponse)
async def search_problems(
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(5, description="Maximum results to return", ge=1, le=20),
    type_filter: str | None = Query(
        None, 
        description="Filter by type: coding_problem, concept, or design_question"
    ),
    difficulty: str | None = Query(
        None,
        description="Filter by difficulty: easy, medium, or hard"
    )
) -> SearchResponse:
    """
    Search for problems by semantic meaning.
    
    🎓 LEARNING NOTE: Semantic Search Endpoint
    
    This is the magic! Unlike traditional search:
    - "find pair summing to target" → finds "Two Sum"
    - "last in first out data structure" → finds Stack problems
    - "how to scale a website" → finds Scalability concept
    
    The embedding model understands MEANING, not just keywords.
    
    Examples:
    - GET /api/search/?q=how do I find duplicates in an array
    - GET /api/search/?q=design a social media feed&type_filter=design_question
    - GET /api/search/?q=tree traversal&difficulty=easy&limit=10
    """
    try:
        vector_store = get_vector_store()
        
        # Build metadata filter
        where: dict | None = None
        if type_filter or difficulty:
            where = {}
            if type_filter:
                where["type"] = type_filter
            if difficulty:
                where["difficulty"] = difficulty
        
        # Perform semantic search
        results = vector_store.search(
            query=q,
            n_results=limit,
            where=where
        )
        
        # Convert to response format
        search_results = []
        for doc_id, metadata, distance in zip(
            results["ids"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            # Convert distance to similarity score
            # Distance is L2 distance, so lower is better
            # We convert to a score where higher is better
            score = 1 - distance  # Simplified scoring
            
            search_results.append(SearchResult(
                id=doc_id,
                title=metadata.get("title", "Unknown"),
                score=round(score, 3),
                type=metadata.get("type", "unknown"),
                difficulty=metadata.get("difficulty"),
                pattern=metadata.get("pattern_name") or metadata.get("pattern"),
                source=metadata.get("source")
            ))
        
        return SearchResponse(
            query=q,
            results=search_results,
            total=len(search_results)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/stats")
async def get_stats() -> dict:
    """
    Get vector store statistics.
    
    Useful for debugging and monitoring.
    """
    try:
        vector_store = get_vector_store()
        return {
            "total_documents": vector_store.count(),
            "collection_name": "problems",
            "status": "ready"
        }
    except Exception as e:
        return {
            "total_documents": 0,
            "collection_name": "problems",
            "status": f"error: {str(e)}"
        }
