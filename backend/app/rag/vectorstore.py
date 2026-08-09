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

import asyncio
import math
import re
from collections import Counter
from typing import Any, Optional, cast

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
        self.collection.add(  # type: ignore[arg-type]
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f" Added {len(documents)} documents to vector store")

    def add_documents_with_embeddings(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
        embeddings: list[list[float]],
    ) -> None:
        """
        Add documents with pre-computed embeddings.

        LEARNING NOTE: Why this method?
        -------------------------------
        Experiment pipelines often compute embeddings with different models.
        This method allows direct insertion without re-embedding through the
        default model.
        """
        self.collection.add(  # type: ignore[arg-type]
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        print(f" Added {len(documents)} documents with pre-computed embeddings")

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
        results = self.collection.query(  # type: ignore[arg-type]
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"]
        )
        return cast(dict[str, Any], results)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[a-z0-9_+#.-]+", text.lower())

    def search_keyword(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Sparse lexical retrieval using lightweight BM25-style scoring."""
        records = cast(dict[str, Any], self.collection.get(include=["documents", "metadatas"]))  # type: ignore[arg-type]
        ids = records.get("ids", []) or []
        documents = records.get("documents", []) or []
        metadatas = records.get("metadatas", []) or []

        if not ids:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        query_terms = self._tokenize(query)
        if not query_terms:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        doc_term_freqs: list[Counter] = []
        doc_lengths: list[int] = []
        filtered: list[tuple[str, str, dict[str, Any]]] = []

        for doc_id, document, metadata in zip(ids, documents, metadatas):
            if where and any(str(metadata.get(k)) != str(v) for k, v in where.items()):
                continue
            tokens = self._tokenize(f"{metadata.get('title', '')} {document}")
            tf = Counter(tokens)
            doc_term_freqs.append(tf)
            doc_lengths.append(len(tokens) or 1)
            filtered.append((doc_id, document, metadata))

        total_docs = len(filtered)
        if total_docs == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        avg_doc_len = sum(doc_lengths) / total_docs
        k1 = 1.5
        b = 0.75

        doc_freq: Counter = Counter()
        for tf in doc_term_freqs:
            for term in set(query_terms):
                if term in tf:
                    doc_freq[term] += 1

        scored: list[tuple[float, str, str, dict[str, Any]]] = []
        for idx, (doc_id, document, metadata) in enumerate(filtered):
            score = 0.0
            tf = doc_term_freqs[idx]
            doc_len = doc_lengths[idx]
            for term in query_terms:
                if tf[term] == 0:
                    continue
                idf = math.log((total_docs - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5) + 1.0)
                denom = tf[term] + k1 * (1 - b + b * (doc_len / (avg_doc_len or 1)))
                score += idf * ((tf[term] * (k1 + 1)) / (denom or 1))
            if score > 0:
                distance = 1.0 / (1.0 + score)
                scored.append((score, doc_id, document, metadata | {"keyword_score": round(score, 4)}))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected = scored[:n_results]
        return {
            "ids": [[item[1] for item in selected]],
            "documents": [[item[2] for item in selected]],
            "metadatas": [[item[3] for item in selected]],
            "distances": [[1.0 / (1.0 + item[0]) for item in selected]],
        }

    def search_hybrid(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[dict] = None,
        dense_weight: float = 0.65,
    ) -> dict[str, Any]:
        """Hybrid retrieval by combining dense and sparse rank signals."""
        candidate_pool = max(n_results * 4, n_results)
        dense = self.search(query=query, n_results=candidate_pool, where=where)
        sparse = self.search_keyword(query=query, n_results=candidate_pool, where=where)

        scored: dict[str, dict[str, Any]] = {}

        for rank, (doc_id, doc, metadata, distance) in enumerate(
            zip(
                dense.get("ids", [[]])[0],
                dense.get("documents", [[]])[0],
                dense.get("metadatas", [[]])[0],
                dense.get("distances", [[]])[0],
            ),
            start=1,
        ):
            score = dense_weight * (1.0 / (60 + rank)) + (1 - dense_weight) * (1.0 / (1.0 + float(distance)))
            scored[doc_id] = {
                "id": doc_id,
                "doc": doc,
                "metadata": metadata,
                "distance": float(distance),
                "score": score,
            }

        for rank, (doc_id, doc, metadata, distance) in enumerate(
            zip(
                sparse.get("ids", [[]])[0],
                sparse.get("documents", [[]])[0],
                sparse.get("metadatas", [[]])[0],
                sparse.get("distances", [[]])[0],
            ),
            start=1,
        ):
            score = (1 - dense_weight) * (1.0 / (60 + rank)) + dense_weight * (1.0 / (1.0 + float(distance)))
            if doc_id in scored:
                scored[doc_id]["score"] += score
                scored[doc_id]["metadata"] = {**scored[doc_id]["metadata"], **metadata}
                scored[doc_id]["distance"] = min(scored[doc_id]["distance"], float(distance))
            else:
                scored[doc_id] = {
                    "id": doc_id,
                    "doc": doc,
                    "metadata": metadata,
                    "distance": float(distance),
                    "score": score,
                }

        ranked = sorted(scored.values(), key=lambda item: item["score"], reverse=True)[:n_results]
        return {
            "ids": [[row["id"] for row in ranked]],
            "documents": [[row["doc"] for row in ranked]],
            "metadatas": [[row["metadata"] for row in ranked]],
            "distances": [[row["distance"] for row in ranked]],
            "scores": [[row["score"] for row in ranked]],
        }

    async def search_hybrid_async(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[dict] = None,
        dense_weight: float = 0.65,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(
            self.search_hybrid,
            query,
            n_results,
            where,
            dense_weight,
        )

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
        results = self.collection.query(  # type: ignore[arg-type]
            query_embeddings=[embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        return cast(dict[str, Any], results)

    def get_by_id(self, doc_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a specific document by ID."""
        result = cast(dict[str, Any], self.collection.get(  # type: ignore[arg-type]
            ids=[doc_id],
            include=["documents", "metadatas"]
        ))
        if result["ids"]:
            documents = result.get("documents") or []
            metadatas = result.get("metadatas") or []
            return {
                "id": result["ids"][0],
                "document": documents[0] if documents else "",
                "metadata": metadatas[0] if metadatas else {},
            }
        return None

    def get_all(self) -> dict[str, Any]:
        """Return all documents, metadata, and IDs from the collection."""
        return cast(dict[str, Any], self.collection.get(include=["documents", "metadatas"]))  # type: ignore[arg-type]

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
