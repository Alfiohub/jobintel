from __future__ import annotations

from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_jsonl, repo_root, tokenize, write_json, write_jsonl


PILOT_TITLES = [
    "Onboarding Specialist",
    "Implementation Engineer",
    "Partner Manager",
    "Producer",
    "Designer",
    "Operations Analyst",
]

TEXT_FIELDS = ["description_clean", "requirements_clean", "responsibilities_clean"]


def _context_text(row: dict[str, Any]) -> str:
    return " ".join(str(row.get(field) or "") for field in TEXT_FIELDS).strip()


def build_context_join(
    titled_path: Path,
    extracted_path: Path,
    out_jsonl: Path,
    out_summary: Path,
    target_titles: list[str] | None = None,
) -> dict[str, Any]:
    titles = set(target_titles or PILOT_TITLES)
    extracted_rows = {row["url"]: row for row in read_jsonl(extracted_path) if row.get("url")}

    joined_rows: list[dict[str, Any]] = []
    by_title: dict[str, int] = {title: 0 for title in titles}

    for row in read_jsonl(titled_path):
        if row.get("classification_status") != "other":
            continue
        title_clean = str(row.get("title_clean") or "")
        if title_clean not in titles:
            continue
        extracted = extracted_rows.get(str(row.get("url") or ""), {})
        context_text = _context_text(extracted)
        joined = {
            "url": row.get("url"),
            "company_name": row.get("company_name"),
            "title_clean": title_clean,
            "normalized_title": row.get("normalized_title"),
            "role_family": row.get("role_family"),
            "departments_raw": extracted.get("departments_raw"),
            "skills": extracted.get("skills") or [],
            "seniority": extracted.get("seniority"),
            "employment_type": extracted.get("employment_type"),
            "tags": extracted.get("tags") or {},
            "context_text": context_text,
            "context_token_count": len(tokenize(context_text)),
            "description_clean": extracted.get("description_clean"),
            "requirements_clean": extracted.get("requirements_clean"),
            "responsibilities_clean": extracted.get("responsibilities_clean"),
        }
        joined_rows.append(joined)
        by_title[title_clean] += 1

    summary = {
        "titled_path": str(titled_path.relative_to(repo_root())),
        "extracted_path": str(extracted_path.relative_to(repo_root())),
        "target_titles": sorted(titles),
        "joined_rows": len(joined_rows),
        "counts_by_title": by_title,
    }

    write_jsonl(out_jsonl, joined_rows)
    write_json(out_summary, summary)
    return summary


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    result = build_context_join(
        titled_path=root / "data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl",
        extracted_path=root / "data/jobs/jobs_extracted_en.jsonl",
        out_jsonl=reports / "context_join_v1.jsonl",
        out_summary=reports / "context_join_v1_summary.json",
    )
    print(result)
