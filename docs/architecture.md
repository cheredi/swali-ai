# Architecture

Swali-AI is a Retrieval-Augmented Generation (RAG) interview learning platform.

## High-level Flow

1. User asks a question from frontend.
2. FastAPI receives request in router (`/api/chat`, `/api/search`).
3. RAG generator retrieves context from ChromaDB.
4. (Optional) reranker re-orders candidates.
5. Prompt template combines context + user input.
6. Gemini model generates grounded response.
7. API returns answer + sources.

## Architecture Diagram

```mermaid
flowchart TD
  User[User]
  Frontend[Frontend\nReact + Vite]
  API[FastAPI Backend\nbackend/main.py]
  ChatRouter[Chat Router\n/api/chat]
  SearchRouter[Search Router\n/api/search]
  Generator[RAG Generator\nbackend/app/rag/generator.py]
  PromptLayer[Prompt Registry\nbackend/app/prompts/__init__.py]
  LLMService[LLM Service\nbackend/app/rag/llm.py]
  Gemini[Gemini API]
  VectorStore[Vector Store\nbackend/app/rag/vectorstore.py]
  Embeddings[Embeddings\nbackend/app/rag/embeddings.py]
  Reranker[Hybrid Reranker\nbackend/app/rag/reranker.py]
  Chroma[(ChromaDB\ndata/chroma_db)]
  DataPipeline[Data Pipeline\nscripts/process_data.py + data_pipeline/*]
  RawData[(Raw Data Sources)]

  User --> Frontend --> API
  API --> ChatRouter
  API --> SearchRouter

  ChatRouter --> Generator
  SearchRouter --> VectorStore

  Generator --> VectorStore
  Generator --> PromptLayer
  Generator --> LLMService --> Gemini

  VectorStore --> Embeddings
  VectorStore --> Chroma
  Generator --> Reranker
  Reranker --> VectorStore

  RawData --> DataPipeline --> Chroma
```

## Chat Request Sequence (`/api/chat`)

```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant F as Frontend (React)
  participant R as Chat Router (/api/chat)
  participant G as RAGGenerator
  participant V as VectorStore
  participant K as HybridReranker
  participant P as Prompt Registry
  participant L as LLMService
  participant M as Gemini API

  U->>F: Submit question
  F->>R: POST /api/chat { message, hint_level?, problem_context? }
  R->>G: generate_answer(...) or generate_hints(...)

  G->>V: search(query, n_results)
  V-->>G: candidate docs + metadata + distances

  opt reranker enabled
    G->>K: rerank_search_results(query, candidates)
    K-->>G: top-k reranked docs
  end

  G->>P: get_prompt(template_name)
  P-->>G: prompt template
  G->>L: generate_with_retry(formatted_prompt)
  L->>M: generate_content(...)
  M-->>L: model response
  L-->>G: content + model + token usage

  G-->>R: RAGResponse(answer, sources, model, tokens_used)
  R-->>F: JSON response
  F-->>U: Render answer + cited sources
```

## Hint Request Sequence (`/api/chat/hint`)

```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant F as Frontend (React)
  participant R as Chat Router (/api/chat/hint)
  participant G as RAGGenerator
  participant V as VectorStore
  participant P as Prompt Registry
  participant L as LLMService
  participant M as Gemini API

  U->>F: Ask for hint on a problem
  F->>R: POST /api/chat/hint { problem_title, hint_level, student_attempt? }
  R->>R: Validate request model
  R->>G: generate_hints(problem_title, hint_level, student_attempt)

  G->>G: Normalize hint_level to [1..3]
  G->>V: search(problem_title, n_results=1)
  V-->>G: best matching problem document

  alt problem not found
    G-->>R: "I couldn't find this problem"
    R-->>F: fallback response with empty sources
  else problem found
    G->>P: get_prompt(hint_level_X)
    P-->>G: selected hint prompt template
    G->>L: generate_with_retry(formatted_hint_prompt)
    L->>M: generate_content(...)
    M-->>L: model response
    L-->>G: hint content + metadata
    G-->>R: RAGResponse(answer, sources, model, tokens_used)
    R-->>F: JSON hint response
  end

  F-->>U: Display progressive hint
```

## Components

### Backend API Layer
- Entry: `backend/main.py`
- Routers:
  - `backend/app/routers/search.py`
  - `backend/app/routers/chat.py`

Responsibilities:
- Request validation (Pydantic models)
- Route-level orchestration
- HTTP response shape

### RAG Orchestration Layer
- `backend/app/rag/generator.py`

Responsibilities:
- Run retrieval
- Build model-ready context
- Select prompt template
- Call LLM service
- Return answer + provenance metadata

### Retrieval Layer
- `backend/app/rag/vectorstore.py`
- `backend/app/rag/embeddings.py`
- `backend/app/rag/reranker.py`

Responsibilities:
- Text embedding generation
- Chroma CRUD/search operations
- Hybrid reranking for better top-k precision

### Prompt Layer
- `backend/app/prompts/__init__.py`

Responsibilities:
- Prompt templates for answer/hints/followups
- Versioning support for experimentable prompt variants

### Data Pipeline Layer
- `scripts/collect_*.py`
- `scripts/data_pipeline/*`
- `scripts/process_data.py`

Responsibilities:
- Collect raw data sources
- Normalize schema
- Deduplicate
- Build vector index

## Design Principles
- Ground generation in retrieved context.
- Keep concerns separated (router vs orchestration vs retrieval).
- Make experiments repeatable and logged.
- Prefer deterministic IDs and data transforms.
