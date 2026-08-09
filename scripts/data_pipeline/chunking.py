"""Semantic and code-aware chunking for ingestion."""

from __future__ import annotations

import re


def split_semantic_code_aware(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    """Split text while preserving fenced code blocks and paragraph semantics."""
    text = (text or "").strip()
    if not text:
        return []

    blocks = re.split(r"(```[\s\S]*?```)", text)
    units: list[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("```") and block.endswith("```"):
            units.append(block)
            continue
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", block) if p.strip()]
        units.extend(paragraphs)

    chunks: list[str] = []
    current = ""
    for unit in units:
        candidate = f"{current}\n\n{unit}".strip() if current else unit
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
        if len(unit) <= chunk_size:
            current = unit
            continue

        start = 0
        while start < len(unit):
            end = min(start + chunk_size, len(unit))
            segment = unit[start:end]
            chunks.append(segment)
            if end == len(unit):
                break
            start = max(0, end - overlap)
        current = ""

    if current:
        chunks.append(current)

    return chunks
