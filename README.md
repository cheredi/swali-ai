# Swali-AI

A RAG-powered interview preparation system for mastering LeetCode, system design, and technical interviews.

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
- **LLM**: Claude API (Anthropic)
- **Embeddings**: sentence-transformers

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
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
