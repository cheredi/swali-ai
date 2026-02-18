"""
Deduplication Layer for AI/ML interview records.

LEARNING NOTE: Why dedup?
-------------------------
When aggregating multiple sources, overlap is common. Duplicates pollute search
results and waste vector store space.
"""

from __future__ import annotations

from typing import Any


def canonical_key(record: dict[str, Any]) -> str:
    """Generate a canonical key for semantic duplicates."""
    title = str(record.get("title", "")).strip().lower()
    # Ignore punctuation-level differences by retaining only alnum + spaces.
    normalized = "".join(char if char.isalnum() or char.isspace() else " " for char in title)
    normalized = " ".join(normalized.split())
    return normalized


def deduplicate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Keep one record per canonical question text.

    LEARNING NOTE: Source preference
    --------------------------------
    We retain the first encountered record. Since source ordering is curated,
    this provides deterministic outputs and stable IDs across runs.
    """
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []

    for record in records:
        key = canonical_key(record)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(record)

    return deduped