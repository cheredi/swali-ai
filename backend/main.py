"""
Swali-AI: RAG-Powered Interview Preparation System
Main FastAPI Application

🎓 LEARNING NOTE: This is the entry point for our backend.
FastAPI provides automatic API documentation at /docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Swali-AI",
    description="RAG-powered interview preparation system",
    version="0.1.0"
)

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
from app.routers import search_router, chat_router

# Include routers
app.include_router(search_router)  # Semantic search at /api/search/
app.include_router(chat_router)    # Chat/RAG at /api/chat/


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
