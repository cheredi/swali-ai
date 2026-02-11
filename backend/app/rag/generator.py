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
from typing import Optional

from app.rag.vectorstore import VectorStore
from app.rag.llm import LLMService, LLMResponse, get_llm_service
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
        llm_service: LLMService | None = None
    ):
        self.vector_store = VectorStore(collection_name)
        self.llm_service = llm_service or get_llm_service()
    
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
        
        3. GENERATE: Claude produces the answer
           "To find duplicates, you can use a HashSet..."
        
        Args:
            question: User's question
            n_context: Number of documents to retrieve
            prompt_version: Which prompt template to use
            max_tokens: Maximum response length
            
        Returns:
            RAGResponse with answer and sources
        """
        # Step 1: RETRIEVE relevant context
        search_results = self.vector_store.search(
            query=question,
            n_results=n_context
        )
        
        # Format context for the prompt
        context_parts = []
        sources = []
        
        for i, (doc_id, doc, metadata) in enumerate(zip(
            search_results["ids"][0],
            search_results["documents"][0],
            search_results["metadatas"][0]
        )):
            # Build context string
            context_parts.append(
                f"[{i+1}] {metadata.get('title', 'Unknown')}\n"
                f"Type: {metadata.get('type', 'problem')}\n"
                f"Difficulty: {metadata.get('difficulty', 'N/A')}\n"
                f"Content: {doc[:500]}"  # Limit content length
            )
            
            # Track sources for response
            sources.append({
                "id": doc_id,
                "title": metadata.get("title", "Unknown"),
                "type": metadata.get("type"),
                "difficulty": metadata.get("difficulty"),
                "pattern": metadata.get("pattern_name") or metadata.get("pattern")
            })
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Step 2: AUGMENT - Get and format the prompt
        prompt_template = get_prompt("answer_problem", prompt_version)
        formatted_prompt = prompt_template.format(
            context=context,
            question=question
        )
        
        # Step 3: GENERATE - Call Claude
        llm_response = self.llm_service.generate_with_retry(
            prompt=formatted_prompt,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return RAGResponse(
            answer=llm_response.content,
            sources=sources,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used
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
        # Find the specific problem
        search_results = self.vector_store.search(
            query=problem_title,
            n_results=1
        )
        
        if not search_results["ids"][0]:
            return RAGResponse(
                answer=f"I couldn't find a problem called '{problem_title}'.",
                sources=[],
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
            model=llm_response.model,
            tokens_used=llm_response.tokens_used
        )


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
