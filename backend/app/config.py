"""
Swali-AI Backend Configuration

This module loads environment variables and provides centralized configuration
for the entire backend application.

🎓 LEARNING NOTE: Configuration management
- Use environment variables for secrets (API keys)
- Use .env files for local development
- Never commit .env files with real secrets
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Determine project root (parent of backend directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load .env file from backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    gemini_api_key: Optional[str] = None  # Get from https://aistudio.google.com/

    # Paths - use absolute paths for consistency
    chroma_persist_dir: str = str(PROJECT_ROOT / "data" / "chroma_db")
    data_dir: str = str(PROJECT_ROOT / "data")

    # Model settings
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "models/gemini-2.0-flash"  # Fast, free tier available!
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # RAG settings
    retrieval_top_k: int = 5  # Number of documents to retrieve
    chunk_size: int = 1000    # Characters per chunk
    chunk_overlap: int = 200  # Overlap between chunks
    dense_weight: float = 0.65

    # Auth + persistence
    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 120
    app_db_path: str = str(PROJECT_ROOT / "data" / "app.db")

    # Redis/caching/rate limiting
    redis_url: str | None = None
    rate_limit_requests: int = 40
    rate_limit_window_seconds: int = 60

    # Observability
    enable_structured_logging: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
