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

    # RAG settings
    retrieval_top_k: int = 5  # Number of documents to retrieve
    chunk_size: int = 1000    # Characters per chunk
    chunk_overlap: int = 200  # Overlap between chunks

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
