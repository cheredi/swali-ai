# ADR 001: Embedding Model Selection

- Status: Accepted
- Date: 2026-02-18

## Context

Swali-AI requires embeddings for semantic retrieval across coding, system design,
and AI/ML interview content. The model must balance quality, speed, and local
resource usage.

## Decision

Use `all-MiniLM-L6-v2` as default embedding model.

## Rationale

- Fast enough for local/dev indexing and query latency.
- Strong retrieval baseline for interview-style text.
- Lightweight footprint compared to larger models.
- Works well with sentence-transformers integration.

## Alternatives Considered

- `all-MiniLM-L12-v2`
  - Pros: Better retrieval quality in some cases.
  - Cons: Higher compute cost and slower throughput.

- Domain-specific larger embeddings
  - Pros: Potentially higher quality.
  - Cons: More infra complexity and cost.

## Consequences

- Keep `all-MiniLM-L6-v2` as production default for now.
- Support A/B experiments with alternate models.
- Revisit decision when eval set grows and accuracy targets tighten.

## Follow-up

- Maintain periodic A/B checks via `scripts/run_retrieval_experiments.py`.
- Add larger and more diverse benchmark queries.
