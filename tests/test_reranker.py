"""Tests for hybrid reranking behavior."""

from app.rag.reranker import HybridReranker


def test_reranker_promotes_lexically_matching_result() -> None:
    reranker = HybridReranker(semantic_weight=0.6, lexical_weight=0.4)
    query = "two sum hash map"

    search_results = {
        "ids": [["doc_semantic", "doc_lexical"]],
        "documents": [[
            "array pair problem",
            "two sum using hash map in one pass",
        ]],
        "metadatas": [[
            {"title": "Pair search"},
            {"title": "Two Sum"},
        ]],
        "distances": [[0.20, 0.30]],
    }

    reranked = reranker.rerank_search_results(query=query, search_results=search_results, top_k=2)

    assert reranked["ids"][0][0] == "doc_lexical"


def test_reranker_respects_top_k() -> None:
    reranker = HybridReranker()
    query = "linked list cycle"

    search_results = {
        "ids": [["a", "b", "c"]],
        "documents": [["doc a", "doc b", "doc c"]],
        "metadatas": [[{"title": "A"}, {"title": "B"}, {"title": "C"}]],
        "distances": [[0.2, 0.3, 0.4]],
    }

    reranked = reranker.rerank_search_results(query=query, search_results=search_results, top_k=1)

    assert len(reranked["ids"][0]) == 1
