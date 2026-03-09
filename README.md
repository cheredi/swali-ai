# Swali-AI

Swali-AI is a Retrieval-Augmented Generation (RAG) interview practice system built to teach coding, system design, and AI/ML concepts with grounded answers, progressive hints, and follow-up questioning.

## Why this project exists

Most interview assistants are either:
- generic LLM chat (ungrounded, inconsistent), or
- static content libraries (no adaptive reasoning).

Swali-AI combines retrieval + generation so responses are grounded in a curated corpus and still feel like an interactive tutor.

## What makes it technically credible

- Retrieval-first architecture (vector search before generation)
- Two-stage ranking path (vector recall + optional hybrid reranking)
- Progressive hint system with controlled depth (`hint_level` 1-3)
- Follow-up generation grounded on retrieved problem context
- Repeatable retrieval experiments with logged metrics
- ADR-backed engineering decisions and architecture docs

## Fast recruiter view (30 seconds)

- Architecture docs: [docs/architecture.md](docs/architecture.md)
- Key design decision: [docs/decisions/001-embedding-model-selection.md](docs/decisions/001-embedding-model-selection.md)
- Retrieval experiment log: [experiments.md](experiments.md)
- Data schema: [data/schema.md](data/schema.md)
- Security posture: [security.md](security.md)

## Architecture at a glance

```mermaid
flowchart TD
	User[User] --> Frontend[Frontend\nReact + Vite]
	Frontend --> API[FastAPI Backend]
	API --> Chat[/api/chat + /api/chat/hint + /api/chat/followup + /api/chat/practice]
	API --> Search[/api/search]
	API --> Auth[/api/auth/*]
	API --> Learning[/api/learning/*]

	Chat --> Generator[RAG Generator]
	Generator --> VS[Vector Store]
	Generator --> Prompts[Prompt Registry]
	Generator --> LLM[LLM Service]
	LLM --> Gemini[Gemini API]

	VS --> Embeddings[Embedding Service]
	VS --> Chroma[(ChromaDB)]
	Generator --> Reranker[Hybrid Reranker]
	Reranker --> VS

	Raw[(Raw Data)] --> Pipeline[Ingestion + Normalize + Deduplicate]
	Pipeline --> Chroma
```

For detailed sequence diagrams, see [docs/architecture.md](docs/architecture.md).

## System capabilities

- **Answer Mode**: grounded answers with source citations
- **Hint Mode**: level-based coaching (nudge → technique → walkthrough)
- **Follow-up Mode**: deeper interview-style probing from your approach
- **Practice Mode**: `general` and `job_aligned` interview-question generation
- **Search Mode**: direct semantic retrieval inspection
- **Auth + Learning APIs**: JWT auth, sessions/history, grading, spaced repetition, sandbox, submissions

## Current API surface (2026-03)

- **Chat**
	- `POST /api/chat/`
	- `POST /api/chat/hint`
	- `POST /api/chat/followup`
	- `POST /api/chat/practice`
- **Search**
	- `GET /api/search/`
	- `GET /api/search/stats`
- **Auth**
	- `POST /api/auth/register`
	- `POST /api/auth/login`
	- `GET /api/auth/me`
- **Learning**
	- `POST /api/learning/sessions`
	- `POST /api/learning/sessions/message`
	- `GET /api/learning/sessions/{session_id}/history`
	- `POST /api/learning/spaced-repetition/review`
	- `GET /api/learning/spaced-repetition/due`
	- `POST /api/learning/grade`
	- `POST /api/learning/mock-interview`
	- `POST /api/learning/sandbox/execute`
	- `POST /api/learning/content/submit`
	- `GET /api/learning/content/submissions`
	- `POST /api/learning/content/review`

## Frontend status vs backend

- Implemented in UI:
	- Landing + practice flow (`/practice`) with `general` and `job_aligned` modes
	- Calls `POST /api/chat/practice`
- Not yet wired in UI (backend ready):
	- Auth flows (`/api/auth/*`)
	- Learning workflows (`/api/learning/*`)
	- Full chat modes (`/api/chat`, `/api/chat/hint`, `/api/chat/followup`) in the new routed UI
	- Search/filter exploration (`/api/search` with metadata filters)

## Engineering decisions (and why)

- **Default embedding model: `all-MiniLM-L6-v2`**
	- chosen for fast local iteration and strong baseline quality
	- documented in ADR: [docs/decisions/001-embedding-model-selection.md](docs/decisions/001-embedding-model-selection.md)

- **RAG orchestration separated from routers**
	- `routers/*` handle HTTP concerns
	- `rag/generator.py` owns retrieval + prompt + generation flow

- **Data pipeline modularized**
	- ingestion, normalization, and dedup are split for maintainability and reproducibility

## Evaluation and experiment results

Experiment runner:

```bash
poetry run python scripts/run_retrieval_experiments.py
```

Most recent logged summary (2026-02-18):

| Experiment | Avg Recall | Avg Precision | Avg MRR |
|---|---:|---:|---:|
| Baseline retrieval | 1.0000 | 0.2000 | 0.8333 |
| Hybrid reranked retrieval | 1.0000 | 0.2000 | 0.8333 |
| Embedding A (`all-MiniLM-L6-v2`) | 1.0000 | 0.2000 | 0.8333 |
| Embedding B (`all-MiniLM-L12-v2`) | 1.0000 | 0.2000 | 0.8750 |

Takeaway: `all-MiniLM-L12-v2` outperformed the default on this small benchmark set, but default remains `L6` for speed/cost balance pending a larger benchmark.

See full analysis and next steps in [experiments.md](experiments.md).

## Quick start

### 1) Install dependencies

```bash
poetry install --with dev
cd frontend && npm install && cd ..
```

### 2) Build/refresh corpus and vector index

```bash
poetry run python scripts/collect_ai_ml.py
poetry run python scripts/collect_external_corpus.py
poetry run python scripts/process_data.py
```

`scripts/process_data.py` now indexes:
- NeetCode + LeetCode + System Design + AI/ML corpora
- External corpus records from `data/raw/external/external_corpus.json`
- Approved user submissions from `content_submissions` (`status='approved'`)

Optional local source files for fuller external coverage:
- `data/raw/external/kaggle_software_engineering_interview_questions.json`
- `data/raw/external/leetcode_discuss_threads.json`
- `data/raw/external/neetcode_explanations.json`
- `data/raw/external/ddia_highlights.json`

### 3) Run backend

```bash
cd backend
poetry run uvicorn main:app --reload
```

### 4) Run frontend

```bash
cd frontend
npm run dev
```

If backend is not on localhost:8000:

```bash
VITE_API_BASE_URL="http://localhost:8000" npm run dev
```

## Makefile shortcuts

```bash
make help
make test
make run-backend
make run-frontend
make process-data
make collect-external
make experiments
```

## API examples

### Chat answer

```bash
curl -X POST http://localhost:8000/api/chat \
	-H "Content-Type: application/json" \
	-d '{"message":"How do I solve Two Sum in O(n)?"}'
```

### Hint

```bash
curl -X POST http://localhost:8000/api/chat/hint \
	-H "Content-Type: application/json" \
	-d '{"problem_title":"Two Sum","hint_level":2,"student_attempt":"Tried nested loops"}'
```

### Follow-up

```bash
curl -X POST http://localhost:8000/api/chat/followup \
	-H "Content-Type: application/json" \
	-d '{"problem_title":"Two Sum","solution_approach":"Used a hash map to track complements"}'
```

## Repository map

```text
backend/app/
	config.py              # central settings
	routers/               # API layer
	rag/                   # embeddings, vectorstore, reranker, generator, llm
	prompts/               # prompt registry/templates

scripts/
	data_pipeline/         # ingestion/normalize/deduplicate
	process_data.py        # index build
	run_retrieval_experiments.py

docs/
	architecture.md
	decisions/
```

## Testing and CI

- Local: `poetry run pytest`
- CI workflow: [.github/workflows/tests.yml](.github/workflows/tests.yml)

## Contributing

See [contributing.md](contributing.md) for setup, workflow, and PR checklist.

## License

MIT
