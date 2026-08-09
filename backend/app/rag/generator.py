"""
RAG Generator for Swali-AI

LEARNING NOTE: The Complete RAG Pipeline
=========================================
This is where everything comes together!

    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │   Question  │ ──► │   Retrieve  │ ──► │   Format    │ ──► │   Generate  │
    │  from user  │     │   context   │     │   prompt    │     │   answer    │
    └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                              │
                         ChromaDB
                         (154 docs)

Why is this called "RAG"?
- Retrieval: Get relevant documents from vector store
- Augmented: Add those documents to the prompt
- Generation: LLM generates answer using the context

This is better than pure LLM because:
- LLM sees actual problem data, not just training memory
- We can update data without retraining
- Answers are grounded in real content
"""

from dataclasses import dataclass
from typing import Any, Optional
import re
import asyncio
import json

from app.config import settings
from app.rag.vectorstore import VectorStore
from app.rag.llm import LLMService, get_llm_service
from app.rag.reranker import get_default_reranker
from app.prompts import get_prompt


@dataclass
class RAGResponse:
    """
    Complete RAG response with answer and sources.
    
    LEARNING NOTE: Citing Sources
    Always include the sources used to generate the answer.
    This lets users:
    - Verify the information
    - Explore related problems
    - Understand why this answer was given
    """
    answer: str
    sources: list[dict]  # Retrieved documents
    citations: list[dict]
    query_variants: list[str]
    model: str
    tokens_used: int


class RAGGenerator:
    """
    Combines retrieval and generation for RAG.
    
    LEARNING NOTE: RAG Pipeline Design
    The generator orchestrates the full pipeline:
    1. Take user question
    2. Search vector store for relevant context
    3. Format prompt with question + context
    4. Send to LLM for generation
    5. Return answer with sources
    """
    
    def __init__(
        self,
        collection_name: str = "problems",
        llm_service: Any | None = None,
        vector_store: Any | None = None,
        use_reranker: bool = True,
    ):
        self.vector_store = vector_store or VectorStore(collection_name)
        self.llm_service = llm_service or get_llm_service()
        self.reranker = get_default_reranker() if use_reranker else None

    @staticmethod
    def _build_context_and_sources(search_results: dict, max_content_chars: int = 500) -> tuple[str, list[dict], list[dict]]:
        """Build prompt context text and source metadata from Chroma-style results."""
        context_parts: list[str] = []
        sources: list[dict] = []
        citations: list[dict] = []

        distances = search_results.get("distances", [[]])[0] if search_results.get("distances") else []
        scores = search_results.get("scores", [[]])[0] if search_results.get("scores") else []

        for index, (doc_id, document, metadata) in enumerate(
            zip(
                search_results["ids"][0],
                search_results["documents"][0],
                search_results["metadatas"][0],
            )
        ):
            context_parts.append(
                f"[{index + 1}] {metadata.get('title', 'Unknown')}\n"
                f"Type: {metadata.get('type', 'problem')}\n"
                f"Difficulty: {metadata.get('difficulty', 'N/A')}\n"
                f"Content: {document[:max_content_chars]}"
            )

            sources.append(
                {
                    "id": doc_id,
                    "title": metadata.get("title", "Unknown"),
                    "type": metadata.get("type"),
                    "difficulty": metadata.get("difficulty"),
                    "pattern": metadata.get("pattern_name") or metadata.get("pattern"),
                }
            )

            citations.append(
                {
                    "source_id": doc_id,
                    "title": metadata.get("title", "Unknown"),
                    "snippet": document[:220],
                    "distance": distances[index] if index < len(distances) else None,
                    "score": scores[index] if index < len(scores) else None,
                }
            )

        return "\n\n---\n\n".join(context_parts), sources, citations

    async def _expand_query_variants(self, question: str) -> list[str]:
        prompt_template = get_prompt("query_expansion")
        prompt = prompt_template.format(question=question)
        try:
            response = await self.llm_service.generate_with_retry_async(
                prompt=prompt,
                max_tokens=180,
                temperature=0.2,
            )
            lines = [line.strip("-• ") for line in response.content.splitlines() if line.strip()]
            variants = [question]
            for line in lines:
                if line and line.lower() != question.lower() and line not in variants:
                    variants.append(line)
                if len(variants) >= 3:
                    break
            return variants
        except Exception:
            return [question]

    async def _retrieve_candidates_async(self, queries: list[str], n_context: int, where: dict | None = None) -> dict:
        merged: dict[str, dict] = {}
        for query in queries:
            results = await self.vector_store.search_hybrid_async(
                query=query,
                n_results=max(n_context * 4, n_context),
                where=where,
                dense_weight=settings.dense_weight,
            )
            for index, (doc_id, document, metadata, distance) in enumerate(
                zip(
                    results.get("ids", [[]])[0],
                    results.get("documents", [[]])[0],
                    results.get("metadatas", [[]])[0],
                    results.get("distances", [[]])[0],
                )
            ):
                previous = merged.get(doc_id)
                score = (results.get("scores", [[]])[0][index] if results.get("scores") else 0.0)
                if previous is None or score > previous["score"]:
                    merged[doc_id] = {
                        "id": doc_id,
                        "document": document,
                        "metadata": metadata,
                        "distance": distance,
                        "score": score,
                    }

        ranked = sorted(merged.values(), key=lambda item: item["score"], reverse=True)
        pool = ranked[: max(n_context * 5, n_context)]
        return {
            "ids": [[row["id"] for row in pool]],
            "documents": [[row["document"] for row in pool]],
            "metadatas": [[row["metadata"] for row in pool]],
            "distances": [[row["distance"] for row in pool]],
            "scores": [[row["score"] for row in pool]],
        }

    async def generate_answer_async(
        self,
        question: str,
        n_context: int = 3,
        prompt_version: str | None = None,
        max_tokens: int = 1024,
        where: dict | None = None,
    ) -> RAGResponse:
        query_variants = await self._expand_query_variants(question)
        search_results = await self._retrieve_candidates_async(query_variants, n_context=n_context, where=where)

        if self.reranker is not None:
            rerank_async = getattr(self.reranker, "rerank_search_results_async", None)
            if callable(rerank_async):
                search_results = await rerank_async(
                    query=question,
                    search_results=search_results,
                    top_k=n_context,
                )
            else:
                search_results = await asyncio.to_thread(
                    self.reranker.rerank_search_results,
                    question,
                    search_results,
                    n_context,
                )
        else:
            trimmed = min(n_context, len(search_results.get("ids", [[]])[0]))
            search_results = {
                "ids": [search_results.get("ids", [[]])[0][:trimmed]],
                "documents": [search_results.get("documents", [[]])[0][:trimmed]],
                "metadatas": [search_results.get("metadatas", [[]])[0][:trimmed]],
                "distances": [search_results.get("distances", [[]])[0][:trimmed]],
                "scores": [search_results.get("scores", [[]])[0][:trimmed]],
            }

        context, sources, citations = self._build_context_and_sources(search_results, max_content_chars=500)
        prompt_template = get_prompt("answer_problem", prompt_version)
        formatted_prompt = prompt_template.format(context=context, question=question)

        llm_response = await self.llm_service.generate_with_retry_async(
            prompt=formatted_prompt,
            max_tokens=max_tokens,
            temperature=0.7,
        )

        return RAGResponse(
            answer=llm_response.content,
            sources=sources,
            citations=citations,
            query_variants=query_variants,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
        )

    @staticmethod
    def _extract_keywords(text: str, limit: int = 8) -> list[str]:
        """Extract simple high-signal keywords for fallback alignment notes."""
        stopwords = {
            "with", "that", "this", "from", "have", "will", "your", "about", "role", "team",
            "need", "requirements", "experience", "and", "for", "the", "you", "our", "are", "to",
            "in", "of", "on", "a", "an", "as", "is", "be", "or", "we", "at", "by", "it",
        }
        tokens = [token.lower() for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_+-]{2,}", text)]
        seen: list[str] = []
        for token in tokens:
            if token in stopwords or token in seen:
                continue
            seen.append(token)
            if len(seen) >= limit:
                break
        return seen
    
    def generate_answer(
        self,
        question: str,
        n_context: int = 3,
        prompt_version: str | None = None,
        max_tokens: int = 1024
    ) -> RAGResponse:
        """
        Generate an answer to a coding/design question.
        
        LEARNING NOTE: The RAG Process
        
        1. RETRIEVE: Find relevant problems/concepts
           Query: "How do I find duplicates in an array?"
           Retrieved: [Contains Duplicate, Two Sum, Valid Anagram]
        
        2. AUGMENT: Add context to prompt
           "Based on these problems: [context]
            Answer this question: [question]"
        
    3. GENERATE: The LLM (Gemini) produces the answer
           "To find duplicates, you can use a HashSet..."
        
        Args:
            question: User's question
            n_context: Number of documents to retrieve
            prompt_version: Which prompt template to use
            max_tokens: Maximum response length
            
        Returns:
            RAGResponse with answer and sources
        """
        return asyncio.run(
            self.generate_answer_async(
                question=question,
                n_context=n_context,
                prompt_version=prompt_version,
                max_tokens=max_tokens,
            )
        )
    
    def generate_hints(
        self,
        problem_title: str,
        hint_level: int = 1,
        student_attempt: str = ""
    ) -> RAGResponse:
        """
        Generate progressive hints for a problem.
        
        LEARNING NOTE: Progressive Hints
        Levels:
        1 = Very subtle nudge (don't give away the approach)
        2 = Suggest the technique (e.g., "try two pointers")
        3 = Detailed walkthrough (pseudocode level)
        
        This mimics a good tutor who doesn't just give answers.
        """
        # LEARNING NOTE: Normalizing hint levels
        # We clamp hint_level to the supported range (1-3) so callers
        # can pass any integer without breaking prompt lookup.
        hint_level = self._normalize_hint_level(hint_level)

        # Find the specific problem
        search_results = self.vector_store.search(
            query=problem_title,
            n_results=1
        )
        
        if not search_results["ids"][0]:
            return RAGResponse(
                answer=f"I couldn't find a problem called '{problem_title}'.",
                sources=[],
                citations=[],
                query_variants=[problem_title],
                model="none",
                tokens_used=0
            )
        
        # Get problem details
        metadata = search_results["metadatas"][0][0]
        doc = search_results["documents"][0][0]
        
        # Get appropriate hint prompt
        # We construct the name like "hint_level_1" which matches the registry keys
        prompt_name = f"hint_level_{hint_level}"
        try:
            prompt_template = get_prompt(prompt_name)
        except ValueError:
            # Fallback to level 1 if requested level doesn't exist
            prompt_template = get_prompt("hint_level_1")
            
        formatted_prompt = prompt_template.format(
            problem_description=doc,
            student_attempt=student_attempt or "No attempt yet"
        )
        
        # Generate hint
        llm_response = self.llm_service.generate_with_retry(
            prompt=formatted_prompt,
            max_tokens=300,  # Hints should be concise
            temperature=0.5  # Less creative, more focused
        )
        
        return RAGResponse(
            answer=llm_response.content,
            sources=[{
                "id": search_results["ids"][0][0],
                "title": metadata.get("title", "Unknown"),
                "type": metadata.get("type", "problem"),
                "difficulty": metadata.get("difficulty", "N/A"),
                "pattern": metadata.get("pattern_name") or metadata.get("pattern")
            }],
            citations=[{
                "source_id": search_results["ids"][0][0],
                "title": metadata.get("title", "Unknown"),
                "snippet": doc[:220],
                "distance": search_results.get("distances", [[None]])[0][0],
                "score": None,
            }],
            query_variants=[problem_title],
            model=llm_response.model,
            tokens_used=llm_response.tokens_used
        )

    def generate_practice_questions(
        self,
        job_description: str | None = None,
        focus_area: str | None = None,
        question_count: int = 8,
    ) -> RAGResponse:
        """
        Generate practice questions for either general prep or job-aligned prep.

        LEARNING NOTE: Two learning modes
        - General mode: broad interview prep across the corpus
        - Job-aligned mode: prioritize topics present in target JD
        """
        question_count = max(3, min(question_count, 15))
        focus_area = (focus_area or "").strip()
        is_job_aligned = bool(job_description and job_description.strip())

        if is_job_aligned:
            jd_text = (job_description or "")[:4000]
            retrieval_query = f"{focus_area}\n{jd_text}".strip()
            prompt_name = "job_aligned_practice_questions"
        else:
            retrieval_query = (
                focus_area
                or "software engineering interview practice coding system design data structures algorithms"
            )
            prompt_name = "general_practice_questions"

        search_results = self.vector_store.search(
            query=retrieval_query,
            n_results=max(question_count * 3, 12),
        )

        if not search_results.get("ids") or not search_results["ids"][0]:
            return RAGResponse(
                answer="I couldn't find enough indexed problems yet. Please run data processing first.",
                sources=[],
                citations=[],
                query_variants=[retrieval_query],
                model="none",
                tokens_used=0,
            )

        if self.reranker is not None:
            if hasattr(self.reranker, "rerank_search_results"):
                search_results = self.reranker.rerank_search_results(
                    query=retrieval_query,
                    search_results=search_results,
                    top_k=min(max(question_count * 2, 8), 20),
                )

        context, sources, citations = self._build_context_and_sources(search_results, max_content_chars=320)
        prompt_template = get_prompt(prompt_name)
        formatted_prompt = prompt_template.format(
            context=context,
            focus_area=focus_area or "General interview preparation",
            question_count=question_count,
            job_description=(job_description or "").strip()[:5000],
        )

        try:
            llm_response = self.llm_service.generate_with_retry(
                prompt=formatted_prompt,
                max_tokens=min(1200, 140 * question_count),
                temperature=0.4,
            )

            return RAGResponse(
                answer=llm_response.content,
                sources=sources,
                citations=citations,
                query_variants=[retrieval_query],
                model=llm_response.model,
                tokens_used=llm_response.tokens_used,
            )
        except Exception:
            # Fallback path when model quota/rate limits are hit.
            jd_keywords = self._extract_keywords(job_description or "")
            lines: list[str] = []
            for index, source in enumerate(sources[:question_count], start=1):
                difficulty = source.get("difficulty") or "n/a"
                alignment = ", ".join(jd_keywords[:4]) if jd_keywords else (focus_area or "general interview readiness")
                lines.append(
                    f"{index}) {source['title']} ({difficulty})\n"
                    f"   - Skill alignment: {alignment}\n"
                    f"   - Why this matters: Tests core problem-solving and communication under constraints."
                )

            fallback_text = (
                "LLM quota is currently unavailable, so this practice set is generated from retrieval-only mode.\n\n"
                + "\n\n".join(lines)
            )

            return RAGResponse(
                answer=fallback_text,
                sources=sources,
                citations=citations,
                query_variants=[retrieval_query],
                model="retrieval-only-fallback",
                tokens_used=0,
            )

    def generate_followup_questions(
        self,
        problem_title: str,
        solution_approach: str
    ) -> RAGResponse:
        """
        Generate follow-up interview questions after a solution.

        LEARNING NOTE: Follow-up questions
        Interviews rarely end at "solve it." A good follow-up tests:
        - Optimization thinking (time/space tradeoffs)
        - Edge cases and constraints
        - Connections to related problems or patterns
        """
        # Retrieve the problem description for grounding
        search_results = self.vector_store.search(
            query=problem_title,
            n_results=1
        )

        if not search_results["ids"][0]:
            return RAGResponse(
                answer=f"I couldn't find a problem called '{problem_title}'.",
                sources=[],
                citations=[],
                query_variants=[problem_title],
                model="none",
                tokens_used=0
            )

        metadata = search_results["metadatas"][0][0]
        doc = search_results["documents"][0][0]

        prompt_template = get_prompt("generate_followup")
        formatted_prompt = prompt_template.format(
            problem_description=doc,
            solution_approach=solution_approach
        )

        llm_response = self.llm_service.generate_with_retry(
            prompt=formatted_prompt,
            max_tokens=250,
            temperature=0.5
        )

        return RAGResponse(
            answer=llm_response.content,
            sources=[{
                "id": search_results["ids"][0][0],
                "title": metadata.get("title", "Unknown"),
                "type": metadata.get("type", "problem"),
                "difficulty": metadata.get("difficulty", "N/A"),
                "pattern": metadata.get("pattern_name") or metadata.get("pattern")
            }],
            citations=[{
                "source_id": search_results["ids"][0][0],
                "title": metadata.get("title", "Unknown"),
                "snippet": doc[:220],
                "distance": search_results.get("distances", [[None]])[0][0],
                "score": None,
            }],
            query_variants=[problem_title],
            model=llm_response.model,
            tokens_used=llm_response.tokens_used
        )

    async def grade_answer_async(
        self,
        problem_title: str,
        answer: str,
        expected_time_complexity: str = "",
        expected_space_complexity: str = "",
        mode: str = "standard",
    ) -> dict:
        prompt_template = get_prompt("grade_answer")
        formatted_prompt = prompt_template.format(
            problem_title=problem_title,
            answer=answer,
            expected_time_complexity=expected_time_complexity or "not provided",
            expected_space_complexity=expected_space_complexity or "not provided",
            mode=mode,
        )

        llm_response = await self.llm_service.generate_with_retry_async(
            prompt=formatted_prompt,
            max_tokens=400,
            temperature=0.2,
        )
        try:
            parsed = json.loads(llm_response.content)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        return {
            "correctness": 0.6,
            "time_complexity": 0.6,
            "edge_cases": 0.6,
            "communication": 0.6,
            "overall": 0.6,
            "feedback": llm_response.content,
            "mode": mode,
        }

    @staticmethod
    def _normalize_hint_level(hint_level: int) -> int:
        """
        Clamp hint level to the supported range [1, 3].

        LEARNING NOTE: Defensive programming
        External clients can send unexpected values. Clamping protects
        the system from invalid prompt names and keeps behavior predictable.
        """
        if hint_level < 1:
            return 1
        if hint_level > 3:
            return 3
        return hint_level


# Quick test
if __name__ == "__main__":
    print("\nTesting RAG Generator\n")
    
    generator = RAGGenerator()
    
    # Test answer generation
    response = generator.generate_answer(
        question="How do I find two numbers in an array that add up to a target?"
    )
    
    print("Question: How do I find two numbers that add up to a target?")
    print(f"\nSources used: {[s['title'] for s in response.sources]}")
    print(f"\nAnswer:\n{response.answer[:500]}...")
    print(f"\nTokens used: {response.tokens_used}")
