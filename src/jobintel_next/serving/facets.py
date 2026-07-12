from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from jobintel_next.pipelines.retrieval import QueryParams, run_retrieval_query
from jobintel_next.storage import sqlite_get_facets


FACET_FIELDS = [
    "role_family",
    "normalized_title",
    "location_type",
    "employment_type",
    "language_bucket",
    "has_salary",
    "has_skills",
    "title_is_other",
    "salary_currency",
]


def _query_dict(q: QueryParams) -> dict[str, Any]:
    return {
        "normalized_title": q.normalized_title,
        "role_family": q.role_family,
        "language_bucket": q.language_bucket,
        "location_type": q.location_type,
        "employment_type": q.employment_type,
        "has_salary": q.has_salary,
        "has_skills": q.has_skills,
        "title_is_other": q.title_is_other,
        "skills_contains": q.skills_contains or [],
        "salary_currency": q.salary_currency,
        "sort_by": q.sort_by,
        "limit": q.limit,
    }


def get_facets(
    *,
    input_path: str | Path,
    query: QueryParams,
    sqlite_path: str | Path | None = None,
    include_fields: list[str] | None = None,
) -> dict[str, Any]:
    if sqlite_path:
        return sqlite_get_facets(
            sqlite_path=sqlite_path,
            query=query,
            include_fields=include_fields,
        )

    base_query = replace(query, limit=None)
    rep = run_retrieval_query(input_path=input_path, query=base_query, output_path=None)
    rows = rep["results"]
    fields = include_fields or FACET_FIELDS
    facets: dict[str, list[dict[str, Any]]] = {}

    for field in fields:
        if field not in FACET_FIELDS:
            continue
        counts: dict[Any, int] = {}
        for row in rows:
            value = row.get(field)
            if field in {"has_salary", "has_skills", "title_is_other"} and value is not None:
                value = bool(value)
            counts[value] = counts.get(value, 0) + 1
        buckets = [{"value": k, "count": v} for k, v in counts.items()]
        buckets.sort(key=lambda x: x["count"], reverse=True)
        facets[field] = buckets

    return {
        "operation": "get_facets",
        "input_path": str(input_path),
        "backend": "jsonl",
        "query": _query_dict(query),
        "total_count": rep["matched_rows"],
        "facets": facets,
    }
