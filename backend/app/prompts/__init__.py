"""
Prompt Templates for Swali-AI

🎓 LEARNING NOTE: Prompt Engineering for RAG
=============================================
Prompts are the interface between retrieved context and LLM output.
Good RAG prompts should:

1. CLEARLY SEPARATE context from instruction
2. GROUND the LLM in retrieved documents
3. HANDLE edge cases (no relevant docs, ambiguous queries)
4. Be VERSIONED for experimentation

This module provides structured prompts for different use cases.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    """
    A versioned prompt template.

    Variables in the template use {variable_name} syntax.
    """
    name: str
    version: str
    template: str
    description: str

    def format(self, **kwargs) -> str:
        """Fill in the template with provided values."""
        return self.template.format(**kwargs)


# =============================================================================
# RAG Answer Prompts
# =============================================================================

ANSWER_PROBLEM_V1 = PromptTemplate(
    name="answer_problem",
    version="1.0",
    description="Generate an explanation for a coding/system design problem",
    template="""You are an expert interview coach helping a student understand a technical problem.

## Retrieved Problem Context
{context}

## Student's Question
{question}

## Instructions
1. If the question is about a specific problem, explain the approach clearly
2. Break down the solution into logical steps
3. Explain the time and space complexity
4. Mention common pitfalls or edge cases
5. If the context doesn't fully answer the question, acknowledge what's missing

Provide a clear, educational explanation that helps the student understand not just WHAT to do, but WHY."""
)

ANSWER_PROBLEM_V2 = PromptTemplate(
    name="answer_problem",
    version="2.0",
    description="More structured problem explanation with pattern recognition",
    template="""You are an expert coding interview coach. Your goal is to help the student deeply understand the problem pattern, not just memorize a solution.

## Retrieved Context
{context}

## Student's Question
{question}

## Response Format
Structure your answer as follows:

### Pattern Recognition
What algorithmic pattern does this problem use? (e.g., Two Pointers, Sliding Window, DFS)

### Intuition
Explain the core insight that makes the solution work. What's the "aha moment"?

### Approach
Step-by-step solution strategy.

### Complexity Analysis
- Time: O(?)
- Space: O(?)

### Edge Cases
What inputs might break a naive solution?

### Similar Problems
What other problems use the same pattern?

Be encouraging and educational. Use analogies when helpful."""
)


# =============================================================================
# Hint Prompts
# =============================================================================

HINT_LEVEL_1 = PromptTemplate(
    name="hint_level_1",
    version="1.0",
    description="First hint - very subtle, just a nudge in the right direction",
    template="""You are helping a student who is stuck on a coding problem. Give them a VERY SUBTLE hint.

## Problem
{problem_description}

## What the student has tried
{student_attempt}

## Instructions
- DO NOT give away the solution or algorithm name
- Just give a small nudge in the right direction
- Ask a guiding question that might help them think differently
- Keep it to 1-2 sentences maximum

Remember: The goal is for THEM to have the "aha moment", not for you to solve it."""
)

HINT_LEVEL_2 = PromptTemplate(
    name="hint_level_2",
    version="1.0",
    description="Second hint - suggests the approach without full solution",
    template="""You are helping a student who needs a bit more guidance.

## Problem
{problem_description}

## What the student has tried
{student_attempt}

## Instructions
- Suggest the general approach or data structure to consider
- You can name the technique (e.g., "Consider using two pointers")
- Explain WHY this approach might help
- Still don't give the full algorithm
- Keep it to 3-4 sentences maximum"""
)

HINT_LEVEL_3 = PromptTemplate(
    name="hint_level_3",
    version="1.0",
    description="Third hint - walk through the approach with pseudocode",
    template="""You are helping a student who needs significant guidance.

## Problem
{problem_description}

## What the student has tried
{student_attempt}

## Instructions
- Walk through the approach step by step
- You can provide pseudocode (but not complete code)
- Explain the key insight that makes it work
- Help them understand so they can implement it themselves"""
)


# =============================================================================
# Follow-up Question Prompts
# =============================================================================

GENERATE_FOLLOWUP = PromptTemplate(
    name="generate_followup",
    version="1.0",
    description="Generate follow-up questions to test understanding",
    template="""You are an interview coach testing a student's understanding after they solved a problem.

## Problem They Solved
{problem_description}

## Their Solution Approach
{solution_approach}

## Instructions
Generate 3 follow-up questions that test deeper understanding:

1. A question about optimizing their solution (time/space)
2. A question about handling an edge case or constraint change
3. A question connecting this to a related problem or concept

Format each question clearly. These should feel like natural interview follow-ups."""
)


# =============================================================================
# System Design Prompts
# =============================================================================

SYSTEM_DESIGN_GUIDE = PromptTemplate(
    name="system_design_guide",
    version="1.0",
    description="Guide through system design problem",
    template="""You are an expert system design interviewer helping a candidate work through a design problem.

## Design Problem
{problem_description}

## Candidate's Current Focus
{current_focus}

## Retrieved Context
{context}

## Instructions
Guide the candidate through the design process:

1. If they haven't clarified requirements, prompt them to do so
2. If they're stuck on a component, explain the trade-offs
3. Reference specific concepts from the context when relevant
4. Keep responses conversational - this is a dialogue, not a lecture
5. Ask probing questions to test understanding

Remember: In real interviews, showing your thought process matters as much as the final design."""
)


# =============================================================================
# Prompt Registry
# =============================================================================

PROMPT_REGISTRY = {
    "answer_problem_v1": ANSWER_PROBLEM_V1,
    "answer_problem_v2": ANSWER_PROBLEM_V2,
    "hint_level_1": HINT_LEVEL_1,
    "hint_level_2": HINT_LEVEL_2,
    "hint_level_3": HINT_LEVEL_3,
    "generate_followup": GENERATE_FOLLOWUP,
    "system_design_guide": SYSTEM_DESIGN_GUIDE,
}


def get_prompt(name: str, version: Optional[str] = None) -> PromptTemplate:
    """
    Get a prompt template by name and optional version.

    If version is not specified, returns the latest version.
    """
    if version:
        key = f"{name}_v{version}"
        if key in PROMPT_REGISTRY:
            return PROMPT_REGISTRY[key]

    # Find latest version
    matching = [k for k in PROMPT_REGISTRY if k.startswith(name)]
    if matching:
        return PROMPT_REGISTRY[sorted(matching)[-1]]

    raise ValueError(f"Prompt '{name}' not found")


# Example usage
if __name__ == "__main__":
    print("Prompt Templates Demo\n")

    # Get a prompt and format it
    prompt = get_prompt("answer_problem", "2")

    formatted = prompt.format(
        context="Two Sum: Given an array and target, find two numbers that add up to target.",
        question="How do I solve the Two Sum problem efficiently?"
    )

    print(f"Prompt: {prompt.name} v{prompt.version}")
    print(f"Description: {prompt.description}")
    print(f"\nFormatted (first 500 chars):\n{str(formatted)[:500]}...")
