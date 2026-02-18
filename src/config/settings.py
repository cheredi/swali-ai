"""Reference settings module for future package-style refactor.

This file does not replace backend runtime settings yet.
It mirrors the same configuration model in a `src/` package layout.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "swali-ai"
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    gemini_api_key: str | None = Field(default=None)
    llm_model: str = Field(default="models/gemini-2.0-flash")

    chroma_persist_dir: str = Field(default=str(ROOT_DIR / "data" / "chroma_db"))
    embedding_model: str = Field(default="all-MiniLM-L6-v2")


settings = Settings()
