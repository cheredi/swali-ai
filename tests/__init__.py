"""
Tests Package

🎓 LEARNING NOTE: Testing RAG Systems
=====================================
RAG systems need different types of tests:

1. UNIT TESTS - Test individual functions
   - Does embed_text() return correct dimensions?
   - Does search() return expected format?

2. INTEGRATION TESTS - Test components together
   - Does the full pipeline work end-to-end?
   - Can we add documents and retrieve them?

3. EVALUATION TESTS - Test quality (not pass/fail)
   - Is retrieval relevant? (Recall@k, MRR)
   - Are answers accurate? (compared to ground truth)
   - Are explanations helpful? (LLM-as-judge)

This package contains all three types.
"""
