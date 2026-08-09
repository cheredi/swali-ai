"""Bootstrap additional interview questions using Gemini from existing corpus."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.rag.llm import get_llm_service
from app.rag.vectorstore import VectorStore


def build_prompt(problem_text: str, title: str) -> str:
    return f"""
Given this interview problem, generate:
1) three variants at increasing difficulty
2) two follow-up deep dive questions
3) one 'what-if' variant

Problem title: {title}
Problem context:
{problem_text[:1800]}

Return JSON with keys: variants, followups, what_if.
""".strip()


def main() -> None:
    store = VectorStore("problems")
    llm = get_llm_service()
    all_docs = store.get_all()

    generated = []
    for doc_id, document, metadata in zip(
        all_docs.get("ids", []),
        all_docs.get("documents", []),
        all_docs.get("metadatas", []),
    ):
        title = metadata.get("title", doc_id)
        try:
            response = llm.generate_with_retry(
                prompt=build_prompt(document, title),
                max_tokens=400,
                temperature=0.4,
            )
            generated.append(
                {
                    "source_id": doc_id,
                    "title": title,
                    "generated": response.content,
                }
            )
        except Exception as error:
            print(f"Skipping {title}: {error}")

        if len(generated) >= 25:
            break

    out_file = Path("data/processed/bootstrap_variants.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(generated, indent=2), encoding="utf-8")
    print(f"Wrote {len(generated)} generated variant sets to {out_file}")


if __name__ == "__main__":
    main()
