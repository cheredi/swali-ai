"""
AI/ML Interview Question Collector for Swali-AI.

This script composes three pipeline layers:
1) Ingestion    -> collect raw records from external sources
2) Normalization -> map to unified schema
3) Deduplication -> remove overlaps across sources
"""

from __future__ import annotations

import json
from pathlib import Path

from data_pipeline.deduplicate import deduplicate_records
from data_pipeline.ingestion import AIMLInterviewCollector
from data_pipeline.normalize import normalize_records


def collect_ai_ml_questions(output_dir: str = "./data/raw/ai_ml") -> list[dict]:
    """Collect, normalize, and deduplicate AI/ML interview questions."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    collector = AIMLInterviewCollector()

    print("Collecting raw AI/ML interview records...")
    raw_records = collector.collect()
    print(f"Raw records: {len(raw_records)}")

    print("Normalizing records...")
    normalized = normalize_records(raw_records)
    print(f"Normalized records: {len(normalized)}")

    print("Deduplicating records...")
    deduped = deduplicate_records(normalized)
    print(f"Deduplicated records: {len(deduped)}")

    output_file = output_path / "ai_ml_questions.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(deduped, file, indent=2, ensure_ascii=False)

    print(f"Saved dataset to: {output_file}")
    return deduped


if __name__ == "__main__":
    collect_ai_ml_questions()