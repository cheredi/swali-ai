# Prompts README

This folder documents prompt design strategy for Swali-AI.

> Runtime prompt templates currently live in `backend/app/prompts/__init__.py`.

## Prompt Types in Use

1. `answer_problem`
   - Purpose: Generate grounded answer from retrieved context.
   - Inputs: `context`, `question`.

2. `hint_level_1..3`
   - Purpose: Progressive hints with increasing specificity.
   - Inputs: `problem_description`, `student_attempt`.

3. `generate_followup`
   - Purpose: Produce interview-style follow-up questions.
   - Inputs: `problem_description`, `solution_approach`.

## Prompt Design Principles

- Ground every response in retrieved context.
- Prefer concise, structured output.
- Keep hints pedagogical (nudge before reveal).
- Use explicit role instructions and output constraints.

## Prompt Versioning Guidance

- Keep template names stable.
- Add optional `version` suffix for experiments.
- Record outcomes in `experiments.md` when prompt changes impact quality.
