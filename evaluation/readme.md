# Evaluation README

This folder is for retrieval/generation evaluation methodology and artifacts.

## Current Evaluation

The script `scripts/run_retrieval_experiments.py` evaluates retrieval with:
- Recall@k
- Precision@k
- MRR

It supports:
1. Baseline retrieval
2. Reranked retrieval (hybrid semantic + lexical)
3. Embedding A/B comparison

## How to Run

```bash
cd /Users/tatyanaamugo/swali-ai
poetry run python scripts/run_retrieval_experiments.py
```

## Where Results Go

- Machine-readable logs are written to `experiments/*.json`.
- Human-readable summary should be added to `experiments.md`.

## Recommended Next Expansion

- Increase from 4 to 30+ evaluation cases.
- Add per-category metrics (arrays, linked lists, system design, AI/ML).
- Add generation metrics (faithfulness/source use).
