# Swali-AI: Complete Project Walkthrough

## Quick Start Commands

```bash
cd /Users/tatyanaamugo/swali-ai
export PATH="/Users/tatyanaamugo/.local/bin:$PATH"

# Run the API server
cd backend && poetry run uvicorn main:app --reload

# Access in browser: http://localhost:8000/docs
```

### Finding Your Virtual Environment (Poetry)

If you don't remember the virtual environment name, Poetry can tell you where it lives.

```bash
# Show the active virtualenv path (if any)
cd /Users/tatyanaamugo/swali-ai
poetry env info -p

# List all Poetry environments for this project
poetry env list
```

If the environment isn't created yet, run:

```bash
poetry install
```

---

## Architecture Overview: The Complete RAG Pipeline

### How All Files Connect

```
                              USER REQUEST
                          "How do I solve Two Sum?"
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI SERVER                                  │
│                                main.py                                       │
│                         (starts server, loads routers)                       │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
            ┌───────────────────────┴────────────────────────┐
            ▼                                                ▼
┌───────────────────────┐                      ┌───────────────────────┐
│   routers/search.py   │                      │   routers/chat.py     │
│   /api/search/        │                      │   /api/chat/          │
│ (semantic search only)│                      │ (RAG: search + LLM)   │
└───────────────────────┘                      └───────────┬───────────┘
                                                           │
                                                           ▼
                                               ┌───────────────────────┐
                                               │   rag/generator.py    │
                                               │   (RAG Orchestrator)  │
                                               │                       │
                                               │   1. RETRIEVE context │
                                               │   2. AUGMENT prompt   │
                                               │   3. GENERATE answer  │
                                               └───────────┬───────────┘
                                                           │
                    ┌──────────────────────────────────────┼──────────────────┐
                    │                                      │                  │
                    ▼                                      ▼                  ▼
        ┌───────────────────┐                  ┌───────────────────┐  ┌──────────────┐
        │ rag/vectorstore.py│                  │ prompts/__init__.py│  │  rag/llm.py  │
        │   (ChromaDB)      │                  │ (Prompt Templates) │  │ (Gemini API) │
        │                   │                  │                    │  │              │
        │ • Store docs      │                  │ • ANSWER_PROMPT    │  │ • API config │
        │ • Search similar  │                  │ • HINT_PROMPT      │  │ • Retry logic│
        │ • Filter by type  │                  │ • FOLLOWUP_PROMPT  │  │ • Temp/tokens│
        └─────────┬─────────┘                  └────────────────────┘  └──────┬───────┘
                  │                                                           │
                  ▼                                                           ▼
        ┌───────────────────┐                                      ┌───────────────────┐
        │ rag/embeddings.py │                                      │   Gemini API      │
        │ (Text → Vectors)  │                                      │   (Google Cloud)  │
        │                   │                                      │                   │
        │ all-MiniLM-L6-v2  │                                      │ gemini-2.0-flash  │
        └─────────┬─────────┘                                      └───────────────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  data/chroma_db/  │
        │  (Vector Storage) │
        │   154 documents   │
        └───────────────────┘
```

### File Purpose Summary

| File | What It Does | Talks To |
|------|--------------|----------|
| `main.py` | Starts FastAPI server, loads routers | All routers |
| `routers/chat.py` | `/api/chat/` endpoint | generator.py |
| `routers/search.py` | `/api/search/` endpoint | vectorstore.py |
| `rag/generator.py` | Orchestrates RAG flow | vectorstore, prompts, llm |
| `rag/llm.py` | Calls Gemini API | Gemini Cloud |
| `rag/vectorstore.py` | Searches ChromaDB | embeddings.py |
| `rag/embeddings.py` | Converts text → vectors | - |
| `prompts/__init__.py` | Prompt templates | Used by generator |
| `config.py` | Loads settings from `.env` | Used everywhere |

### What is RAG (Retrieval-Augmented Generation)?

RAG combines search with AI generation:
1. **Retrieve** - Find relevant documents from your database
2. **Augment** - Add those documents as context to the prompt
3. **Generate** - Let the LLM answer using that context

This gives you AI responses grounded in YOUR data!

---

## Phase 1: Data & Embeddings (Completed ✓)

### The Embedding Pipeline

```
JSON Files → Embeddings → ChromaDB
     │            │            │
  Raw data   384-dim vectors  Searchable
```

| File | Purpose |
|------|---------|
| [process_data.py](file:///Users/tatyanaamugo/swali-ai/scripts/process_data.py) | Pipeline: JSON → Embeddings → ChromaDB |
| [embeddings.py](file:///Users/tatyanaamugo/swali-ai/backend/app/rag/embeddings.py) | Text → Vector conversion via `all-MiniLM-L6-v2` |
| [vectorstore.py](file:///Users/tatyanaamugo/swali-ai/backend/app/rag/vectorstore.py) | ChromaDB wrapper for storage & search |
| [search.py](file:///Users/tatyanaamugo/swali-ai/backend/app/routers/search.py) | REST API for semantic search |

---

## Phase 2: LLM Integration (Completed ✓)

### New Files Created

| File | Purpose | Key Concepts |
|------|---------|--------------|
| [llm.py](file:///Users/tatyanaamugo/swali-ai/backend/app/rag/llm.py) | Gemini API wrapper | API keys, temperature, token limits |
| [generator.py](file:///Users/tatyanaamugo/swali-ai/backend/app/rag/generator.py) | RAG pipeline orchestrator | Context formatting, source tracking |
| [chat.py](file:///Users/tatyanaamugo/swali-ai/backend/app/routers/chat.py) | Chat API endpoint | Request/response models |
| [prompts/\_\_init\_\_.py](file:///Users/tatyanaamugo/swali-ai/backend/app/prompts/__init__.py) | Versioned prompt templates | Prompt engineering |

### How `llm.py` Works

```python
# 1. Configure API with your key
genai.configure(api_key=settings.gemini_api_key)

# 2. Create model instance
model = GenerativeModel("models/gemini-2.0-flash")

# 3. Generate response
response = model.generate_content(prompt)
```

**Key Concepts:**
- **API Key** - Your secret credential (stored in `.env`)
- **Temperature** - 0 = deterministic, 1 = creative
- **Max Tokens** - Limits response length to control costs

### How `generator.py` Works

```python
# The RAG flow:
def generate_answer(question):
    # 1. RETRIEVE - Find similar documents
    context_docs = vector_store.search(question, n=3)
    
    # 2. AUGMENT - Format prompt with context
    prompt = f"""
    Context: {context_docs}
    Question: {question}
    Answer based on the context above.
    """
    
    # 3. GENERATE - Get LLM response
    return llm.generate(prompt)
```

---

## Using the Chat API

### Ask a Question
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I solve Two Sum?"}'
```

**Response:**
```json
{
  "answer": "Two Sum can be solved using a HashMap...",
  "sources": [
    {"title": "Two Sum", "pattern": "Arrays Hashing", "difficulty": "easy"}
  ],
  "tokens_used": 150,
  "model": "models/gemini-2.0-flash"
}
```

### Get a Hint
```bash
curl -X POST http://localhost:8000/api/chat/hint \
  -H "Content-Type: application/json" \
  -d '{"problem_title": "Two Sum", "hint_level": 1}'
```

### Progressive Hints (How It Works)

The backend supports hint levels 1–3:

1. **Level 1**: Subtle nudge (no algorithm name)
2. **Level 2**: Suggests a technique (e.g., HashMap, Two Pointers)
3. **Level 3**: Step-by-step walkthrough (pseudocode level)

There are two ways to request hints:

- **Dedicated endpoint**: `POST /api/chat/hint`
- **Unified endpoint**: `POST /api/chat/` with `hint_level > 0`

When using the unified endpoint, you must pass `problem_context` (the title):

```json
{
  "message": "I tried nested loops and it's too slow",
  "hint_level": 2,
  "problem_context": "Two Sum"
}
```

### Follow-up Questions (How It Works)

Follow-ups test depth after a solution. They focus on:

- Optimization tradeoffs
- Edge cases or constraints changes
- Related problems or patterns

Call the new endpoint:

```bash
curl -X POST http://localhost:8000/api/chat/followup \
  -H "Content-Type: application/json" \
  -d '{"problem_title": "Two Sum", "solution_approach": "Used a HashMap to store complements."}'
```

Sample response:

```json
{
  "questions": "1) How would you reduce space...\n2) What if the array is sorted...\n3) Which problems share this pattern...",
  "sources": [{"title": "Two Sum", "difficulty": "easy"}],
  "tokens_used": 120,
  "model": "models/gemini-2.0-flash"
}
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# LLM - Get key from https://aistudio.google.com/apikey
GEMINI_API_KEY=your-key-here

# Model - Available models listed at API
LLM_MODEL=models/gemini-2.0-flash

# Vector Store
CHROMA_PERSIST_DIR=./data/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

> **SECURITY NOTE**: Never commit `.env` to git! It contains secrets.

---

## Key Learning: Service Pattern

We wrap APIs in "service" classes for clean code:

```python
# Bad: Direct API calls everywhere
response = genai.GenerativeModel(...).generate_content(...)

# Good: Service wrapper
class LLMService:
    def generate(self, prompt):
        # Centralized config, retry logic, error handling
        return self.model.generate_content(prompt)
        
service = LLMService()
response = service.generate(prompt)
```

**Benefits:**
- Centralized configuration
- Retry logic in one place
- Easy to mock for testing
- Consistent error handling

---

## Project Structure

```
swali-ai/
├── backend/
│   ├── app/
│   │   ├── rag/
│   │   │   ├── embeddings.py   # Text → Vectors
│   │   │   ├── vectorstore.py  # ChromaDB wrapper
│   │   │   ├── llm.py          # Gemini API ← NEW
│   │   │   └── generator.py    # RAG orchestrator ← NEW
│   │   ├── routers/
│   │   │   ├── search.py       # /api/search/
│   │   │   └── chat.py         # /api/chat/ ← NEW
│   │   ├── prompts/            # Prompt templates ← NEW
│   │   └── config.py           # Settings
│   ├── main.py                 # FastAPI app
│   └── .env                    # Secrets (not in git!)
├── data/
│   ├── raw/                    # JSON source data
│   └── chroma_db/              # Vector database
└── scripts/
    ├── process_data.py         # Data pipeline
    └── collect_*.py            # Data collectors
```

---

## Command Reference

| Task | Command |
|------|---------|
| Start API | `cd backend && poetry run uvicorn main:app --reload` |
| Process data | `poetry run python scripts/process_data.py` |
| Run tests | `poetry run pytest` |
| Test LLM | `poetry run python -m app.rag.llm` |
| API docs | http://localhost:8000/docs |

---

## Data Stats

| Metric | Value |
|--------|-------|
| Total documents | 154 |
| NeetCode problems | 138 |
| System Design topics | 8 |
| System Design questions | 8 |
| Embedding dimensions | 384 |
| LLM Model | gemini-2.0-flash |

---

## Next Steps

1. **Progressive Hints** - Add a hint-level UI in the frontend and capture student attempts
2. **Similar Problem Search** - Use `vectorstore.search_by_embedding()` to suggest related problems
3. **Follow-up Questions** - Add an endpoint that uses `generate_followup` prompts
4. **React Frontend** - Build the user interface (chat, hints, sources)
5. **Evaluation** - Add simple metrics (answer quality, retrieval relevance)

---

## Change Log: Follow-up Questions (Step-by-step)

1. **Added a generator method**
  - Implemented `generate_followup_questions()` in `rag/generator.py`.
  - **Why**: Keeps RAG orchestration in one place and reuses the prompt registry.

2. **Grounded follow-ups in the problem**
  - Reused vector search to fetch the problem description by title.
  - **Why**: Follow-ups are stronger when tied to the exact problem context.

3. **Added a dedicated API endpoint**
  - Created `POST /api/chat/followup` in `routers/chat.py`.
  - **Why**: Keeps the main chat endpoint clean and makes follow-ups explicit.

4. **Returned sources and metadata**
  - The response includes sources, tokens, and model name.
  - **Why**: Transparency helps debugging and user trust.

---

## Phase 3: Data Expansion for AI/ML Interviews (Completed ✓)

### Why We Added This

The previous corpus was strong for coding + system design, but weak for AI/ML engineering interview prep.
To improve coverage, we added a dedicated AI/ML data pipeline with three explicit layers:

1. **Ingestion** (fetch and parse external sources)
2. **Normalization** (convert into one unified schema)
3. **Deduplication** (remove overlaps before embedding)

### Sources Chosen (and why)

1. **alexeygrigorev/data-science-interviews**
  - High-volume, structured interview questions in markdown
  - Strong coverage of ML theory, ML technical, and applied interview topics
2. **khangich/machine-learning-interview**
  - Focused ML engineering interview question lists and practical prompts

These sources significantly increase AI/ML interview breadth while keeping ingestion maintainable.

### New Files Added

| File | Purpose | Significance |
|------|---------|--------------|
| `scripts/data_pipeline/ingestion.py` | Pulls and parses markdown sources into raw records | Isolates external-source parsing logic from the rest of the pipeline |
| `scripts/data_pipeline/normalize.py` | Standardizes fields (`id`, `title`, `difficulty`, `tags`, etc.) | Gives stable schema for embeddings and filtering |
| `scripts/data_pipeline/deduplicate.py` | Removes duplicate/near-duplicate question records | Reduces noisy retrieval and vector-store bloat |
| `scripts/collect_ai_ml.py` | Orchestrates ingestion + normalization + dedup and writes dataset JSON | One command to refresh AI/ML corpus |

### Backend Integration Changes

`scripts/process_data.py` now includes:

1. **`process_ai_ml_questions()`**
  - Reads `data/raw/ai_ml/ai_ml_questions.json`
  - Converts each question into embedding text
  - Stores metadata with `type = ai_ml_question`

2. **Updated pipeline order**
  - `process_neetcode()`
  - `process_system_design()`
  - `process_ai_ml_questions()`

3. **Stats update**
  - Added `ai_ml_questions` to run summary output

### Important Bug Fix During Implementation

While embedding AI/ML questions, Chroma raised duplicate ID errors.

- **Cause**: IDs were slug-based and truncated, causing collisions for long similar questions.
- **Fix**: IDs now append a deterministic hash suffix from question text.
- **Significance**: Stable and unique IDs are required for reliable vector-store insertion and updates.

### Commands Used to Build the Expanded Corpus

```bash
cd /Users/tatyanaamugo/swali-ai
poetry run python scripts/collect_ai_ml.py
poetry run python scripts/process_data.py
```

### Current Corpus Size After Expansion

- NeetCode problems: **138**
- System design items: **16**
- AI/ML interview questions: **261**
- Total vector records: **415**

### Learning Notes

1. **Ingestion stability**
  - Raw markdown endpoints are usually more stable than scraping rendered HTML.
2. **Schema first, then vectors**
  - Normalize fields before embeddings to keep retrieval metadata consistent.
3. **Dedup before embedding**
  - Deduping late wastes embedding time and pollutes retrieval results.
4. **Deterministic IDs matter**
  - They prevent collisions and make re-runs reproducible.

---

## Phase 4: Retrieval Experiments (Reranking + Embedding A/B + Metrics) (Completed ✓)

### What We Added

1. **Reranker module**
  - File: `backend/app/rag/reranker.py`
  - Adds a hybrid reranker that combines:
    - semantic signal (vector distance)
    - lexical overlap (query vs document/title terms)

2. **Two-stage retrieval in generator**
  - File: `backend/app/rag/generator.py`
  - `generate_answer()` now:
    - retrieves a larger candidate set (`top = n_context * 4`)
    - reranks candidates
    - keeps top `n_context` for prompting

3. **Embedding A/B support in embedding service**
  - File: `backend/app/rag/embeddings.py`
  - Added model-cache methods for running multiple embedding models in one process:
    - `get_model_by_name()`
    - `embed_text_with_model()`
    - `embed_batch_with_model()`

4. **Vector-store experiment helpers**
  - File: `backend/app/rag/vectorstore.py`
  - Added:
    - `add_documents_with_embeddings()` for precomputed vectors
    - `get_all()` for exporting full collection content

5. **Evaluation harness script**
  - File: `scripts/run_retrieval_experiments.py`
  - Runs 4 experiment tracks:
    - baseline retrieval
    - reranked retrieval
    - embedding variant A
    - embedding variant B
  - Logs JSON outputs to `experiments/`

### Why This Is Significant

1. **Reranking improves top-k precision potential**
  - Vector search alone can return semantically close but less useful items.
  - Reranking is a standard production RAG pattern for quality at the top of results.

2. **Embedding A/B creates measurable model decisions**
  - Instead of guessing, we compare models on the same eval set and metrics.
  - This gives evidence for embedding-model changes.

3. **Metrics-first iteration loop**
  - We now have a repeatable loop:
    1) change retrieval strategy
    2) run evaluation
    3) compare metrics and logs

### Commands to Run Experiments

```bash
cd /Users/tatyanaamugo/swali-ai
poetry run python scripts/run_retrieval_experiments.py
```

### Latest Experiment Output (Example)

- Baseline run: `experiments/run_20260218_103436.json`
- Reranked run: `experiments/run_20260218_103439.json`
- Embedding A run: `experiments/run_20260218_103445_embedA.json`
- Embedding B run: `experiments/run_20260218_103445_embedB.json`

### Latest Metrics Snapshot

- **Baseline**: Recall@5 = 1.0, Precision@5 = 0.2, MRR = 0.8333
- **Reranked**: Recall@5 = 1.0, Precision@5 = 0.2, MRR = 0.8333
- **Embedding A (`all-MiniLM-L6-v2`)**: MRR = 0.8333
- **Embedding B (`all-MiniLM-L12-v2`)**: MRR = 0.875

### Learning Notes

1. **No metric change from reranking can still be valid**
  - On small eval sets, improvements may be invisible.
  - Increase eval coverage to better see reranker impact.

2. **Embedding B showed better MRR in this run**
  - This suggests better ranking of the first relevant hit for some queries.

3. **Evaluation quality depends on eval-case quality**
  - The more representative your queries and expected IDs, the more trustworthy your decisions.

---

## Frontend Build: What Was Added and Why

### UI Components (App.tsx)

We replaced the default Vite counter with a RAG client that mirrors the backend.

Key pieces:

1. **Mode selector** (`answer` | `hint` | `followup`)
  - **What it does**: Switches the request payload shape and endpoint.
  - **Why**: Each backend flow expects different fields.

2. **Request builder form**
  - **Answer** uses `message` only.
  - **Hint** uses `problem_title`, `hint_level`, `student_attempt`.
  - **Follow-up** uses `problem_title`, `solution_approach`.
  - **Why**: Keeps input validation client-side and avoids bad requests.

3. **Explicit endpoint routing**
  - `POST /api/chat` for answers
  - `POST /api/chat/hint` for hints
  - `POST /api/chat/followup` for follow-ups
  - **Why**: Prevents mixing payload shapes across endpoints.

4. **Response panel**
  - Shows answer/questions, sources, model name, tokens used.
  - **Why**: Helps you understand retrieval grounding and cost.

### Styling (App.css + index.css)

1. **Design system tokens**
  - CSS variables for colors, fonts, shadows, surfaces.
  - **Why**: Makes visual changes consistent and easier to theme.

2. **Intentional layout**
  - Two-panel grid: request builder + response output.
  - **Why**: Mirrors the request/response mental model for RAG.

3. **Animations and motion**
  - Subtle entry animations and button hover lift.
  - **Why**: Adds clarity without distracting from content.

4. **Typography**
  - Serif headline + geometric sans body.
  - **Why**: Gives contrast and a learning-oriented tone.

---

## Backend Additions: What Was Added and Why

### Follow-up Questions Endpoint

1. **Generator method** (`generate_followup_questions()`)
  - Retrieves the problem document, formats the follow-up prompt, and calls the LLM.
  - **Why**: Keeps RAG orchestration centralized in `RAGGenerator`.

2. **API endpoint** (`POST /api/chat/followup`)
  - Accepts `problem_title` and `solution_approach`.
  - Returns follow-up questions plus sources, tokens, and model.
  - **Why**: Dedicated endpoint keeps main chat flow clean.

### Progressive Hints Improvements

1. **Hint level normalization**
  - Clamps `hint_level` to 1-3 in `RAGGenerator`.
  - **Why**: Prevents invalid prompt selection from client mistakes.

2. **Input enforcement in chat router**
  - Requires `problem_context` when `hint_level > 0`.
  - **Why**: Avoids ambiguous hint generation without a target problem.

### Chroma Path Debug Fix (Why Search Was Empty)

1. **Symptom**: `GET /api/search` returned empty results.
2. **Cause**: `CHROMA_PERSIST_DIR` was set to a relative path in `.env`.
3. **Fix**: Remove the override so the backend uses the absolute default path.
4. **Why**: The API server and data pipeline must read/write the same DB folder.
