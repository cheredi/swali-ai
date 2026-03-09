# Swali-AI Frontend

React + TypeScript + Vite frontend for Swali-AI.

## What exists now

- Routed app with:
  - `/` → landing page
  - `/practice` → practice workspace
- Practice workspace currently supports:
  - `general` mode
  - `job_aligned` mode
  - `mock_interview` mode (question workflow + scoring)
  - job-description paste/upload (`.txt`, `.md`, `.docx`)
  - API call to `POST /api/chat/practice`
  - API call to `POST /api/learning/mock-interview`
  - auth-required gating via modal + `/login` and `/register` routes

## Backend API coverage matrix

- **Wired in frontend**
  - `POST /api/chat/practice`
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `POST /api/learning/mock-interview`

- **Backend ready, frontend pending**
  - Chat: `POST /api/chat/`, `POST /api/chat/hint`, `POST /api/chat/followup`
  - Search: `GET /api/search/`, `GET /api/search/stats`
  - Auth: `GET /api/auth/me`
  - Learning:
    - sessions/history
    - spaced repetition review/due
    - grading and mock interview
    - sandbox execute
    - content submission/review

## Recommended next frontend milestones

1. Add auth shell (register/login, token storage, `Authorization: Bearer`).
2. Add session-aware chat panel using `/api/chat*` endpoints.
3. Show citations/query variants from chat responses.
4. Add learning dashboard for grade + spaced repetition due queue.
5. Add sandbox UI for runnable code practice.

## Local development

```bash
npm install
npm run dev
```

Set backend URL when needed:

```bash
VITE_API_BASE_URL="http://localhost:8000" npm run dev
```
