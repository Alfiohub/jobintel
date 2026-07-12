from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jobintel_next.pipelines.retrieval import QueryParams, list_query_pack_names

from .service import count_jobs, count_pack, list_jobs, run_pack


def _compact(rows: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows[:limit]:
        out.append(
            {
                "url": row.get("url"),
                "title_raw": row.get("title_raw"),
                "normalized_title": row.get("normalized_title"),
                "role_family": row.get("role_family"),
                "location_type": row.get("location_type"),
                "employment_type": row.get("employment_type"),
                "has_salary": row.get("has_salary"),
                "has_skills": row.get("has_skills"),
                "title_is_other": row.get("title_is_other"),
                "skills": row.get("skills") if isinstance(row.get("skills"), list) else [],
                "published_at": row.get("published_at"),
            }
        )
    return out


def build_serving_layer_report(
    *,
    input_path: str | Path,
    report_dir: str | Path = "docs",
) -> dict[str, Any]:
    in_path = Path(input_path)
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sample_ops: list[dict[str, Any]] = []

    q1 = QueryParams(normalized_title="account_executive", sort_by="published_at_desc")
    q1_res = list_jobs(input_path=in_path, query=q1, limit=5, offset=0)
    q1_count = count_jobs(input_path=in_path, query=q1)
    sample_ops.append(
        {
            "name": "list_account_executive",
            "type": "list_jobs",
            "query": q1_res["query"],
            "total_count": q1_res["total_count"],
            "returned_count": q1_res["returned_count"],
            "count_api": q1_count["count"],
            "sample_rows": _compact(q1_res["results"], limit=5),
        }
    )

    q2 = QueryParams(role_family="marketing", has_salary=True, sort_by="updated_at_desc")
    q2_res = list_jobs(input_path=in_path, query=q2, limit=5, offset=5)
    q2_count = count_jobs(input_path=in_path, query=q2)
    sample_ops.append(
        {
            "name": "list_marketing_with_salary_offset_5",
            "type": "list_jobs",
            "query": q2_res["query"],
            "total_count": q2_res["total_count"],
            "returned_count": q2_res["returned_count"],
            "count_api": q2_count["count"],
            "sample_rows": _compact(q2_res["results"], limit=5),
        }
    )

    p1_name = "high_confidence_tech_jobs"
    p1_res = run_pack(input_path=in_path, pack_name=p1_name, limit=5, offset=0)
    p1_count = count_pack(input_path=in_path, pack_name=p1_name)
    sample_ops.append(
        {
            "name": "pack_high_confidence_tech_jobs",
            "type": "run_pack",
            "pack_name": p1_name,
            "total_count": p1_res["total_count"],
            "returned_count": p1_res["returned_count"],
            "count_api": p1_count["count"],
            "sample_rows": _compact(p1_res["results"], limit=5),
        }
    )

    p2_name = "python_tech_jobs"
    p2_res = run_pack(input_path=in_path, pack_name=p2_name, limit=5, offset=5)
    p2_count = count_pack(input_path=in_path, pack_name=p2_name)
    sample_ops.append(
        {
            "name": "pack_python_tech_jobs_offset_5",
            "type": "run_pack",
            "pack_name": p2_name,
            "total_count": p2_res["total_count"],
            "returned_count": p2_res["returned_count"],
            "count_api": p2_count["count"],
            "sample_rows": _compact(p2_res["results"], limit=5),
        }
    )

    report = {
        "input_path": str(in_path),
        "supported_operations": [
            "list_jobs(filters..., limit, offset)",
            "count_jobs(filters...)",
            "run_pack(pack_name, limit, offset)",
            "count_pack(pack_name)",
        ],
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
        "pagination": {
            "params": ["limit", "offset"],
            "default_limit": 20,
            "default_offset": 0,
            "behavior": "offset applied before limit on sorted matches",
        },
        "available_query_packs": list_query_pack_names(),
        "examples": [
            "jobintel-next serve query --input data/jobs/jobs_indexed_en.jsonl --normalized-title account_executive --limit 20 --offset 0",
            "jobintel-next serve count --input data/jobs/jobs_indexed_en.jsonl --role-family marketing --has-salary true",
            "jobintel-next serve pack --input data/jobs/jobs_indexed_en.jsonl --pack high_confidence_tech_jobs --limit 20 --offset 0",
            "jobintel-next serve pack-count --input data/jobs/jobs_indexed_en.jsonl --pack python_tech_jobs",
        ],
        "sample_results": sample_ops,
        "known_limits": [
            "Local JSONL scan in memory; no DB index in step19.",
            "No ranking, semantic search, or recommendation.",
            "Quality depends on upstream structured signals.",
        ],
    }

    json_path = out_dir / "serving_layer_step19.json"
    md_path = out_dir / "serving_layer_step19.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Serving Layer Step 19",
        "",
        f"Input: `{in_path}`",
        "",
        "## Supported Operations",
    ]
    for op in report["supported_operations"]:
        md_lines.append(f"- `{op}`")

    md_lines += [
        "",
        "## Supported Filters",
    ]
    for f in report["supported_filters"]:
        md_lines.append(f"- `{f}`")

    md_lines += [
        "",
        "## Pagination",
        f"- params: `{report['pagination']['params']}`",
        f"- default_limit: {report['pagination']['default_limit']}",
        f"- default_offset: {report['pagination']['default_offset']}",
        f"- behavior: {report['pagination']['behavior']}",
        "",
        "## Available Query Packs",
    ]
    for p in report["available_query_packs"]:
        md_lines.append(f"- `{p}`")

    md_lines += [
        "",
        "## Examples",
    ]
    for ex in report["examples"]:
        md_lines.append(f"- `{ex}`")

    md_lines += [
        "",
        "## Sample Results",
    ]
    for s in report["sample_results"]:
        md_lines.append(f"### {s['name']}")
        md_lines.append(f"- type: `{s['type']}`")
        if "query" in s:
            md_lines.append(f"- query: `{s['query']}`")
        if "pack_name" in s:
            md_lines.append(f"- pack_name: `{s['pack_name']}`")
        md_lines.append(f"- total_count: {s['total_count']}")
        md_lines.append(f"- returned_count: {s['returned_count']}")
        md_lines.append(f"- count_api: {s['count_api']}")
        for row in s["sample_rows"]:
            md_lines.append(
                f"- {row['url']} | {row['title_raw']} | {row['normalized_title']} | "
                f"family={row['role_family']} | loc={row['location_type']} | "
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
