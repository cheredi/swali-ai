"""
Vector Store Module for Swali-AI

🎓 LEARNING NOTE: What is a Vector Store?
=========================================
A vector store (or vector database) is optimized for:
1. Storing high-dimensional vectors efficiently
2. Finding similar vectors FAST using approximate nearest neighbor (ANN) algorithms

Traditional DB: "Find all users where name = 'John'"
Vector DB: "Find the 5 vectors most similar to this query vector"

Why ChromaDB?
- Simple API, great for learning
- Runs locally (no cloud setup)
- Persistent storage (survives restarts)
- Supports metadata filtering
"""

from typing import Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.rag.embeddings import EmbeddingService


class VectorStore:
    """
    Vector store interface using ChromaDB.

    LEARNING NOTE: Collections
    ChromaDB organizes data into "collections" (like tables in SQL).
    Each collection stores documents with:
    - id: Unique identifier
    - embedding: The vector representation
    - document: The original text
    - metadata: Additional info (difficulty, tags, etc.)
    """

    def __init__(self, collection_name: str = "problems"):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the ChromaDB collection
        """
        # Create persistent client (data survives restarts)
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        # Get or create the collection
        # 🎓 NOTE: We don't specify an embedding function because
        # we'll provide pre-computed embeddings ourselves
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Interview preparation problems"}
        )

        print(f"Vector store initialized: {collection_name}")
        print(f"Current document count: {self.collection.count()}")

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str]
    ) -> None:
        """
        Add documents to the vector store.

       LEARNING NOTE: Document Ingestion Pipeline
        1. Take raw text documents
        2. Generate embeddings for each
        3. Store (id, embedding, text, metadata) together

        Args:
            documents: List of text content
            metadatas: List of metadata dicts (must match documents length)
            ids: List of unique IDs (must match documents length)
        """
        # Generate embeddings for all documents
        print(f"Generating embeddings for {len(documents)} documents...")
        embeddings = EmbeddingService.embed_batch(documents)

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f" Added {len(documents)} documents to vector store")

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[dict] = None,
        where_document: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Search for similar documents.

        LEARNING NOTE: Semantic Search
        Unlike keyword search, this finds documents by MEANING, not exact words.

        Query: "How do I find if an array has duplicate elements?"
        Might return: "Contains Duplicate" problem (even without word "duplicate")

        Args:
            query: The search query
            n_results: Number of results to return
            where: Metadata filter (e.g., {"difficulty": "easy"})
            where_document: Document content filter

        Returns:
            Dict with 'ids', 'documents', 'metadatas', 'distances'
        """
        # Generate embedding for the query
        query_embedding = EmbeddingService.embed_text(query)

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"]
        )

        return results

    def search_by_embedding(
        self,
        embedding: list[float],
        n_results: int = 5,
        where: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Search using a pre-computed embedding.

        LEARNING NOTE: When to use this?
        - Finding similar problems to one you've already embedded
        - Re-ranking results with modified embeddings
        - Query expansion (averaging multiple query embeddings)
        """
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        return results

    def get_by_id(self, doc_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a specific document by ID."""
        result = self.collection.get(
            ids=[doc_id],
            include=["documents", "metadatas"]
        )
        if result["ids"]:
            return {
                "id": result["ids"][0],
                "document": result["documents"][0],
                "metadata": result["metadatas"][0]
            }
        return None

    def delete_all(self) -> None:
        """Clear all documents (useful for re-indexing)."""
        # Get all IDs first
        all_data = self.collection.get()
        if all_data["ids"]:
            self.collection.delete(ids=all_data["ids"])
            print(f"🗑️ Deleted {len(all_data['ids'])} documents")

    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self.collection.count()


# Global instance for easy access
_vector_store: Optional[VectorStore] = None


def get_vector_store(collection_name: str = "problems") -> VectorStore:
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(collection_name)
    return _vector_store


# Example usage
if __name__ == "__main__":
    print("🧪 Testing Vector Store\n")

    # Create a test collection
    store = VectorStore("test_collection")

    # Add some test documents
    test_docs = [
        "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "Given a string s, find the length of the longest substring without repeating characters.",
        "Design a URL shortening service like TinyURL.",
    ]

    test_metadata = [
        {"title": "Two Sum", "difficulty": "easy", "category": "array"},
        {"title": "Longest Substring", "difficulty": "medium", "category": "string"},
        {"title": "URL Shortener", "difficulty": "medium", "category": "system_design"},
    ]

    test_ids = ["lc_1", "lc_3", "sd_url"]

    # Clear and re-add
    store.delete_all()
    store.add_documents(test_docs, test_metadata, test_ids)

    # Test search
    print("\n🔍 Searching for 'find pair of numbers that sum to target'...")
    results = store.search("find pair of numbers that sum to target", n_results=2)

    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"\n  Result {i+1}:")
        print(f"    Title: {meta['title']}")
        print(f"    Distance: {dist:.4f}")
        print(f"    Preview: {doc[:80]}...")
