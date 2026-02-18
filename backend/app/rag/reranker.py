"""
Reranking utilities for retrieval results.

LEARNING NOTE: Why rerank?
--------------------------
Vector retrieval is good at recall (finding candidates), but it can return
near-miss items in top positions. A reranker re-orders candidates using
additional signals to improve precision in top-k.
"""

from __future__ import annotations

import re
from typing import Any


class HybridReranker:
    """
    Re-ranks candidates with hybrid scoring.

    Score combines:
    - semantic signal from vector distance
    - lexical overlap between query and document/title text
    """

    def __init__(self, semantic_weight: float = 0.7, lexical_weight: float = 0.3):
        self.semantic_weight = semantic_weight
        self.lexical_weight = lexical_weight

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        return {token for token in tokens if len(token) > 1}

    def _lexical_overlap(self, query: str, doc_text: str) -> float:
        query_tokens = self._tokenize(query)
        doc_tokens = self._tokenize(doc_text)

        if not query_tokens or not doc_tokens:
            return 0.0

        intersection = len(query_tokens & doc_tokens)
        return intersection / len(query_tokens)

    def rerank_search_results(
        self,
        query: str,
        search_results: dict[str, Any],
        top_k: int,
    ) -> dict[str, Any]:
        """
        Re-order Chroma-style search results and keep only top_k.

        LEARNING NOTE: Distance handling
        -------------------------------
        Chroma returns distances where lower is better. We convert distance into
        a semantic score by negating it, so higher total score means better rank.
        """
        if not search_results.get("ids") or not search_results["ids"][0]:
            return search_results

        candidates = []
        for index, (doc_id, document, metadata, distance) in enumerate(
            zip(
                search_results["ids"][0],
                search_results["documents"][0],
                search_results["metadatas"][0],
                search_results["distances"][0],
            )
        ):
            title = str(metadata.get("title", ""))
            lexical = self._lexical_overlap(query, f"{title} {document}")
            semantic = -float(distance)
            score = (self.semantic_weight * semantic) + (self.lexical_weight * lexical)

            candidates.append(
                {
                    "idx": index,
                    "id": doc_id,
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                    "score": score,
                }
            )

        candidates.sort(key=lambda candidate: candidate["score"], reverse=True)
        selected = candidates[:top_k]

        return {
            "ids": [[candidate["id"] for candidate in selected]],
            "documents": [[candidate["document"] for candidate in selected]],
            "metadatas": [[candidate["metadata"] for candidate in selected]],
            "distances": [[candidate["distance"] for candidate in selected]],
        }
