"""
Unit Tests for Vector Store Module

🎓 LEARNING NOTE: Testing Vector Stores
=======================================
Vector store tests verify:
1. CRUD operations work correctly
2. Search returns relevant results
3. Metadata filtering works
4. Edge cases (empty store, duplicate IDs)
"""


import pytest


class TestVectorStore:
    """Tests for the VectorStore class."""

    @pytest.fixture
    def temp_store(self):
        """Create a temporary vector store for testing."""
        # Use a temp directory to avoid polluting real data
        import tempfile

        from app.config import settings
        from app.rag.vectorstore import VectorStore

        with tempfile.TemporaryDirectory() as tmpdir:
            # Override the persist directory
            original_dir = settings.chroma_persist_dir
            settings.chroma_persist_dir = tmpdir

            store = VectorStore("test_collection")
            yield store

            # Cleanup
            settings.chroma_persist_dir = original_dir

    def test_add_and_count(self, temp_store):
        """Adding documents should increase count."""
        initial_count = temp_store.count()

        temp_store.add_documents(
            documents=["Test document one", "Test document two"],
            metadatas=[{"type": "test"}, {"type": "test"}],
            ids=["doc1", "doc2"]
        )

        assert temp_store.count() == initial_count + 2

    def test_search_returns_results(self, temp_store):
        """Search should return results in expected format."""
        temp_store.add_documents(
            documents=["How to implement binary search"],
            metadatas=[{"difficulty": "easy"}],
            ids=["bs_1"]
        )

        results = temp_store.search("binary search algorithm", n_results=1)

        assert "ids" in results
        assert "documents" in results
        assert "distances" in results
        assert len(results["ids"][0]) == 1

    def test_search_returns_relevant_results(self, temp_store):
        """Search should return semantically relevant documents."""
        temp_store.add_documents(
            documents=[
                "Implement a stack using two queues",
                "Find the maximum element in an array",
                "Design a Twitter-like social media platform"
            ],
            metadatas=[
                {"category": "stack"},
                {"category": "array"},
                {"category": "system_design"}
            ],
            ids=["q1", "q2", "q3"]
        )

        results = temp_store.search("data structure with LIFO", n_results=1)

        # Should return the stack question
        assert results["metadatas"][0][0]["category"] == "stack"

    def test_metadata_filtering(self, temp_store):
        """Search should respect metadata filters."""
        temp_store.add_documents(
            documents=[
                "Easy array problem about two sum",
                "Hard dynamic programming challenge"
            ],
            metadatas=[
                {"difficulty": "easy"},
                {"difficulty": "hard"}
            ],
            ids=["easy_1", "hard_1"]
        )

        results = temp_store.search(
            "algorithm problem",
            n_results=5,
            where={"difficulty": "easy"}
        )

        # Should only return easy problems
        assert all(m["difficulty"] == "easy" for m in results["metadatas"][0])

    def test_get_by_id(self, temp_store):
        """Should retrieve specific document by ID."""
        temp_store.add_documents(
            documents=["Specific document content"],
            metadatas=[{"title": "Test Title"}],
            ids=["specific_id"]
        )

        result = temp_store.get_by_id("specific_id")

        assert result is not None
        assert result["id"] == "specific_id"
        assert result["metadata"]["title"] == "Test Title"

    def test_get_nonexistent_id_returns_none(self, temp_store):
        """Getting non-existent ID should return None."""
        result = temp_store.get_by_id("does_not_exist")
        assert result is None

    def test_delete_all(self, temp_store):
        """delete_all should remove all documents."""
        temp_store.add_documents(
            documents=["Doc 1", "Doc 2"],
            metadatas=[{"id": 1}, {"id": 2}],
            ids=["d1", "d2"]
        )

        assert temp_store.count() == 2

        temp_store.delete_all()

        assert temp_store.count() == 0
