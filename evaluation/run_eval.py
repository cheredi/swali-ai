"""Automated retrieval evaluation for CI quality regression checks."""

from __future__ import annotations

import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.rag.vectorstore import VectorStore


EVAL_CASES = [
    {"query": "O(log n) binary search", "expected": ["binary", "search"]},
    {"query": "hash map two sum", "expected": ["two sum", "hash"]},
    {"query": "design scalable feed service", "expected": ["design", "system"]},
]


def evaluate() -> dict:
    store = VectorStore("problems")
    hits = 0
    total = len(EVAL_CASES)
    details = []

    for case in EVAL_CASES:
        results = store.search_hybrid(case["query"], n_results=5)
        titles = [
            (metadata.get("title") or "").lower()
            for metadata in results.get("metadatas", [[]])[0]
        ]
        found = any(any(expected in title for expected in case["expected"]) for title in titles)
        hits += int(found)
        details.append({"query": case["query"], "matched": found, "titles": titles[:3]})

    score = hits / total if total else 0.0
    return {"score": score, "hits": hits, "total": total, "details": details}


def main() -> None:
    report = evaluate()
    out_path = Path("evaluation") / "last_eval.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["score"] < 0.34:
        raise SystemExit("Retrieval quality check failed")


if __name__ == "__main__":
    main()
