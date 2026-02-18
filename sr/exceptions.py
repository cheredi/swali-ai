"""Project-level custom exception types.

Note: This file is intentionally placed under `sr/` as requested.
"""

from __future__ import annotations


class SwaliError(Exception):
    """Base exception for project-specific failures."""


class DataPipelineError(SwaliError):
    """Raised when ingestion/normalization/deduplication fails."""


class RetrievalError(SwaliError):
    """Raised when retrieval pipeline fails."""


class LLMGenerationError(SwaliError):
    """Raised when LLM generation fails."""
