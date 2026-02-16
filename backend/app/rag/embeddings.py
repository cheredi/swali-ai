"""
Embeddings Module for Swali-AI

🎓 LEARNING NOTE: What are Embeddings?
=====================================
Embeddings are dense vector representations of text that capture semantic meaning.
Similar concepts have similar embeddings (close in vector space).

Example:
  - "Two Sum" problem → [0.12, -0.34, 0.56, ...]  (384 dimensions)
  - "Add Two Numbers" → [0.11, -0.32, 0.58, ...]  (similar vector!)
  - "Binary Search Tree" → [0.78, 0.21, -0.15, ...] (different vector)

Why sentence-transformers?
- Free to use (no API costs)
- Runs locally (no network latency)
- all-MiniLM-L6-v2 is fast and good quality for retrieval tasks
"""

from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.

    LEARNING NOTE: Singleton Pattern
    We use a class-level model to avoid loading the model multiple times.
    Loading happens once, then the model stays in memory for fast inference.
    """

    _model: SentenceTransformer = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Load model lazily (only when first needed)."""
        if cls._model is None:
            print(f"Loading embedding model: {settings.embedding_model}")
            cls._model = SentenceTransformer(settings.embedding_model)
            print(f"Model loaded! Dimension: {cls._model.get_sentence_embedding_dimension()}")
        return cls._model

    @classmethod
    def embed_text(cls, text: str) -> list[float]:
        """
        Convert a single text string into an embedding vector.

        Args:
            text: The text to embed

        Returns:
            A list of floats representing the embedding vector

        LEARNING NOTE: Why List[float]?
        ChromaDB and most vector stores expect Python lists, not numpy arrays.
        We convert here to avoid issues downstream.
        """
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    @classmethod
    def embed_batch(cls, texts: list[str]) -> list[list[float]]:
        """
        Convert multiple texts into embeddings efficiently.

        🎓 LEARNING NOTE: Batching
        Processing multiple texts together is MUCH faster than one at a time.
        The model can parallelize operations on the GPU/CPU.

        For 100 texts:
        - One at a time: ~10 seconds
        - Batched: ~1 second
        """
        model = cls.get_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()

    @classmethod
    def get_dimension(cls) -> int:
        """Get the embedding dimension (useful for vector store setup)."""
        model = cls.get_model()
        return model.get_sentence_embedding_dimension()


# Convenience functions for quick access
def embed(text: str) -> list[float]:
    """Quick function to embed a single text."""
    return EmbeddingService.embed_text(text)


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Quick function to embed multiple texts."""
    return EmbeddingService.embed_batch(texts)


# Example usage and testing
if __name__ == "__main__":
    # Test the embedding service
    print("🧪 Testing Embedding Service\n")

    test_texts = [
        "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "You are given two non-empty linked lists representing two non-negative integers.",
        "Design a system that can handle millions of requests per second."
    ]

    print("Generating embeddings for test texts...")
    embeddings = embed_batch(test_texts)

    print("\n Results:")
    print(f"   Number of embeddings: {len(embeddings)}")
    print(f"   Embedding dimension: {len(embeddings[0])}")

    # Show similarity between first two (both are array/math problems)
    from numpy import dot
    from numpy.linalg import norm

    def cosine_similarity(a, b):
        return dot(a, b) / (norm(a) * norm(b))

    sim_1_2 = cosine_similarity(embeddings[0], embeddings[1])
    sim_1_3 = cosine_similarity(embeddings[0], embeddings[2])

    print("\n Similarity Analysis:")
    print(f"   Two Sum ↔ Add Two Numbers: {sim_1_2:.3f} (similar - both are number problems)")
    print(f"   Two Sum ↔ System Design:   {sim_1_3:.3f} (different domains)")
