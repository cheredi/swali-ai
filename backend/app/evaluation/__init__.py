"""
Evaluation Framework for Swali-AI

🎓 LEARNING NOTE: Evaluating RAG Systems
=========================================
Unlike traditional software, RAG systems need quality metrics:

1. RETRIEVAL METRICS
   - Recall@k: What fraction of relevant docs are in top-k?
   - MRR (Mean Reciprocal Rank): Where does the first relevant doc appear?
   - Precision@k: What fraction of top-k are relevant?

2. GENERATION METRICS
   - Faithfulness: Is the answer grounded in retrieved context?
   - Relevance: Does the answer address the question?
   - Helpfulness: Is the explanation clear and educational?

3. END-TO-END METRICS
   - Answer accuracy: Does the answer match ground truth?
   - User satisfaction: Would a user find this helpful?

This module provides tools to measure these metrics.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class EvaluationCase:
    """
    A single evaluation test case.

    🎓 LEARNING NOTE: Building Evaluation Sets
    Good evaluation requires curated test cases with:
    - Input query
    - Expected relevant documents (for retrieval eval)
    - Expected answer or key points (for generation eval)
    """
    query: str
    expected_doc_ids: list[str] = field(default_factory=list)
    expected_answer_contains: list[str] = field(default_factory=list)
    difficulty: str = "medium"
    category: str = "general"

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "expected_doc_ids": self.expected_doc_ids,
            "expected_answer_contains": self.expected_answer_contains,
            "difficulty": self.difficulty,
            "category": self.category
        }


@dataclass
class RetrievalResult:
    """Result of a retrieval evaluation."""
    query: str
    retrieved_ids: list[str]
    expected_ids: list[str]
    recall_at_k: float
    precision_at_k: float
    mrr: float
    k: int


@dataclass
class EvaluationRun:
    """A complete evaluation run with multiple test cases."""
    run_id: str
    timestamp: datetime
    config: dict[str, Any]
    results: list[RetrievalResult] = field(default_factory=list)

    def summary(self) -> dict:
        """Get aggregate metrics."""
        if not self.results:
            return {}

        return {
            "run_id": self.run_id,
            "num_cases": len(self.results),
            "avg_recall": sum(r.recall_at_k for r in self.results) / len(self.results),
            "avg_precision": sum(r.precision_at_k for r in self.results) / len(self.results),
            "avg_mrr": sum(r.mrr for r in self.results) / len(self.results),
        }


class RetrievalEvaluator:
    """
    Evaluates retrieval quality.

    🎓 LEARNING NOTE: Retrieval Evaluation
    The key insight: retrieval is a ranking problem.
    We want relevant documents ranked HIGHER than irrelevant ones.
    """

    @staticmethod
    def recall_at_k(retrieved_ids: list[str], expected_ids: list[str], k: int) -> float:
        """
        Recall@k: What fraction of expected documents appear in top-k retrieved?

        Formula: |Retrieved ∩ Expected| / |Expected|

        Example:
            Retrieved top-5: [A, B, C, D, E]
            Expected: [A, C, F]
            Recall@5 = 2/3 = 0.67 (found A and C, missed F)
        """
        if not expected_ids:
            return 1.0  # If no expected docs, consider it a success

        # Type hint for slicing result to satisfy strict checkers
        retrieved_slice = list(retrieved_ids)[:k]
        retrieved_set = set(retrieved_slice)
        expected_set = set(expected_ids)

        hits = len(retrieved_set & expected_set)
        return hits / len(expected_set)

    @staticmethod
    def precision_at_k(retrieved_ids: list[str], expected_ids: list[str], k: int) -> float:
        """
        Precision@k: What fraction of top-k retrieved are relevant?

        Formula: |Retrieved ∩ Expected| / k

        Example:
            Retrieved top-5: [A, B, C, D, E]
            Expected: [A, C]
            Precision@5 = 2/5 = 0.4
        """
        # Explicitly handling the slice as a list to satisfy strict type checking
        retrieved_slice = list(retrieved_ids)[:k]
        retrieved_set = set(retrieved_slice)
        expected_set = set(expected_ids)

        hits = len(retrieved_set & expected_set)
        return hits / k

    @staticmethod
    def mrr(retrieved_ids: list[str], expected_ids: list[str]) -> float:
        """
        Mean Reciprocal Rank: 1 / position of first relevant result.

        Example:
            Retrieved: [X, Y, A, Z]  (A is relevant)
            MRR = 1/3 = 0.33 (first relevant at position 3)
        """
        expected_set = set(expected_ids)

        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_set:
                return 1.0 / (i + 1)

        return 0.0  # No relevant document found

    def evaluate(
        self,
        test_cases: list[EvaluationCase],
        retrieval_fn,  # Function that takes query and returns list of doc IDs
        k: int = 5
    ) -> EvaluationRun:
        """
        Run evaluation on a set of test cases.

        Args:
            test_cases: List of evaluation cases
            retrieval_fn: Function(query) -> List[doc_ids]
            k: Number of results to evaluate
        """
        run = EvaluationRun(
            run_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            timestamp=datetime.now(),
            config={"k": k, "num_cases": len(test_cases)}
        )

        for case in test_cases:
            retrieved = retrieval_fn(case.query)

            result = RetrievalResult(
                query=case.query,
                retrieved_ids=retrieved[:k],
                expected_ids=case.expected_doc_ids,
                recall_at_k=self.recall_at_k(retrieved, case.expected_doc_ids, k),
                precision_at_k=self.precision_at_k(retrieved, case.expected_doc_ids, k),
                mrr=self.mrr(retrieved, case.expected_doc_ids),
                k=k
            )
            run.results.append(result)

        return run


class ExperimentTracker:
    """
    Tracks experiments for comparison.

    🎓 LEARNING NOTE: Why Track Experiments?
    When tuning RAG systems, you'll try many variations:
    - Different embedding models
    - Different chunk sizes
    - Different prompts

    Tracking helps you know what actually improved performance.
    """

    def __init__(self, output_dir: str = "./experiments"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log_run(self, run: EvaluationRun, notes: str = "") -> str:
        """Save an evaluation run to disk."""
        output_file = self.output_dir / f"run_{run.run_id}.json"

        data = {
            "run_id": run.run_id,
            "timestamp": run.timestamp.isoformat(),
            "config": run.config,
            "summary": run.summary(),
            "notes": notes,
            "results": [
                {
                    "query": r.query,
                    "recall": r.recall_at_k,
                    "precision": r.precision_at_k,
                    "mrr": r.mrr
                }
                for r in run.results
            ]
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        return str(output_file)

    def compare_runs(self, run_ids: list[str]) -> dict:
        """Load and compare multiple runs."""
        runs = []
        for run_id in run_ids:
            run_file = self.output_dir / f"run_{run_id}.json"
            if run_file.exists():
                with open(run_file) as f:
                    runs.append(json.load(f))

        return {
            "runs": [
                {
                    "run_id": r["run_id"],
                    "summary": r["summary"],
                    "notes": r.get("notes", "")
                }
                for r in runs
            ]
        }


# Example evaluation cases for testing
SAMPLE_EVAL_CASES = [
    EvaluationCase(
        query="How do I find two numbers that add up to a target?",
        expected_doc_ids=["lc_1"],  # Two Sum
        expected_answer_contains=["hash map", "O(n)", "complement"],
        difficulty="easy",
        category="array"
    ),
    EvaluationCase(
        query="What's the best way to detect a cycle in a linked list?",
        expected_doc_ids=["lc_141"],  # Linked List Cycle
        expected_answer_contains=["two pointers", "fast", "slow", "Floyd"],
        difficulty="easy",
        category="linked_list"
    ),
    EvaluationCase(
        query="How would you design a URL shortening service?",
        expected_doc_ids=["sd_url_shortener"],
        expected_answer_contains=["base62", "hash", "database", "cache"],
        difficulty="medium",
        category="system_design"
    ),
]


if __name__ == "__main__":
    # Demo the evaluation framework
    print("🧪 Evaluation Framework Demo\n")

    evaluator = RetrievalEvaluator()

    # Mock retrieval function for demo
    def mock_retrieval(query: str) -> list[str]:
        return ["lc_1", "lc_15", "lc_167", "lc_1"]

    # Run evaluation
    run = evaluator.evaluate(list(SAMPLE_EVAL_CASES)[:1], mock_retrieval, k=3)

    print(f"Run ID: {run.run_id}")
    print(f"Summary: {run.summary()}")
