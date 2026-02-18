# Experiments

This file tracks retrieval and RAG experiment history in a human-readable format.

## Goals
- Improve retrieval quality before generation quality.
- Compare controlled changes one variable at a time.
- Keep every experiment reproducible with commands and outputs.

## Baseline Setup
- Dataset: LeetCode + NeetCode + System Design + AI/ML interview questions
- Vector store: ChromaDB
- Default embedding model: `all-MiniLM-L6-v2`
- Retrieval size: top-5 final output

## Experiment Log

### 2026-02-18 — Baseline vs Reranker + Embedding A/B
- Script: `python scripts/run_retrieval_experiments.py`
- Output files:
  - `experiments/run_20260218_103436.json`
  - `experiments/run_20260218_103439.json`
  - `experiments/run_20260218_103445_embedA.json`
  - `experiments/run_20260218_103445_embedB.json`
- Summary:
  - Baseline avg MRR: 0.8333
  - Reranked avg MRR: 0.8333
  - Embedding A (`all-MiniLM-L6-v2`) avg MRR: 0.8333
  - Embedding B (`all-MiniLM-L12-v2`) avg MRR: 0.8750
- Takeaway: Embedding B showed better ranking on this small test set.

## Next Experiments
- Increase evaluation cases to at least 30 queries.
- Add category-level metrics (arrays, graphs, system design, AI/ML).
- Compare reranker weight settings (`semantic_weight`, `lexical_weight`).
- Add answer-level evaluation (faithfulness and source grounding).
