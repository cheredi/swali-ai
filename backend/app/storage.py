"""Persistence layer for auth, sessions, learning progress, and submissions."""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from app.config import settings


def _utcnow_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


class SQLiteStore:
    """Small SQLite-backed storage service for product features."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.app_db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    metadata TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                );

                CREATE TABLE IF NOT EXISTS spaced_repetition (
                    user_id TEXT NOT NULL,
                    problem_id TEXT NOT NULL,
                    quality INTEGER NOT NULL,
                    repetitions INTEGER NOT NULL,
                    interval_days INTEGER NOT NULL,
                    ease_factor REAL NOT NULL,
                    due_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(user_id, problem_id)
                );

                CREATE TABLE IF NOT EXISTS answer_grades (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    problem_title TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    grading_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS content_submissions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT,
                    status TEXT NOT NULL,
                    reviewer_note TEXT,
                    created_at TEXT NOT NULL,
                    reviewed_at TEXT
                );
                """
            )

    def create_user(self, email: str, password_hash: str) -> dict[str, Any]:
        user_id = str(uuid.uuid4())
        created_at = _utcnow_iso()
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO users(id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (user_id, email.lower(), password_hash, created_at),
            )
        return {"id": user_id, "email": email.lower(), "created_at": created_at}

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
                (email.lower(),),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT id, email, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def create_session(self, user_id: str, mode: str, metadata: str = "") -> dict[str, Any]:
        session_id = str(uuid.uuid4())
        started_at = _utcnow_iso()
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO sessions(id, user_id, mode, started_at, metadata) VALUES (?, ?, ?, ?, ?)",
                (session_id, user_id, mode, started_at, metadata),
            )
        return {"id": session_id, "user_id": user_id, "mode": mode, "started_at": started_at}

    def append_message(self, session_id: str, role: str, content: str) -> dict[str, Any]:
        message_id = str(uuid.uuid4())
        created_at = _utcnow_iso()
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO chat_messages(id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (message_id, session_id, role, content, created_at),
            )
        return {
            "id": message_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": created_at,
        }

    def get_session_history(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def upsert_spaced_repetition(
        self,
        user_id: str,
        problem_id: str,
        quality: int,
        repetitions: int,
        interval_days: int,
        ease_factor: float,
        due_at: str,
    ) -> None:
        updated_at = _utcnow_iso()
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO spaced_repetition(
                    user_id, problem_id, quality, repetitions, interval_days, ease_factor, due_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, problem_id) DO UPDATE SET
                    quality=excluded.quality,
                    repetitions=excluded.repetitions,
                    interval_days=excluded.interval_days,
                    ease_factor=excluded.ease_factor,
                    due_at=excluded.due_at,
                    updated_at=excluded.updated_at
                """,
                (
                    user_id,
                    problem_id,
                    quality,
                    repetitions,
                    interval_days,
                    ease_factor,
                    due_at,
                    updated_at,
                ),
            )

    def get_spaced_repetition(self, user_id: str, problem_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT user_id, problem_id, quality, repetitions, interval_days, ease_factor, due_at, updated_at
                FROM spaced_repetition
                WHERE user_id = ? AND problem_id = ?
                """,
                (user_id, problem_id),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def list_due_reviews(self, user_id: str, now_iso: str) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT user_id, problem_id, quality, repetitions, interval_days, ease_factor, due_at, updated_at
                FROM spaced_repetition
                WHERE user_id = ? AND due_at <= ?
                ORDER BY due_at ASC
                """,
                (user_id, now_iso),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_grade(self, user_id: str | None, problem_title: str, answer: str, grading_json: str) -> str:
        grade_id = str(uuid.uuid4())
        created_at = _utcnow_iso()
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO answer_grades(id, user_id, problem_title, answer, grading_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (grade_id, user_id, problem_title, answer, grading_json, created_at),
            )
        return grade_id

    def create_submission(self, user_id: str, title: str, content: str, metadata_json: str) -> dict[str, Any]:
        submission_id = str(uuid.uuid4())
        created_at = _utcnow_iso()
        status = "pending"
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO content_submissions(id, user_id, title, content, metadata_json, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (submission_id, user_id, title, content, metadata_json, status, created_at),
            )
        return {
            "id": submission_id,
            "user_id": user_id,
            "title": title,
            "status": status,
            "created_at": created_at,
        }

    def update_submission_review(self, submission_id: str, status: str, reviewer_note: str) -> bool:
        reviewed_at = _utcnow_iso()
        with self.connection() as conn:
            cursor = conn.execute(
                """
                UPDATE content_submissions
                SET status = ?, reviewer_note = ?, reviewed_at = ?
                WHERE id = ?
                """,
                (status, reviewer_note, reviewed_at, submission_id),
            )
        return cursor.rowcount > 0

    def list_submissions(self, status: str | None = None) -> list[dict[str, Any]]:
        with self.connection() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM content_submissions WHERE status = ? ORDER BY created_at DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM content_submissions ORDER BY created_at DESC"
                ).fetchall()
        return [dict(row) for row in rows]


_store: SQLiteStore | None = None


def get_store() -> SQLiteStore:
    global _store
    if _store is None:
        _store = SQLiteStore()
    return _store
