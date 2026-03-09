"""Integration tests for upgraded RAG pipeline behavior."""

from __future__ import annotations

import pytest

from app.rag.generator import RAGGenerator


class _FakeLLMResponse:
    def __init__(self, content: str):
        self.content = content
        self.model = "fake"
        self.tokens_used = 10


class _FakeLLMService:
    def __init__(self):
        self.calls = 0

    async def generate_with_retry_async(self, prompt: str, max_tokens: int, temperature: float):
        self.calls += 1
        if self.calls == 1:
            return _FakeLLMResponse("- hash map pair search\n- complement lookup array")
        return _FakeLLMResponse("Use a hash map in one pass.")


class _FakeVectorStore:
    async def search_hybrid_async(self, query: str, n_results: int, where=None, dense_weight=0.65):
        return {
            "ids": [["doc_1"]],
            "documents": [["Two Sum solved with hash map and complement lookup."]],
            "metadatas": [[{"title": "Two Sum", "type": "coding_problem", "difficulty": "easy"}]],
            "distances": [[0.2]],
            "scores": [[0.9]],
        }


@pytest.mark.asyncio
async def test_generate_answer_async_adds_query_variants_and_citations():
    generator = RAGGenerator(llm_service=_FakeLLMService(), vector_store=_FakeVectorStore(), use_reranker=False)

    result = await generator.generate_answer_async("How do I solve Two Sum?", n_context=1)

    assert result.query_variants
    assert len(result.citations) == 1
    assert result.citations[0]["title"] == "Two Sum"
    assert "hash map" in result.answer.lower()


@pytest.mark.asyncio
async def test_grade_answer_fallback_parsing():
    class _BadJsonLLM:
        async def generate_with_retry_async(self, prompt: str, max_tokens: int, temperature: float):
            return _FakeLLMResponse("Not valid JSON, but useful feedback")

    generator = RAGGenerator(llm_service=_BadJsonLLM(), vector_store=_FakeVectorStore(), use_reranker=False)
    grading = await generator.grade_answer_async("Two Sum", "I'd use brute force")

    assert "overall" in grading
    assert grading["overall"] == 0.6
