# Swali-AI

A production-grade RAG system for technical interview preparation.

## Features

- **Smart Q&A** - Get explanations for coding and system design problems
- **Progressive Hints** - Nudges that guide without giving away the answer
-  **Adaptive Difficulty** - System learns from your performance
-  **Similar Problems** - Find related problems to reinforce learning
- **Follow-up Questions** - Test your understanding deeper

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: React + Vite
- **Vector DB**: ChromaDB
- **LLM**: Gemini API (Google)
- **Embeddings**: sentence-transformers

## Quick Start

```bash
# Backend
cd backend
poetry install
poetry run uvicorn main:app --reload

# Build the vector DB (required for search and follow-ups)
cd ..
poetry run python scripts/collect_ai_ml.py
poetry run python scripts/process_data.py

# Frontend
cd frontend
npm install
npm run dev
```

If your backend runs on a different host/port, set:

```bash
VITE_API_BASE_URL="http://localhost:8000" npm run dev
```

## Project Structure

```
swali-ai/
├── backend/           # FastAPI backend
│   ├── rag/          # RAG engine components
│   ├── services/     # Business logic
│   └── models/       # Data models
├── frontend/         # React frontend
├── data/             # Problem corpus
│   ├── raw/          # Scraped/collected data
│   └── processed/    # Chunked & embedded
└── scripts/          # Data collection scripts
```

## License

MIT

## Experiments

Run retrieval experiments (baseline, reranked, embedding A/B):

```bash
cd /Users/tatyanaamugo/swali-ai
poetry run python scripts/run_retrieval_experiments.py
```
