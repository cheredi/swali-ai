"""
Unit Tests for Embeddings Module

🎓 LEARNING NOTE: Testing Embeddings
====================================
When testing embedding systems, we verify:
1. Output shape is correct (dimension matches model spec)
2. Determinism (same input → same output)
3. Semantic similarity (similar texts → similar vectors)
4. Batching works correctly
"""


import pytest


class TestEmbeddingService:
    """Tests for the EmbeddingService class."""

    def test_embed_text_returns_list(self):
        """Verify embed_text returns a list of floats."""
        # Import here to avoid loading model during collection
        from app.rag.embeddings import embed

        result = embed("Test sentence")

        assert isinstance(result, list)
        assert all(isinstance(x, float) for x in result)

    def test_embed_text_dimension(self):
        """Verify embedding dimension matches model spec (384 for MiniLM)."""
        from app.rag.embeddings import EmbeddingService, embed

        result = embed("Test sentence")
        expected_dim = EmbeddingService.get_dimension()

        assert len(result) == expected_dim

    def test_embed_text_deterministic(self):
        """Same input should produce same output."""
        from app.rag.embeddings import embed

        text = "Determinism test"
        result1 = embed(text)
        result2 = embed(text)

        assert result1 == result2

    def test_embed_batch_returns_correct_count(self):
        """Batch embedding should return one embedding per input."""
        from app.rag.embeddings import embed_batch

        texts = ["First text", "Second text", "Third text"]
        results = embed_batch(texts)

        assert len(results) == len(texts)

    def test_similar_texts_have_similar_embeddings(self):
        """Semantically similar texts should have similar embeddings."""
        import numpy as np
        from app.rag.embeddings import embed

        # Similar topics
        text1 = "How to reverse a linked list"
        text2 = "Reversing a singly linked list algorithm"
        text3 = "Design a distributed cache system"

        emb1 = np.array(embed(text1))
        emb2 = np.array(embed(text2))
        emb3 = np.array(embed(text3))

        # Cosine similarity
        def cosine_sim(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        sim_1_2 = cosine_sim(emb1, emb2)
        sim_1_3 = cosine_sim(emb1, emb3)

        # Similar topics should have higher similarity
        assert sim_1_2 > sim_1_3, f"Similar texts should have higher similarity: {sim_1_2} vs {sim_1_3}"

    def test_empty_string_handling(self):
        """Empty strings should not crash."""
        from app.rag.embeddings import embed

        result = embed("")
        assert isinstance(result, list)
        assert len(result) > 0  # Should still return valid embedding


class TestEmbeddingPerformance:
    """Performance-related tests (marked slow)."""

    @pytest.mark.slow
    def test_batch_faster_than_individual(self):
        """Batching should be faster than individual embedding."""
        import time

        from app.rag.embeddings import embed, embed_batch

        texts = [f"Test sentence number {i}" for i in range(100)]

        # Individual
        start = time.time()
        [embed(t) for t in texts]
        individual_time = time.time() - start

        # Batch
        start = time.time()
        embed_batch(texts)
        batch_time = time.time() - start

        assert batch_time < individual_time, "Batching should be faster"
