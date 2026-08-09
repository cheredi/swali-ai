"""Collect additional interview corpus sources and normalize them for indexing.

This collector intentionally supports two acquisition modes:
1) Remote fetch from public URLs (GitHub raw markdown, HuggingFace preview API).
2) Local file ingestion for sources that usually need credentials/export flow
    (Kaggle downloads, custom LeetCode Discuss exports, NeetCode explanation notes).
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


@dataclass(frozen=True)
class RemoteMarkdownSource:
    slug: str
    title: str
    source_url: str
    topic: str
    tags: list[str]
    difficulty: str = "mixed"
    type: str = "reference"


REMOTE_MARKDOWN_SOURCES = [
    RemoteMarkdownSource(
        slug="system_design_primer",
        title="System Design Primer",
        source_url="https://raw.githubusercontent.com/donnemartin/system-design-primer/master/README.md",
        topic="system_design",
        tags=["system_design", "architecture", "distributed_systems"],
    ),
    RemoteMarkdownSource(
        slug="tech_interview_handbook",
        title="Tech Interview Handbook",
        source_url="https://raw.githubusercontent.com/yangshun/tech-interview-handbook/master/README.md",
        topic="coding_interview",
        tags=["coding", "behavioral", "system_design"],
    ),
    RemoteMarkdownSource(
        slug="awesome_interview_questions",
        title="Awesome Interview Questions",
        source_url="https://raw.githubusercontent.com/DopplerHQ/awesome-interview-questions/master/README.md",
        topic="interview_prep",
        tags=["interview", "question_bank", "curated"],
    ),
    RemoteMarkdownSource(
        slug="leetscrape",
        title="LeetScrape",
        source_url="https://raw.githubusercontent.com/nikhil-ravi/LeetScrape/main/README.md",
        topic="leetcode",
        tags=["leetcode", "scraping", "problem_collection"],
    ),
    RemoteMarkdownSource(
        slug="data_science_interviews",
        title="Data Science Interviews",
        source_url="https://raw.githubusercontent.com/alexeygrigorev/data-science-interviews/master/README.md",
        topic="ai_ml",
        tags=["machine_learning", "data_science", "interview_questions"],
    ),
]

HF_FIRST_ROWS_URL = (
    "https://datasets-server.huggingface.co/first-rows"
    "?dataset=ali-alkhars/interviews&config=default&split=train"
)

LOCAL_OPTIONAL_FILES: list[tuple[Path, dict[str, Any]]] = [
    (
        Path("data/raw/external/kaggle_software_engineering_interview_questions.json"),
        {
            "source": "kaggle_syedmharis",
            "source_url": "https://www.kaggle.com/datasets/syedmharis/software-engineering-interview-questions-dataset",
            "topic": "software_engineering",
            "tags": ["kaggle", "software_engineering", "interview_questions"],
            "type": "question",
            "difficulty": "mixed",
        },
    ),
    (
        Path("data/raw/external/leetcode_discuss_threads.json"),
        {
            "source": "leetcode_discuss",
            "source_url": "https://leetcode.com/discuss/interview-question",
            "topic": "leetcode",
            "tags": ["leetcode", "discuss", "community"],
            "type": "discussion",
            "difficulty": "mixed",
        },
    ),
    (
        Path("data/raw/external/neetcode_explanations.json"),
        {
            "source": "neetcode_explanations",
            "source_url": "https://neetcode.io",
            "topic": "coding_interview",
            "tags": ["neetcode", "explanations", "patterns"],
            "type": "explanation",
            "difficulty": "mixed",
        },
    ),
    (
        Path("data/raw/external/ddia_highlights.json"),
        {
            "source": "ddia_highlights",
            "source_url": "https://github.com/donnemartin/system-design-primer",
            "topic": "system_design",
            "tags": ["ddia", "distributed_systems", "design_principles"],
            "type": "highlight",
            "difficulty": "advanced",
        },
    ),
]

OPTIONAL_ITEM_ALLOWED_FIELDS = {
    "id",
    "title",
    "question",
    "description",
    "content",
    "answer",
    "notes",
    "body",
    "text",
    "difficulty",
    "tags",
    "source",
    "source_name",
    "source_url",
    "type",
    "topic",
    "topic_family",
    "company",
}

OPTIONAL_REQUIRED_TEXT_FIELDS = {
    "description",
    "content",
    "question",
    "answer",
    "notes",
    "body",
    "text",
}


def _validate_optional_payload(file_path: Path, payload: Any) -> list[dict[str, Any]]:
    """Strictly validate optional corpus files and fail fast on malformed data."""
    if not isinstance(payload, list):
        raise ValueError(f"{file_path}: expected top-level JSON array")

    validated: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"{file_path}: item {index} must be a JSON object")

        if unknown_fields := set(item.keys()) - OPTIONAL_ITEM_ALLOWED_FIELDS:
            unknown_text = ", ".join(sorted(unknown_fields))
            raise ValueError(f"{file_path}: item {index} has unsupported fields: {unknown_text}")

        title = item.get("title") or item.get("question")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{file_path}: item {index} must include non-empty 'title' or 'question'")

        has_text_blob = any(
            isinstance(item.get(field), str) and item.get(field, "").strip()
            for field in OPTIONAL_REQUIRED_TEXT_FIELDS
        )
        if not has_text_blob:
            raise ValueError(
                f"{file_path}: item {index} must include one non-empty text field from "
                f"{sorted(OPTIONAL_REQUIRED_TEXT_FIELDS)}"
            )

        if "difficulty" in item and not isinstance(item.get("difficulty"), str):
            raise ValueError(f"{file_path}: item {index} field 'difficulty' must be a string")

        tags = item.get("tags")
        if tags is not None and not isinstance(tags, (list, str)):
            raise ValueError(f"{file_path}: item {index} field 'tags' must be a list or comma-separated string")
        if isinstance(tags, list) and any(not isinstance(tag, str) for tag in tags):
            raise ValueError(f"{file_path}: item {index} field 'tags' list must contain only strings")

        if "company" in item and item.get("company") is not None and not isinstance(item.get("company"), str):
            raise ValueError(f"{file_path}: item {index} field 'company' must be a string if provided")

        validated.append(item)

    return validated


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _stable_id(prefix: str, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _split_markdown_sections(markdown_text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_title = "overview"
    current_lines: list[str] = []

    for line in markdown_text.splitlines():
        if heading_match := re.match(r"^#{2,3}\s+(.+?)\s*$", line.strip()):
            if content := "\n".join(current_lines).strip():
                sections.append((current_title, content))
            current_title = heading_match.group(1).strip()
            current_lines = []
            continue
        current_lines.append(line)

    if trailing := "\n".join(current_lines).strip():
        sections.append((current_title, trailing))

    return sections[:40]


def _collect_remote_markdown(client: httpx.Client) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in REMOTE_MARKDOWN_SOURCES:
        try:
            response = client.get(source.source_url)
            response.raise_for_status()
            sections = _split_markdown_sections(response.text)
            for section_title, section_body in sections:
                excerpt = section_body[:2400]
                anchor = _slugify(section_title)
                unique_text = f"{source.slug}:{section_title}:{excerpt[:180]}"
                records.append(
                    {
                        "id": _stable_id("ext", unique_text),
                        "title": f"{source.title} — {section_title}",
                        "description": excerpt,
                        "difficulty": source.difficulty,
                        "tags": source.tags,
                        "source": source.slug,
                        "source_name": source.title,
                        "source_url": f"{source.source_url}#{anchor}" if anchor else source.source_url,
                        "type": source.type,
                        "topic": source.topic,
                        "topic_family": source.topic,
                    }
                )
        except Exception as error:
            print(f"Skipping {source.source_url}: {error}")

    return records


def _collect_huggingface_preview(client: httpx.Client) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        response = client.get(HF_FIRST_ROWS_URL)
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("rows", [])
        for index, row in enumerate(rows):
            row_data = row.get("row", {})
            values = [str(value).strip() for value in row_data.values() if str(value).strip()]
            text = " | ".join(values)[:2400]
            if len(text) < 20:
                continue
            title = values[0][:120] if values else f"HF interview row {index + 1}"
            records.append(
                {
                    "id": _stable_id("hf", f"{title}:{text[:120]}"),
                    "title": f"HF interviews — {title}",
                    "description": text,
                    "difficulty": "mixed",
                    "tags": ["huggingface", "interviews", "dataset"],
                    "source": "huggingface_ali_alkhars_interviews",
                    "source_name": "ali-alkhars/interviews",
                    "source_url": "https://huggingface.co/datasets/ali-alkhars/interviews",
                    "type": "question",
                    "topic": "interview_prep",
                    "topic_family": "interview_prep",
                }
            )
    except Exception as error:
        print(f"Skipping HuggingFace dataset preview: {error}")

    return records


def _extract_text_blob(item: dict[str, Any]) -> str:
    candidate_fields = [
        "description",
        "content",
        "question",
        "answer",
        "notes",
        "body",
        "text",
    ]
    text_parts: list[str] = []
    for field in candidate_fields:
        if value := item.get(field):
            text_parts.append(str(value).strip())
    return "\n".join(part for part in text_parts if part)


def _collect_local_optional_files() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for file_path, defaults in LOCAL_OPTIONAL_FILES:
        if not file_path.exists():
            print(f"Optional source not found (skipping): {file_path}")
            continue

        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as error:
            print(f"Skipping unreadable JSON file {file_path}: {error}")
            continue

        try:
            validated_payload = _validate_optional_payload(file_path, payload)
        except ValueError as error:
            raise ValueError(str(error)) from error

        for index, item in enumerate(validated_payload):
            title = str(item.get("title") or item.get("question") or f"{defaults['source']} item {index + 1}")
            description = _extract_text_blob(item)
            if len(description) < 20:
                continue
            source = str(item.get("source") or defaults["source"])
            topic = str(item.get("topic") or item.get("topic_family") or defaults["topic"])
            tags = item.get("tags") or defaults["tags"]
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if not isinstance(tags, list):
                tags = defaults["tags"]

            unique_text = f"{source}:{title}:{description[:120]}"
            records.append(
                {
                    "id": str(item.get("id") or _stable_id("local", unique_text)),
                    "title": title[:180],
                    "description": description[:2600],
                    "difficulty": str(item.get("difficulty") or defaults["difficulty"]),
                    "tags": tags,
                    "source": source,
                    "source_name": str(item.get("source_name") or source),
                    "source_url": str(item.get("source_url") or defaults["source_url"]),
                    "type": str(item.get("type") or defaults["type"]),
                    "topic": topic,
                    "topic_family": topic,
                    "company": item.get("company"),
                }
            )

    return records


def collect_external_corpus() -> list[dict[str, Any]]:
    with httpx.Client(timeout=25) as client:
        records = []
        records.extend(_collect_remote_markdown(client))
        records.extend(_collect_huggingface_preview(client))

    records.extend(_collect_local_optional_files())

    deduped: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for record in records:
        key = f"{record.get('source')}::{record.get('title')}"
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(record)

    return deduped


def main() -> None:
    records = collect_external_corpus()

    out_file = Path("data/raw/external/external_corpus.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} external records to {out_file}")
    print("\nOptional local files (drop these in for fuller coverage):")
    for file_path, defaults in LOCAL_OPTIONAL_FILES:
        print(f"  - {file_path}  ({defaults['source_url']})")


if __name__ == "__main__":
    main()
