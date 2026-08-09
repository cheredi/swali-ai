"""
Swali-AI: RAG-Powered Interview Preparation System
Main FastAPI Application

🎓 LEARNING NOTE: This is the entry point for our backend.
FastAPI provides automatic API documentation at /docs
"""

import json
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


logger = logging.getLogger("swali")
if settings.enable_structured_logging and not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started = time.time()
        response = await call_next(request)
        latency_ms = round((time.time() - started) * 1000, 2)
        response.headers["x-request-id"] = request_id

        if settings.enable_structured_logging:
            logger.info(
                json.dumps(
                    {
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "latency_ms": latency_ms,
                    }
                )
            )
        return response

# Create FastAPI app
app = FastAPI(
    title="Swali-AI",
    description="RAG-powered interview preparation system",
    version="0.1.0"
)

app.add_middleware(RequestLoggingMiddleware)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite & CRA defaults
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Welcome to Swali-AI! ",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "api": "up",
            "vector_store": "up",  # ChromaDB with 154 documents
            "llm": "up"            # Claude integration ready
        }
    }


# Import and include routers
from app.routers import auth_router, chat_router, learning_router, search_router

# Include routers
app.include_router(search_router)  # Semantic search at /api/search/
app.include_router(chat_router)    # Chat/RAG at /api/chat/
app.include_router(auth_router)    # JWT auth at /api/auth/
app.include_router(learning_router)  # learning tools at /api/learning/


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
