"""
Chat API Router for Swali-AI

LEARNING NOTE: The Chat Endpoint
=================================
This is the main user-facing API for asking questions.

Flow:
    POST /api/chat/ → RAG Generator → Answer + Sources

The frontend will call this endpoint when users ask questions.
"""

import asyncio

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import Literal

from app.auth import get_optional_user
from app.services.cache_rate_limit import get_cache_rate_limiter
from app.storage import get_store
from app.rag.generator import RAGGenerator


# Create router
router = APIRouter(prefix="/api/chat", tags=["chat"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ChatRequest(BaseModel):
    """Request to ask a question."""
    message: str
    hint_level: int = 0  # 0 = full answer, 1-3 = progressive hints
    problem_context: str | None = None  # Required when hint_level > 0
    topic: str | None = None
    company: str | None = None
    difficulty: str | None = None
    session_id: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "How do I solve the Two Sum problem?",
                "hint_level": 0
            }
        }


class Source(BaseModel):
    """A source document used to generate the answer."""
    id: str
    title: str
    type: str | None = None
    difficulty: str | None = None
    pattern: str | None = None


class ChatResponse(BaseModel):
    """Response containing the answer and sources."""
    answer: str
    sources: list[Source]
    citations: list[dict] = []
    query_variants: list[str] = []
    tokens_used: int
    model: str


class HintRequest(BaseModel):
    """Request for a hint on a specific problem."""
    problem_title: str
    hint_level: int = 1  # 1 = subtle, 2 = medium, 3 = detailed
    student_attempt: str = ""  # What has the student tried?
    
    class Config:
        json_schema_extra = {
            "example": {
                "problem_title": "Two Sum",
                "hint_level": 1,
                "student_attempt": "I tried using two nested loops but it's too slow"
            }
        }


class FollowupRequest(BaseModel):
    """Request for follow-up interview questions."""
    problem_title: str
    solution_approach: str

    class Config:
        json_schema_extra = {
            "example": {
                "problem_title": "Two Sum",
                "solution_approach": "I used a HashMap to track complements."
            }
        }


class FollowupResponse(BaseModel):
    """Response containing follow-up questions and sources."""
    questions: str
    sources: list[Source]
    tokens_used: int
    model: str


class PracticeRequest(BaseModel):
    """Request for practice question generation."""
    mode: Literal["general", "job_aligned"] = "general"
    focus_area: str = ""
    job_description: str = ""
    question_count: int = 8


class PracticeResponse(BaseModel):
    """Practice question response payload."""
    questions: str
    sources: list[Source]
    tokens_used: int
    model: str


# =============================================================================
# Generator Instance
# =============================================================================

_generator: RAGGenerator | None = None


def get_generator() -> RAGGenerator:
    """Get or create the RAG generator."""
    global _generator
    if _generator is None:
        _generator = RAGGenerator()
    return _generator


def _build_where_filter(request: ChatRequest) -> dict | None:
    where: dict[str, str] = {}
    if request.topic:
        where["topic"] = request.topic
    if request.company:
        where["company"] = request.company
    if request.difficulty:
        where["difficulty"] = request.difficulty
    return where or None


def _source_list(raw_sources: list[dict]) -> list[Source]:
    return [
        Source(
            id=s["id"],
            title=s["title"],
            type=s.get("type"),
            difficulty=s.get("difficulty"),
            pattern=s.get("pattern"),
        )
        for s in raw_sources
    ]


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict | None = Depends(get_optional_user),
    authorization: str | None = Header(default=None),
) -> ChatResponse:
    """
    Ask a coding or system design question.
    
    LEARNING NOTE: The Main RAG Endpoint
    
    This endpoint:
    1. Takes a natural language question
    2. Retrieves relevant problems/concepts from ChromaDB
    3. Sends question + context to the LLM (Gemini)
    4. Returns the answer with sources
    
    Examples:
    - "How do I find duplicates in an array?"
    - "Explain the sliding window technique"
    - "How would you design Twitter?"
    """
    try:
        generator = get_generator()
        cache_service = get_cache_rate_limiter()

        user_key = current_user["id"] if current_user else (authorization or "anonymous")
        allowed, remaining = await cache_service.check_rate_limit(user_key)
        if not allowed:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please retry shortly.")

        cache_key = request.model_dump_json()
        cached = await cache_service.get_cached("chat", cache_key)
        if cached:
            return ChatResponse(**cached)
        
    # LEARNING NOTE: Hint routing
    # We only generate hints when the client passes BOTH:
    # - hint_level > 0
    # - problem_context (the specific problem title)
    # Otherwise, we fall back to a full RAG answer.
        if request.hint_level > 0:
            if not request.problem_context:
                raise HTTPException(
                    status_code=400,
                    detail="problem_context is required when hint_level > 0"
                )

            # If hint_level > 0 and we have problem context, generate hints
            response = await asyncio.to_thread(
                generator.generate_hints,
                problem_title=request.problem_context,
                hint_level=request.hint_level,
                student_attempt=request.message
            )
        else:
            # Generate full answer
            response = await generator.generate_answer_async(
                question=request.message,
                n_context=3,
                where=_build_where_filter(request),
            )

        chat_response = ChatResponse(
            answer=response.answer,
            sources=_source_list(response.sources),
            citations=response.citations,
            query_variants=response.query_variants,
            tokens_used=response.tokens_used,
            model=response.model
        )

        if current_user and request.session_id:
            store = get_store()
            await asyncio.to_thread(store.append_message, request.session_id, "user", request.message)
            await asyncio.to_thread(store.append_message, request.session_id, "assistant", chat_response.answer)

        await cache_service.set_cached("chat", cache_key, chat_response.model_dump(), ttl_seconds=180)
        return chat_response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )


@router.post("/hint", response_model=ChatResponse)
async def get_hint(request: HintRequest) -> ChatResponse:
    """
    Get a progressive hint for a specific problem.
    
    LEARNING NOTE: Progressive Hints
    
    Good tutors don't give away answers immediately.
    This endpoint provides hints at 3 levels:
    
    - Level 1: "Have you considered using a data structure for O(1) lookup?"
    - Level 2: "Try using a HashMap to store seen values"
    - Level 3: "Here's the approach: iterate through array, for each num..."
    """
    try:
        generator = get_generator()
        
        response = await asyncio.to_thread(
            generator.generate_hints,
            problem_title=request.problem_title,
            hint_level=request.hint_level,
            student_attempt=request.student_attempt
        )

        return ChatResponse(
            answer=response.answer,
            sources=_source_list(response.sources),
            citations=response.citations,
            query_variants=response.query_variants,
            tokens_used=response.tokens_used,
            model=response.model
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate hint: {str(e)}"
        )


@router.post("/followup", response_model=FollowupResponse)
async def get_followup_questions(request: FollowupRequest) -> FollowupResponse:
    """
    Generate follow-up questions after a solution.

    LEARNING NOTE: Interview follow-ups
    These questions probe depth of understanding, not just correctness.
    They test optimization, edge cases, and related patterns.
    """
    try:
        generator = get_generator()

        response = await asyncio.to_thread(
            generator.generate_followup_questions,
            request.problem_title,
            request.solution_approach,
        )

        return FollowupResponse(
            questions=response.answer,
            sources=[
                Source(
                    id=s["id"],
                    title=s["title"],
                    type=s.get("type"),
                    difficulty=s.get("difficulty"),
                    pattern=s.get("pattern")
                )
                for s in response.sources
            ],
            tokens_used=response.tokens_used,
            model=response.model
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate follow-up questions: {str(e)}"
        )


@router.post("/practice", response_model=PracticeResponse)
async def get_practice_questions(request: PracticeRequest) -> PracticeResponse:
    """Generate either general or job-aligned practice question sets."""
    try:
        generator = get_generator()

        if request.mode == "job_aligned" and not request.job_description.strip():
            raise HTTPException(
                status_code=400,
                detail="job_description is required when mode='job_aligned'",
            )

        response = await asyncio.to_thread(
            generator.generate_practice_questions,
            request.job_description,
            request.focus_area,
            request.question_count,
        )

        return PracticeResponse(
            questions=response.answer,
            sources=[
                Source(
                    id=s["id"],
                    title=s["title"],
                    type=s.get("type"),
                    difficulty=s.get("difficulty"),
                    pattern=s.get("pattern"),
                )
                for s in response.sources
            ],
            tokens_used=response.tokens_used,
            model=response.model,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate practice questions: {str(e)}",
        )
