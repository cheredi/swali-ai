"""
Run retrieval experiments for Swali-AI.

Experiments included:
1) Baseline retrieval vs reranked retrieval
2) Embedding model A/B comparison

LEARNING NOTE: Evaluation mindset
---------------------------------
Always compare one controlled change at a time and log metrics to disk.
This avoids intuition-driven tuning and keeps improvements reproducible.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports from backend/app
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import settings
from app.evaluation import EvaluationCase, ExperimentTracker, RetrievalEvaluator
from app.rag.embeddings import EmbeddingService
from app.rag.reranker import HybridReranker
from app.rag.vectorstore import VectorStore


def build_eval_cases() -> list[EvaluationCase]:
    """Small deterministic evaluation set against known IDs."""
    return [
        EvaluationCase(
            query="How do I solve two sum in linear time?",
            expected_doc_ids=["nc_1"],
            category="arrays_hashing",
            difficulty="easy",
        ),
        EvaluationCase(
            query="How can I detect a cycle in a linked list?",
            expected_doc_ids=["nc_141"],
            category="linked_list",
            difficulty="easy",
        ),
        EvaluationCase(
            query="Design a tinyurl style URL shortening system",
            expected_doc_ids=["sd_url_shortener"],
            category="system_design",
            difficulty="medium",
        ),
        EvaluationCase(
            query="How do I check if an array has duplicates quickly?",
            expected_doc_ids=["nc_217"],
            category="arrays_hashing",
            difficulty="easy",
        ),
    ]


def make_retrieval_fn(store: VectorStore, n_results: int = 20):
    def retrieval_fn(query: str) -> list[str]:
        results = store.search(query=query, n_results=n_results)
        return list(results["ids"][0])

    return retrieval_fn


def make_reranked_retrieval_fn(store: VectorStore, reranker: HybridReranker, n_results: int = 20):
    def retrieval_fn(query: str) -> list[str]:
        raw_results = store.search(query=query, n_results=n_results)
        reranked = reranker.rerank_search_results(query=query, search_results=raw_results, top_k=n_results)
        return list(reranked["ids"][0])

    return retrieval_fn


def build_model_specific_collection(
    source_store: VectorStore,
    model_name: str,
    collection_name: str,
) -> VectorStore:
    """
    Build a temporary collection with embeddings from a specified model.

    LEARNING NOTE: Fair embedding comparisons
    ----------------------------------------
    Query-time model swaps alone are not fair. We must embed both documents and
    queries with the same model to evaluate retrieval quality correctly.
    """
    all_data = source_store.get_all()
    ids = list(all_data.get("ids", []))
    documents = list(all_data.get("documents", []))
    metadatas = list(all_data.get("metadatas", []))

    if not ids:
        raise RuntimeError("Source collection is empty. Run process_data.py first.")

    embeddings = EmbeddingService.embed_batch_with_model(documents, model_name)

    target_store = VectorStore(collection_name)
    target_store.delete_all()
    target_store.add_documents_with_embeddings(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings,
    )
    return target_store


def main() -> None:
    evaluator = RetrievalEvaluator()
    tracker = ExperimentTracker("./experiments")
    cases = build_eval_cases()

    baseline_store = VectorStore("problems")
    reranker = HybridReranker()

    baseline_run = evaluator.evaluate(
        test_cases=cases,
        retrieval_fn=make_retrieval_fn(baseline_store),
        k=5,
    )
    baseline_run.config.update(
        {
            "experiment": "baseline_retrieval",
            "collection": "problems",
            "embedding_model": settings.embedding_model,
            "reranker": False,
        }
    )
    baseline_file = tracker.log_run(baseline_run, notes="Baseline vector retrieval")

    reranked_run = evaluator.evaluate(
        test_cases=cases,
        retrieval_fn=make_reranked_retrieval_fn(baseline_store, reranker),
        k=5,
    )
    reranked_run.config.update(
        {
            "experiment": "reranked_retrieval",
            "collection": "problems",
            "embedding_model": settings.embedding_model,
            "reranker": True,
        }
    )
    reranked_file = tracker.log_run(reranked_run, notes="Hybrid semantic+lexical reranking")

    # Embedding A/B comparison
    model_a = settings.embedding_model
    model_b = "all-MiniLM-L12-v2"

    store_a = build_model_specific_collection(
        source_store=baseline_store,
        model_name=model_a,
        collection_name="exp_embed_a",
    )
    store_b = build_model_specific_collection(
        source_store=baseline_store,
        model_name=model_b,
        collection_name="exp_embed_b",
    )

    run_a = evaluator.evaluate(cases, make_retrieval_fn(store_a), k=5)
    run_a.run_id = f"{run_a.run_id}_embedA"
    run_a.config.update(
        {
            "experiment": "embedding_ab",
            "variant": "A",
            "embedding_model": model_a,
            "collection": "exp_embed_a",
        }
    )
    run_a_file = tracker.log_run(run_a, notes="Embedding model A")

    run_b = evaluator.evaluate(cases, make_retrieval_fn(store_b), k=5)
    run_b.run_id = f"{run_b.run_id}_embedB"
    run_b.config.update(
        {
            "experiment": "embedding_ab",
            "variant": "B",
            "embedding_model": model_b,
            "collection": "exp_embed_b",
        }
    )
    run_b_file = tracker.log_run(run_b, notes="Embedding model B")

    print("\n=== Retrieval Experiment Summary ===")
    print(f"Baseline run: {baseline_file}")
    print(f"Reranked run: {reranked_file}")
    print(f"Embedding A run: {run_a_file}")
    print(f"Embedding B run: {run_b_file}")
    print("\nBaseline summary:", baseline_run.summary())
    print("Reranked summary:", reranked_run.summary())
    print("Embedding A summary:", run_a.summary())
    print("Embedding B summary:", run_b.summary())


if __name__ == "__main__":
    main()