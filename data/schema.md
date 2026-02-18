# Data Schema

This document defines the normalized record formats used by Swali-AI.

## 1) Core Indexed Document Schema

Used when writing into ChromaDB (`collection=problems`).

```json
{
  "id": "nc_1",
  "title": "Two Sum",
  "description": "Given an array of integers...",
  "difficulty": "easy",
  "type": "leetcode_problem",
  "source": "neetcode_150",
  "tags": ["arrays_hashing", "hash_map"],
  "pattern": "Arrays & Hashing"
}
```

### Field Notes
- `id` (string, required): Stable unique key, never reused.
- `title` (string, required): Human-readable problem name.
- `description` (string, required): Content used for embedding/retrieval.
- `difficulty` (string, optional): `easy|medium|hard`.
- `type` (string, required): Domain type (`leetcode_problem`, `system_design`, `ai_ml_question`).
- `source` (string, required): Dataset origin.
- `tags` (array[string], optional): Topic taxonomy.
- `pattern` (string, optional): Interview pattern label.

---

## 2) AI/ML Ingestion Normalized Schema

Output of `scripts/collect_ai_ml.py` after normalize + deduplicate.

```json
{
  "id": "aiml_data-science-interviews_what-is-overfitting_ab12cd34ef56",
  "title": "What is overfitting?",
  "difficulty": "medium",
  "description": "What is overfitting?",
  "tags": ["ml_theory", "ai_ml_interview"],
  "source": "ai_ml_interviews",
  "source_name": "data_science_interviews_theory",
  "source_url": "https://raw.githubusercontent.com/...",
  "type": "ai_ml_question",
  "topic_family": "ml_theory"
}
```

---

## 3) API Response Shape (RAG)

Returned by `/api/chat/`, `/api/chat/hint`, and `/api/chat/followup`.

```json
{
  "answer": "...",
  "sources": [
    {
      "id": "nc_1",
      "title": "Two Sum",
      "type": "leetcode_problem",
      "difficulty": "easy",
      "pattern": "Arrays & Hashing"
    }
  ],
  "model": "models/gemini-2.0-flash",
  "tokens_used": 123
}
```

---

## 4) ID Strategy

- Problem IDs from curated datasets are preserved where possible.
- AI/ML IDs are deterministic and include:
  - source slug
  - question slug
  - hash suffix

This prevents collisions across merged corpora while keeping IDs reproducible.
