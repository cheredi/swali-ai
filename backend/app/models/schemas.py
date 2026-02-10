"""
Data Models for Swali-AI

These Pydantic models define the structure of our data.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    """Problem difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProblemCategory(str, Enum):
    """Problem categories."""
    ARRAY = "array"
    STRING = "string"
    LINKED_LIST = "linked_list"
    TREE = "tree"
    GRAPH = "graph"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    BINARY_SEARCH = "binary_search"
    HASH_TABLE = "hash_table"
    STACK = "stack"
    HEAP = "heap"
    SYSTEM_DESIGN = "system_design"
    OTHER = "other"


class Problem(BaseModel):
    """
    A coding or system design problem.

    🎓 LEARNING NOTE: Pydantic Models
    These provide automatic validation and serialization.
    If you try to create a Problem with invalid data, it raises an error.
    """
    id: str = Field(..., description="Unique identifier (e.g., 'lc_1')")
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Full problem description")
    difficulty: Difficulty = Field(..., description="Difficulty level")
    category: ProblemCategory = Field(..., description="Primary category")
    tags: list[str] = Field(default_factory=list, description="Additional tags")

    # Optional fields
    examples: list[str] = Field(default_factory=list, description="Example inputs/outputs")
    constraints: list[str] = Field(default_factory=list, description="Problem constraints")
    hints: list[str] = Field(default_factory=list, description="Progressive hints")
    solution_approach: Optional[str] = Field(None, description="Brief solution approach")
    time_complexity: Optional[str] = Field(None, description="Expected time complexity")
    space_complexity: Optional[str] = Field(None, description="Expected space complexity")

    # Source information
    source: str = Field("custom", description="Source (leetcode, neetcode, etc.)")
    source_url: Optional[str] = Field(None, description="URL to original problem")

    def to_embedding_text(self) -> str:
        """
        Create text representation for embedding.

        🎓 LEARNING NOTE: What to embed?
        We combine title + description + tags for richer semantic meaning.
        This helps the model understand the problem better.
        """
        parts = [
            f"Title: {self.title}",
            f"Description: {self.description}",
            f"Category: {self.category.value}",
            f"Difficulty: {self.difficulty.value}",
        ]
        if self.tags:
            parts.append(f"Tags: {', '.join(self.tags)}")
        return "\n".join(parts)

    def to_metadata(self) -> dict[str, Any]:
        """Convert to metadata dict for vector store."""
        return {
            "title": self.title,
            "difficulty": self.difficulty.value,
            "category": self.category.value,
            "tags": ",".join(self.tags),
            "source": self.source,
        }


class SearchResult(BaseModel):
    """A search result from the vector store."""
    problem: Problem
    score: float = Field(..., description="Similarity score (lower = more similar)")


class ChatMessage(BaseModel):
    """A message in the chat."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for the chat endpoint."""
    message: str = Field(..., description="User's question or message")
    problem_id: Optional[str] = Field(None, description="Current problem context")
    conversation_history: list[ChatMessage] = Field(
        default_factory=list,
        description="Previous messages for context"
    )
    hint_level: int = Field(0, ge=0, le=3, description="Current hint level (0-3)")


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    answer: str = Field(..., description="The assistant's response")
    retrieved_problems: list[str] = Field(
        default_factory=list,
        description="IDs of problems used for context"
    )
    hint_level: int = Field(0, description="Updated hint level")
