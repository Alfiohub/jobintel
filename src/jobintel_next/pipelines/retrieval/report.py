from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .query import QueryParams, run_retrieval_query


def _compact(rows: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows[:limit]:
        out.append(
            {
                "url": row.get("url"),
                "title_raw": row.get("title_raw"),
                "normalized_title": row.get("normalized_title"),
                "role_family": row.get("role_family"),
                "language_bucket": row.get("language_bucket"),
                "has_salary": row.get("has_salary"),
                "has_skills": row.get("has_skills"),
                "title_is_other": row.get("title_is_other"),
                "published_at": row.get("published_at"),
            }
        )
    return out


def build_retrieval_layer_report(
    *,
    input_path: str | Path,
    report_dir: str | Path = "docs",
) -> dict[str, Any]:
    in_path = Path(input_path)
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sample_queries = [
        {
            "name": "data_engineer_with_salary",
            "params": QueryParams(normalized_title="data_engineer", has_salary=True, sort_by="published_at_desc", limit=5),
        },
        {
            "name": "marketing_role_family",
            "params": QueryParams(role_family="marketing", sort_by="updated_at_desc", limit=5),
        },
        {
            "name": "other_titles_with_skills",
            "params": QueryParams(title_is_other=True, has_skills=True, sort_by="published_at_desc", limit=5),
        },
        {
            "name": "python_skill",
            "params": QueryParams(skills_contains=["python"], sort_by="published_at_desc", limit=5),
        },
    ]

    query_results: list[dict[str, Any]] = []
    for item in sample_queries:
        res = run_retrieval_query(input_path=in_path, query=item["params"])
        query_results.append(
            {
                "name": item["name"],
                "query": res["query"],
                "matched_rows": res["matched_rows"],
                "sample_rows": _compact(res["results"], limit=5),
            }
        )

    report = {
        "input_path": str(in_path),
        "supported_filters": [
            "normalized_title",
            "role_family",
            "language_bucket",
            "location_type",
            "employment_type",
            "has_salary",
            "has_skills",
            "title_is_other",
            "skills_contains",
            "salary_currency",
        ],
        "supported_sorting": [
            "published_at_desc",
            "updated_at_desc",
            "url",
        ],
        "examples": [
            "jobintel-next retrieval query --input data/jobs/jobs_indexed_en.jsonl --normalized-title data_engineer --has-salary true --sort-by published_at_desc --limit 20",
            "jobintel-next retrieval query --input data/jobs/jobs_indexed_en.jsonl --role-family marketing --sort-by updated_at_desc --limit 20",
            "jobintel-next retrieval query --input data/jobs/jobs_indexed_en.jsonl --skills-contains python --has-skills true --limit 20",
        ],
        "sample_query_results": query_results,
        "known_limits": [
            "In-memory JSONL scan; no DB index in v1.",
            "Only exact-match filters (except skills_contains over normalized skill tokens).",
            "No ranking, semantic search, or recommendation in this step.",
        ],
    }

    json_path = out_dir / "retrieval_layer_step15.json"
    md_path = out_dir / "retrieval_layer_step15.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Retrieval Layer Step 15",
        "",
        f"Input: `{in_path}`",
        "",
        "## Supported Filters",
    ]
    for f in report["supported_filters"]:
        md_lines.append(f"- {f}")

    md_lines += [
        "",
        "## Supported Sorting",
    ]
    for s in report["supported_sorting"]:
        md_lines.append(f"- {s}")

    md_lines += [
        "",
        "## Examples",
    ]
    for ex in report["examples"]:
        md_lines.append(f"- `{ex}`")

    md_lines += [
        "",
        "## Sample Query Results",
    ]
    for q in query_results:
        md_lines.append(f"### {q['name']}")
        md_lines.append(f"- matched_rows: {q['matched_rows']}")
        md_lines.append(f"- query: `{q['query']}`")
        for row in q["sample_rows"]:
            md_lines.append(
                f"- {row['url']} | {row['title_raw']} | {row['normalized_title']} | "
                f"family={row['role_family']} | lang={row['language_bucket']} | "
                f"salary={row['has_salary']} | skills={row['has_skills']} | other={row['title_is_other']}"
            )
        md_lines.append("")

    md_lines += [
        "## Known Limits",
    ]
    for lim in report["known_limits"]:
        md_lines.append(f"- {lim}")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return report
