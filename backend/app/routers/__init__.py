"""
API Routers package for Swali-AI

LEARNING NOTE: Router Organization
=====================================
FastAPI encourages organizing endpoints into "routers".
Each router handles a specific feature area:

  /api/search/  → search.py  (semantic search)
  /api/chat/    → chat.py    (LLM conversations)
  /api/problems/→ problems.py (CRUD operations) - coming later

This separation makes the codebase easier to navigate and test.
"""

from .search import router as search_router
from .chat import router as chat_router

__all__ = ["search_router", "chat_router"]
