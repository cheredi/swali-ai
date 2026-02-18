"""
Data Ingestion Module for AI/ML Interview Questions.

LEARNING NOTE: Ingestion layer responsibilities
----------------------------------------------
Ingestion should do one thing well: pull raw content from external sources
reliably and convert it into a common in-memory structure.

We intentionally keep ingestion separate from normalization and deduplication:
- Ingestion = fetch + parse
- Normalization = clean + standardize schema
- Deduplication = remove overlaps across sources
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class IngestionSource:
    """Definition of one external source."""

    name: str
    url: str
    category: str
    parser: str


class AIMLInterviewCollector:
    """
    Collect AI/ML interview questions from curated markdown sources.

    LEARNING NOTE: Why markdown sources?
    -----------------------------------
    Markdown repos are easy to version, inspect, and update. They are also
    less likely to break than scraping rendered HTML pages.
    """

    SOURCES: list[IngestionSource] = [
        IngestionSource(
            name="data_science_interviews_theory",
            url="https://raw.githubusercontent.com/alexeygrigorev/data-science-interviews/master/theory.md",
            category="ml_theory",
            parser="bold_question",
        ),
        IngestionSource(
            name="data_science_interviews_technical",
            url="https://raw.githubusercontent.com/alexeygrigorev/data-science-interviews/master/technical.md",
            category="ml_technical",
            parser="bold_question",
        ),
        IngestionSource(
            name="ml_interview_questions_list",
            url="https://raw.githubusercontent.com/khangich/machine-learning-interview/master/questions.md",
            category="ml_engineering",
            parser="numbered_question",
        ),
    ]

    def __init__(self, timeout_seconds: float = 30.0):
        self.client = httpx.Client(timeout=timeout_seconds)

    def collect(self) -> list[dict[str, Any]]:
        """Collect and parse all configured sources."""
        all_records: list[dict[str, Any]] = []

        for source in self.SOURCES:
            text = self._fetch_markdown(source.url)
            if not text:
                continue

            if source.parser == "bold_question":
                records = self._parse_bold_question_markdown(text, source)
            elif source.parser == "numbered_question":
                records = self._parse_numbered_question_markdown(text, source)
            else:
                records = []

            all_records.extend(records)

        return all_records

    def _fetch_markdown(self, url: str) -> str:
        """Fetch markdown content from URL."""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as error:
            print(f"Failed to fetch {url}: {error}")
            return ""

    def _parse_bold_question_markdown(
        self,
        markdown_text: str,
        source: IngestionSource,
    ) -> list[dict[str, Any]]:
        """
        Parse markdown where questions are written as bold lines.

        Example pattern:
        **What is supervised machine learning? 👶**
        """
        lines = markdown_text.splitlines()
        records: list[dict[str, Any]] = []
        current_section = "general"

        for line in lines:
            section_match = re.match(r"^##\s+(.+)$", line.strip())
            if section_match:
                current_section = section_match.group(1).strip().lower().replace(" ", "_")
                continue

            question_match = re.match(r"^\*\*(.+?)\*\*$", line.strip())
            if not question_match:
                continue

            question = question_match.group(1).strip()
            # Filter out non-question headings accidentally wrapped in bold.
            if "?" not in question:
                continue

            records.append(
                {
                    "question": question,
                    "category": current_section,
                    "source": source.name,
                    "source_url": source.url,
                    "topic_family": source.category,
                }
            )

        return records

    def _parse_numbered_question_markdown(
        self,
        markdown_text: str,
        source: IngestionSource,
    ) -> list[dict[str, Any]]:
        """
        Parse markdown where questions appear in numbered lists.

        Example pattern:
        20. Explain collinearity...
        """
        lines = markdown_text.splitlines()
        records: list[dict[str, Any]] = []
        current_section = "general"

        for line in lines:
            section_match = re.match(r"^##\s+(.+)$", line.strip())
            if section_match:
                current_section = section_match.group(1).strip().lower().replace(" ", "_")
                continue

            question_match = re.match(r"^\d+\.\s+(.+)$", line.strip())
            if not question_match:
                continue

            question = question_match.group(1).strip()
            if len(question) < 12:
                continue

            records.append(
                {
                    "question": question,
                    "category": current_section,
                    "source": source.name,
                    "source_url": source.url,
                    "topic_family": source.category,
                }
            )

        return records