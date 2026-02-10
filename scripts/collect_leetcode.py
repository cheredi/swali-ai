"""
LeetCode Data Collector for Swali-AI

🎓 LEARNING NOTE: Data Collection for RAG
=========================================
The quality of your RAG system depends heavily on data quality.
For interview prep, we need:
- Problem descriptions
- Examples and constraints
- Difficulty levels
- Tags/categories for filtering

This script uses the LeetCode GraphQL API (unofficial but widely used).
We're collecting public problem data for educational purposes.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import httpx


@dataclass
class LeetCodeProblem:
    """Represents a LeetCode problem."""
    id: str
    title: str
    title_slug: str
    difficulty: str
    description: str
    examples: list[str]
    constraints: list[str]
    tags: list[str]
    hints: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "title_slug": self.title_slug,
            "difficulty": self.difficulty.lower(),
            "description": self.description,
            "examples": self.examples,
            "constraints": self.constraints,
            "tags": self.tags,
            "hints": self.hints,
            "source": "leetcode",
            "source_url": f"https://leetcode.com/problems/{self.title_slug}/"
        }


class LeetCodeCollector:
    """
    Collects problem data from LeetCode's GraphQL API.

    🎓 LEARNING NOTE: Rate Limiting
    Always be respectful when scraping - add delays between requests.
    LeetCode's API is unofficial, so we should be careful not to abuse it.
    """

    BASE_URL = "https://leetcode.com/graphql"

    # GraphQL query to get problem list
    PROBLEM_LIST_QUERY = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
        ) {
            total: totalNum
            questions: data {
                questionId
                title
                titleSlug
                difficulty
                topicTags {
                    name
                    slug
                }
            }
        }
    }
    """

    # GraphQL query to get problem details
    PROBLEM_DETAIL_QUERY = """
    query questionContent($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            title
            titleSlug
            content
            difficulty
            hints
            topicTags {
                name
            }
            exampleTestcaseList
        }
    }
    """

    def __init__(self, output_dir: str = "./data/raw/leetcode"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.Client(timeout=30.0)

    def _make_request(self, query: str, variables: dict) -> Optional[dict]:
        """Make a GraphQL request to LeetCode."""
        try:
            response = self.client.post(
                self.BASE_URL,
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

    def get_problem_list(
        self,
        limit: int = 50,
        skip: int = 0,
        difficulty: Optional[str] = None
    ) -> list[dict]:
        """
        Get a list of problems from LeetCode.

        Args:
            limit: Number of problems to fetch
            skip: Number of problems to skip (for pagination)
            difficulty: Filter by difficulty (EASY, MEDIUM, HARD)
        """
        filters = {}
        if difficulty:
            filters["difficulty"] = difficulty

        variables = {
            "categorySlug": "",
            "limit": limit,
            "skip": skip,
            "filters": filters
        }

        result = self._make_request(self.PROBLEM_LIST_QUERY, variables)
        if result and "data" in result:
            return result["data"]["problemsetQuestionList"]["questions"]
        return []

    def get_problem_detail(self, title_slug: str) -> Optional[LeetCodeProblem]:
        """
        Get detailed information about a specific problem.

        🎓 LEARNING NOTE: HTML Content
        LeetCode returns problem descriptions as HTML.
        We'll need to parse and clean this for our embeddings.
        """
        result = self._make_request(
            self.PROBLEM_DETAIL_QUERY,
            {"titleSlug": title_slug}
        )

        if not result or "data" not in result or not result["data"]["question"]:
            return None

        q = result["data"]["question"]

        # Parse HTML content (basic cleanup)
        description = self._clean_html(q.get("content", ""))

        # Extract examples from content
        examples = self._extract_examples(q.get("content", ""))

        # Extract constraints
        constraints = self._extract_constraints(q.get("content", ""))

        return LeetCodeProblem(
            id=f"lc_{q['questionId']}",
            title=q["title"],
            title_slug=q["titleSlug"],
            difficulty=q["difficulty"],
            description=description,
            examples=examples,
            constraints=constraints,
            tags=[t["name"] for t in q.get("topicTags", [])],
            hints=q.get("hints", [])
        )

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags for cleaner text."""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_examples(self, html: str) -> list[str]:
        """Extract examples from problem HTML."""
        import re
        examples = []
        # Look for Example patterns
        pattern = r'<strong>Example \d+:</strong>(.*?)(?=<strong>Example|<strong>Constraints|$)'
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            clean = self._clean_html(match)
            if clean:
                examples.append(clean)
        # Limit to 3 examples
        return list(examples)[:3]

    def _extract_constraints(self, html: str) -> list[str]:
        """Extract constraints from problem HTML."""
        import re
        # Look for Constraints section
        pattern = r'<strong>Constraints:</strong>(.*?)(?=<|$)'
        match = re.search(pattern, html, re.DOTALL)
        if match:
            constraints_text = match.group(1)
            # Split by list items or newlines
            items = re.findall(r'<li>(.*?)</li>', constraints_text)
            return [self._clean_html(item) for item in items]
        return []

    def collect_problems(
        self,
        num_problems: int = 100,
        delay: float = 1.0
    ) -> list[dict]:
        """
        Collect multiple problems and save to disk.

        🎓 LEARNING NOTE: Batching and Persistence
        We save after each problem to avoid losing progress if something fails.
        This is important for long-running data collection tasks.
        """
        print(f"🚀 Starting to collect {num_problems} LeetCode problems...")

        problems = []
        problem_list = self.get_problem_list(limit=num_problems)

        print(f"📋 Found {len(problem_list)} problems to fetch")

        for i, p in enumerate(problem_list):
            print(f"  [{i+1}/{len(problem_list)}] Fetching: {p['title']}...")

            detail = self.get_problem_detail(p["titleSlug"])
            if detail:
                problems.append(detail.to_dict())

                # Save incrementally
                self._save_problem(detail)

            # Be nice to the API
            time.sleep(delay)

        # Save complete collection
        output_file = self.output_dir / "all_problems.json"
        with open(output_file, "w") as f:
            json.dump(problems, f, indent=2)

        print(f"\n✅ Collected {len(problems)} problems")
        print(f"📁 Saved to: {output_file}")

        return problems

    def _save_problem(self, problem: LeetCodeProblem) -> None:
        """Save a single problem to disk."""
        output_file = self.output_dir / f"{problem.id}.json"
        with open(output_file, "w") as f:
            json.dump(problem.to_dict(), f, indent=2)


# Convenience function
def collect_leetcode_problems(num_problems: int = 100) -> list[dict]:
    """Quick function to collect LeetCode problems."""
    collector = LeetCodeCollector()
    return collector.collect_problems(num_problems)


if __name__ == "__main__":
    # Test with a small batch
    print("🧪 Testing LeetCode Collector\n")
    collector = LeetCodeCollector()

    # Get problem list
    problems = collector.get_problem_list(limit=5)
    print(f"Found {len(problems)} problems")

    if problems:
        # Get details for first problem
        detail = collector.get_problem_detail(problems[0]["titleSlug"])
        if detail:
            print("\n📝 Sample Problem:")
            print(f"   Title: {detail.title}")
            print(f"   Difficulty: {detail.difficulty}")
            print(f"   Tags: {detail.tags}")
            print(f"   Description preview: {str(detail.description)[:200]}...")
