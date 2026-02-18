"""
Normalization Layer for AI/ML interview data.

LEARNING NOTE: Why normalize?
-----------------------------
Different sources format content differently. Normalization creates a stable
schema for downstream embedding, filtering, and evaluation.
"""

from __future__ import annotations

import re
import hashlib
from typing import Any


def normalize_question_text(text: str) -> str:
    """Normalize question text while preserving meaning."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = re.sub(r"\s*👶|\s*⭐️|\s*⭐|\s*🚀", "", cleaned)
    return cleaned.strip()


def infer_difficulty(question_text: str) -> str:
    """
    Infer difficulty from emoji markers used in many interview repos.

    LEARNING NOTE: Heuristic labels
    --------------------------------
    Heuristics are useful when source data is weakly structured. We keep this
    conservative and default to "medium" when uncertain.
    """
    if "🚀" in question_text:
        return "hard"
    if "⭐" in question_text:
        return "medium"
    if "👶" in question_text:
        return "easy"
    return "medium"


def slugify(value: str) -> str:
    """Create a deterministic slug for IDs and dedup keys."""
    lowered = value.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", "-", lowered)
    return normalized.strip("-")


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize one raw ingestion record into Swali-AI schema."""
    raw_question = str(record.get("question", "")).strip()
    normalized_question = normalize_question_text(raw_question)

    topic = str(record.get("category", "ml_general")).strip().lower().replace(" ", "_")
    source = str(record.get("source", "unknown_source")).strip()

    question_slug = slugify(normalized_question)[:60]
    source_slug = slugify(source)
    digest = hashlib.sha1(normalized_question.encode("utf-8")).hexdigest()[:12]

    return {
        "id": f"aiml_{source_slug}_{question_slug}_{digest}",
        "title": normalized_question,
        "difficulty": infer_difficulty(raw_question),
        "description": normalized_question,
        "tags": [topic, "ai_ml_interview"],
        "source": "ai_ml_interviews",
        "source_name": source,
        "source_url": record.get("source_url"),
        "type": "ai_ml_question",
        "topic_family": record.get("topic_family", "ml_engineering"),
    }


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize multiple records and drop empty titles."""
    normalized = [normalize_record(record) for record in records]
    return [record for record in normalized if record.get("title")]