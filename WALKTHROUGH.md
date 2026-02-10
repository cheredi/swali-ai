# Swali-AI: Complete Project Walkthrough

## Quick Start Commands

```bash
cd /Users/tatyanaamugo/swali-ai
export PATH="/Users/tatyanaamugo/.local/bin:$PATH"

# Run the API server
cd backend && poetry run uvicorn main:app --reload

# Access in browser: http://localhost:8000/docs
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

1. **Progressive Hints** - Hint levels 1-3 with increasing detail
2. **Similar Problem Search** - Find related problems
3. **React Frontend** - Build the user interface
