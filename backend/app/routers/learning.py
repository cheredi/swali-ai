"""Product features router: sessions, grading, mock interviews, spaced repetition, sandbox, and user content."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.rag.generator import RAGGenerator
from app.services.sandbox import get_sandbox
from app.services.scheduler import SM2State, next_sm2_state
from app.storage import get_store

router = APIRouter(prefix="/api/learning", tags=["learning"])

_generator: RAGGenerator | None = None


def get_generator() -> RAGGenerator:
    global _generator
    if _generator is None:
        _generator = RAGGenerator()
    return _generator


class SessionCreateRequest(BaseModel):
    mode: str = Field(default="practice", description="practice|mock_interview|review")
    metadata: dict = Field(default_factory=dict)


class SessionMessageRequest(BaseModel):
    session_id: str
    role: str
    content: str


class ReviewRecordRequest(BaseModel):
    problem_id: str
    quality: int = Field(ge=0, le=5)


class GradeRequest(BaseModel):
    problem_title: str
    answer: str
    expected_time_complexity: str = ""
    expected_space_complexity: str = ""


class MockInterviewRequest(BaseModel):
    question: str
    answer: str
    duration_minutes: int = 35


class SandboxRequest(BaseModel):
    language: str = "python"
    version: str = "3.10.0"
    code: str
    stdin: str = ""


class SubmissionRequest(BaseModel):
    title: str
    content: str
    metadata: dict = Field(default_factory=dict)


class ReviewSubmissionRequest(BaseModel):
    submission_id: str
    status: str = Field(pattern="^(approved|rejected)$")
    reviewer_note: str = ""


@router.post("/sessions")
async def create_session(request: SessionCreateRequest, current_user: dict = Depends(get_current_user)) -> dict:
    store = get_store()
    session = await asyncio.to_thread(
        store.create_session,
        current_user["id"],
        request.mode,
        json.dumps(request.metadata),
    )
    return session


@router.post("/sessions/message")
async def add_session_message(request: SessionMessageRequest, current_user: dict = Depends(get_current_user)) -> dict:
    store = get_store()
    message = await asyncio.to_thread(store.append_message, request.session_id, request.role, request.content)
    return message


@router.get("/sessions/{session_id}/history")
async def get_history(session_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    store = get_store()
    history = await asyncio.to_thread(store.get_session_history, session_id, 100)
    return {"session_id": session_id, "messages": history}


@router.post("/spaced-repetition/review")
async def review_problem(request: ReviewRecordRequest, current_user: dict = Depends(get_current_user)) -> dict:
    store = get_store()
    previous = await asyncio.to_thread(store.get_spaced_repetition, current_user["id"], request.problem_id)

    prev_state = None
    if previous:
        prev_state = SM2State(
            repetitions=int(previous["repetitions"]),
            interval_days=int(previous["interval_days"]),
            ease_factor=float(previous["ease_factor"]),
        )

    state, due_at = next_sm2_state(prev_state, request.quality)
    due_at_iso = due_at.isoformat(timespec="seconds")
    await asyncio.to_thread(
        store.upsert_spaced_repetition,
        current_user["id"],
        request.problem_id,
        request.quality,
        state.repetitions,
        state.interval_days,
        state.ease_factor,
        due_at_iso,
    )

    return {
        "problem_id": request.problem_id,
        "quality": request.quality,
        "repetitions": state.repetitions,
        "interval_days": state.interval_days,
        "ease_factor": round(state.ease_factor, 3),
        "due_at": due_at_iso,
    }


@router.get("/spaced-repetition/due")
async def due_reviews(current_user: dict = Depends(get_current_user)) -> dict:
    store = get_store()
    now_iso = datetime.utcnow().isoformat(timespec="seconds")
    due = await asyncio.to_thread(store.list_due_reviews, current_user["id"], now_iso)
    return {"due_count": len(due), "items": due}


@router.post("/grade")
async def grade_answer(request: GradeRequest, current_user: dict = Depends(get_current_user)) -> dict:
    generator = get_generator()
    grading = await generator.grade_answer_async(
        problem_title=request.problem_title,
        answer=request.answer,
        expected_time_complexity=request.expected_time_complexity,
        expected_space_complexity=request.expected_space_complexity,
    )
    store = get_store()
    grade_id = await asyncio.to_thread(
        store.save_grade,
        current_user["id"],
        request.problem_title,
        request.answer,
        json.dumps(grading),
    )
    return {"grade_id": grade_id, "grading": grading}


@router.post("/mock-interview")
async def mock_interview(request: MockInterviewRequest, current_user: dict = Depends(get_current_user)) -> dict:
    generator = get_generator()
    grading = await generator.grade_answer_async(
        problem_title=request.question,
        answer=request.answer,
        expected_time_complexity="",
        expected_space_complexity="",
        mode="mock_interview",
    )
    grading["duration_minutes"] = request.duration_minutes
    grading["hints_allowed"] = False
    return grading


@router.post("/sandbox/execute")
async def execute_code(request: SandboxRequest, current_user: dict = Depends(get_current_user)) -> dict:
    sandbox = get_sandbox()
    try:
        result = await sandbox.execute(
            language=request.language,
            version=request.version,
            code=request.code,
            stdin=request.stdin,
        )
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Sandbox execution failed: {error}") from error
    return result


@router.post("/content/submit")
async def submit_content(request: SubmissionRequest, current_user: dict = Depends(get_current_user)) -> dict:
    store = get_store()
    created = await asyncio.to_thread(
        store.create_submission,
        current_user["id"],
        request.title,
        request.content,
        json.dumps(request.metadata),
    )
    return created


@router.get("/content/submissions")
async def list_submissions(status: str | None = None, current_user: dict = Depends(get_current_user)) -> dict:
    store = get_store()
    records = await asyncio.to_thread(store.list_submissions, status)
    return {"total": len(records), "records": records}


@router.post("/content/review")
async def review_submission(request: ReviewSubmissionRequest, current_user: dict = Depends(get_current_user)) -> dict:
    store = get_store()
    updated = await asyncio.to_thread(
        store.update_submission_review,
        request.submission_id,
        request.status,
        request.reviewer_note,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"submission_id": request.submission_id, "status": request.status}
