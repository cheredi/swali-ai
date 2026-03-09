# Swali-AI — Agent Reference

## Agent Quick Start (Open These 5 Files First)
1. `backend/main.py` — app entrypoint, middleware, router wiring.
2. `backend/app/config.py` — all runtime environment settings.
3. `backend/app/routers/chat.py` — core user-facing RAG endpoints.
4. `backend/app/rag/generator.py` — retrieval + prompt + LLM orchestration.
5. `frontend/src/components/PracticeSection.tsx` — primary user workflow and key frontend API calls.

Useful jump points:
- API surface: `backend/app/routers/`
- Prompt templates: `backend/app/prompts/__init__.py`
- Data/index pipeline: `scripts/process_data.py`
- Evaluation gate: `evaluation/run_eval.py`
- CI flow: `.github/workflows/tests.yml`

## Safe Change Checklist
Before editing:
1. Read this file fully.
2. Confirm current mode/feature path in both router and frontend caller.
3. Check whether change touches prompts, indexing, or auth/token flow.

During editing:
1. Keep changes scoped; avoid unrelated refactors.
2. Preserve API response shapes unless change is intentional and propagated.
3. Do not modify `data/chroma_db/*` directly.

After editing:
1. Run targeted tests first (closest affected tests).
2. Run broader checks:
  - `make test`
  - `poetry run python evaluation/run_eval.py` (if retrieval/prompt/index touched)
  - `cd frontend && npm run build` (if UI touched)
3. Manually verify key endpoints/pages you changed.

## What This App Does
Swali-AI is a retrieval-augmented interview preparation app. It helps candidates practice coding, system design, and AI/ML interview questions with grounded responses instead of generic chatbot output. The system retrieves relevant content from a local vector database first, then uses an LLM to generate answers, hints, follow-up questions, and practice sets.

The core users are software and ML candidates who want both broad practice and role-specific practice. The key value is trust + relevance: responses are tied to retrieved sources (not pure hallucination), and users can run structured practice modes including job-aligned drills and mock-interview scoring.

## Tech Stack
- FastAPI — backend API framework and routing (`backend/main.py`, `backend/app/routers/*`).
- Pydantic / pydantic-settings — request/response validation + env configuration (`backend/app/config.py`).
- Uvicorn — ASGI server for local/dev runtime.
- ChromaDB — persistent vector index (`data/chroma_db`, `backend/app/rag/vectorstore.py`).
- sentence-transformers — text embedding generation (`backend/app/rag/embeddings.py`).
- Cross-encoder reranker — optional precision reranking (`backend/app/rag/reranker.py`).
- Gemini API (`google-generativeai`) — generation and grading (`backend/app/rag/llm.py`).
- SQLite — app persistence for users/sessions/messages/grades/submissions (`backend/app/storage.py`, default `data/app.db`).
- JWT auth (`python-jose`, `passlib`) — token auth + password hashing (`backend/app/auth.py`).
- Redis (optional) — cache/rate-limiter backend with in-memory fallback (`backend/app/services/cache_rate_limit.py`).
- React 19 + TypeScript — frontend app (`frontend/src/*`).
- Vite — frontend build/dev server (`frontend/vite.config.ts`).
- React Router — frontend routing (`frontend/src/App.tsx`).
- Tailwind CSS — frontend styling (`frontend/src/index.css`).
- Mammoth — `.docx` parsing for job descriptions (`frontend/src/components/PracticeSection.tsx`).
- Poetry — dependency and environment management (`pyproject.toml`).
- Docker / docker compose — local containerized dev (`Dockerfile.dev`, `docker-composer.dev.yml`).
- GitHub Actions — CI tests + retrieval evaluation (`.github/workflows/tests.yml`).

## Project Structure
- `backend/` — production backend code.
  - `backend/main.py` — FastAPI entrypoint, middleware, router inclusion.
  - `backend/app/config.py` — env-based settings.
  - `backend/app/routers/` — API routes (`chat.py`, `search.py`, `auth.py`, `learning.py`).
  - `backend/app/rag/` — RAG engine (embeddings, vectorstore, reranker, generator, llm).
  - `backend/app/prompts/` — runtime prompt template registry.
  - `backend/app/services/` — cache/rate-limit, scheduler, sandbox helpers.
  - `backend/app/storage.py` — SQLite schema + CRUD layer.
  - `backend/app/models/` — API and domain schemas.
- `frontend/` — React/Vite frontend.
  - `frontend/src/pages/` — page-level routes (`LandingPage`, `PracticePage`).
  - `frontend/src/components/` — UI components (`PracticeSection`, `AuthPanel`, etc.).
  - `frontend/src/App.tsx` — route map (lazy-loaded pages).
- `scripts/` — data collection, normalization, indexing, experiments.
  - `scripts/data_pipeline/` — ingestion/normalize/dedup/chunking helpers.
- `data/` — raw and processed data artifacts.
  - `data/raw/` — source corpora by domain.
  - `data/chroma_db/` — persistent vector index files.
- `evaluation/` — retrieval quality checks (`evaluation/run_eval.py`).
- `tests/` — backend tests.
- `docs/` — architecture docs + ADRs.
- `prompts/` — prompt strategy docs (runtime prompt code is under backend).
- `src/` + `sr/` — non-runtime/auxiliary scaffolding; current app runtime paths are `backend/` and `frontend/`.
- Root configs: `pyproject.toml`, `Makefile`, `docker-composer.dev.yml`, `.github/workflows/tests.yml`, `Dockerfile.dev`.

## Key Files
- Runtime entrypoints:
  - `backend/main.py`
  - `frontend/src/main.tsx`
  - `frontend/src/App.tsx`
- Core backend flow:
  - `backend/app/routers/chat.py`
  - `backend/app/rag/generator.py`
  - `backend/app/rag/vectorstore.py`
  - `backend/app/rag/reranker.py`
  - `backend/app/rag/llm.py`
- Auth/session/learning:
  - `backend/app/auth.py`
  - `backend/app/routers/auth.py`
  - `backend/app/routers/learning.py`
  - `backend/app/storage.py`
- Config/environment:
  - `backend/app/config.py`
  - `frontend/src/components/AuthPanel.tsx` (token handling)
  - `frontend/src/components/PracticeSection.tsx` (API base URL usage)
- Prompt templates:
  - `backend/app/prompts/__init__.py`
- Data pipeline:
  - `scripts/collect_ai_ml.py`
  - `scripts/collect_leetcode.py`
  - `scripts/process_data.py`
  - `scripts/data_pipeline/chunking.py`
- Evaluation/CI:
  - `evaluation/run_eval.py`
  - `.github/workflows/tests.yml`

## Data Pipeline
Data flows in this order:
1. **Collect raw datasets** into `data/raw/*`.
   - AI/ML: `scripts/collect_ai_ml.py` (internally uses ingestion/normalize/dedup pipeline helpers).
   - Optional LeetCode expansion: `scripts/collect_leetcode.py` -> `data/raw/leetcode/all_problems.json`.
   - Existing NeetCode/system-design corpora are loaded from their JSON files under `data/raw/`.
2. **Process and index** with `scripts/process_data.py`.
   - Loads each corpus.
   - Builds embed text + metadata.
   - Splits text with semantic/code-aware chunking (`scripts/data_pipeline/chunking.py`).
   - Generates embeddings (`backend/app/rag/embeddings.py`).
   - Inserts into Chroma collection `problems` (`backend/app/rag/vectorstore.py`).
3. **Persist index** in `data/chroma_db/` for retrieval at runtime.

Important: `process_data.py` clears existing vector docs before rebuilding.

## RAG Pipeline
Typical query flow (`/api/chat`):
1. Frontend sends question to `POST /api/chat/` (`backend/app/routers/chat.py`).
2. Router applies rate-limit/cache checks (`backend/app/services/cache_rate_limit.py`).
3. Router calls `RAGGenerator.generate_answer_async` (`backend/app/rag/generator.py`).
4. Generator may create query variants for expansion.
5. Generator retrieves candidates via hybrid search (`search_hybrid_async` in `vectorstore.py`).
6. Optional reranking refines top candidates (`reranker.py`).
7. Generator builds prompt using templates (`backend/app/prompts/__init__.py`).
8. Generator calls Gemini through `llm.py`.
9. Response is returned with answer + sources + citations + query variants + token/model metadata.

## Frontend Routes & Pages
- `/` -> `LandingPage` (`frontend/src/pages/LandingPage.tsx`)
  - Main purpose: product overview + CTA to practice modes.
  - API calls: none direct.
- `/practice` -> `PracticePage` (`frontend/src/pages/PracticePage.tsx`)
  - Renders `AuthPanel` + `PracticeSection`.
  - Query param `mode` controls active practice mode.

Main frontend API callers:
- `frontend/src/components/AuthPanel.tsx`
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- `frontend/src/components/PracticeSection.tsx`
  - `POST /api/chat/practice`
  - `POST /api/learning/mock-interview` (score mock answers; bearer token expected)

## API Endpoints
### System
- `GET /` -> greeting/status/docs pointer.
- `GET /health` -> component health payload.

### Chat
- `POST /api/chat/`
  - Input: `message`, optional `hint_level`, `problem_context`, `topic`, `company`, `difficulty`, `session_id`.
  - Returns: `answer`, `sources`, `citations`, `query_variants`, `tokens_used`, `model`.
- `POST /api/chat/hint`
  - Input: `problem_title`, `hint_level`, `student_attempt`.
  - Returns: chat-shaped hint response.
- `POST /api/chat/followup`
  - Input: `problem_title`, `solution_approach`.
  - Returns: `questions`, `sources`, `tokens_used`, `model`.
- `POST /api/chat/practice`
  - Input: `mode` (`general|job_aligned`), `focus_area`, `job_description`, `question_count`.
  - Returns: `questions`, `sources`, `tokens_used`, `model`.

### Search
- `GET /api/search/`
  - Query params: `q`, `limit`, `type_filter`, `difficulty`, `topic`, `company`.
  - Returns: ranked retrieval results and metadata.
- `GET /api/search/stats`
  - Returns: collection stats/counts.

### Auth
- `POST /api/auth/register`
  - Input: `email`, `password`.
  - Returns: `access_token`, `token_type`, `user_id`, `email`.
- `POST /api/auth/login`
  - Input: `email`, `password`.
  - Returns: same auth payload.
- `GET /api/auth/me` (bearer)
  - Returns: current user profile.

### Learning (bearer required)
- `POST /api/learning/sessions` -> create session.
- `POST /api/learning/sessions/message` -> append session message.
- `GET /api/learning/sessions/{session_id}/history` -> session messages.
- `POST /api/learning/spaced-repetition/review` -> submit quality and compute next due.
- `GET /api/learning/spaced-repetition/due` -> due review items.
- `POST /api/learning/grade` -> rubric score an answer.
- `POST /api/learning/mock-interview` -> score mock interview answer.
- `POST /api/learning/sandbox/execute` -> run code via sandbox API.
- `POST /api/learning/content/submit` -> submit user content.
- `GET /api/learning/content/submissions` -> list submissions.
- `POST /api/learning/content/review` -> approve/reject submission.

## Practice Modes
- **General Practice**
  - Prompt: general practice template.
  - Retrieval: broad/focus-based query.
  - Response: generated question set + sources.
- **Job-Aligned Practice**
  - Prompt: job-aligned practice template.
  - Retrieval: includes JD text + focus area.
  - Router validation: requires non-empty `job_description`.
  - Response: role-specific question set + sources.
- **Mock Interview**
  - Frontend mode orchestration:
    - Generates question set via `/api/chat/practice` (currently mapped to general generation path).
    - Scores typed answer via `/api/learning/mock-interview`.
  - UX extras: timer, score card, no default hinting emphasis.

## Environment Variables
Backend (`backend/app/config.py`):
- `GEMINI_API_KEY` — Gemini credentials.
- `CHROMA_PERSIST_DIR` — Chroma storage path.
- `DATA_DIR` — data root path.
- `EMBEDDING_MODEL` — sentence-transformers model name.
- `LLM_MODEL` — Gemini model identifier.
- `RERANKER_MODEL` — cross-encoder reranker model name.
- `RETRIEVAL_TOP_K` — default retrieval k.
- `CHUNK_SIZE` — chunk size for text splitting.
- `CHUNK_OVERLAP` — overlap between chunks.
- `DENSE_WEIGHT` — dense/sparse mix ratio for hybrid retrieval.
- `JWT_SECRET_KEY` — JWT signing key.
- `JWT_ALGORITHM` — JWT algorithm (default HS256).
- `JWT_EXP_MINUTES` — token expiry window.
- `APP_DB_PATH` — SQLite app DB location.
- `REDIS_URL` — optional Redis connection URL.
- `RATE_LIMIT_REQUESTS` — max requests per window.
- `RATE_LIMIT_WINDOW_SECONDS` — rate limit window size.
- `ENABLE_STRUCTURED_LOGGING` — JSON request logging toggle.

Frontend:
- `VITE_API_BASE_URL` — backend base URL (defaults to `http://localhost:8000`).

## How to Run Locally
From project root:
1. Install dependencies:
   - `make install`
2. Build/rebuild vector index:
   - `make collect-ai-ml` (optional refresh)
   - `make collect-leetcode` (optional expansion)
  - `make collect-external` (external corpus refresh)
   - `make process-data`
3. Start backend:
   - `make run-backend`
4. Start frontend (new terminal):
   - `make run-frontend`
5. Verify:
   - Backend docs: `http://localhost:8000/docs`
   - Frontend app: `http://localhost:5173`

Alternative Docker dev:
- `docker compose -f docker-composer.dev.yml up --build`

## What NOT to Touch
- Do **not** edit `data/chroma_db/*` manually (binary/index internals).
- Do **not** mutate vector index by hand; rebuild via scripts.
- Be careful with `scripts/process_data.py`: it clears vector docs before reindex.
- Do **not** rename prompt keys in `backend/app/prompts/__init__.py` without updating generator lookups and testing outputs.
- Do **not** change ID conventions in indexing scripts lightly (`nc_*`, `sd_*`, `aiml_*`, etc.).
- Do **not** alter auth token shape/storage conventions casually (`swali_access_token`, bearer header) without updating both frontend and backend.
- Treat `experiments/`, `htmlcov/`, and data artifacts as generated outputs.

## External Corpus Notes
- Collector: `scripts/collect_external_corpus.py`
- Output: `data/raw/external/external_corpus.json`
- Optional local files (strictly validated when present):
  - `data/raw/external/kaggle_software_engineering_interview_questions.json`
  - `data/raw/external/leetcode_discuss_threads.json`
  - `data/raw/external/neetcode_explanations.json`
  - `data/raw/external/ddia_highlights.json`
- `scripts/process_data.py` now ingests:
  - external corpus records
  - approved user submissions from SQLite (`content_submissions`, `status='approved'`)

## Agent Rules
- Always read this file before making any change
- Never modify the vector DB index directly
- Never change prompt templates without testing retrieval output first
- Keep frontend components in their existing file structure
- Run existing tests before and after changes
