from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class QueryParams:
    normalized_title: str | None = None
    role_family: str | None = None
    language_bucket: str | None = None
    location_type: str | None = None
    employment_type: str | None = None
    has_salary: bool | None = None
    has_skills: bool | None = None
    title_is_other: bool | None = None
    skills_contains: list[str] | None = None
    salary_currency: str | None = None
    sort_by: str = "published_at_desc"
    limit: int | None = None


def _parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _matches(row: dict[str, Any], q: QueryParams) -> bool:
    if q.normalized_title and str(row.get("normalized_title") or "") != q.normalized_title:
        return False
    if q.role_family and str(row.get("role_family") or "") != q.role_family:
        return False
    if q.language_bucket and str(row.get("language_bucket") or "") != q.language_bucket:
        return False
    if q.location_type and str(row.get("location_type") or "") != q.location_type:
        return False
    if q.employment_type and str(row.get("employment_type") or "") != q.employment_type:
        return False
    if q.salary_currency and str(row.get("salary_currency") or "") != q.salary_currency:
        return False

    if q.has_salary is not None and bool(row.get("has_salary")) is not q.has_salary:
        return False
    if q.has_skills is not None and bool(row.get("has_skills")) is not q.has_skills:
        return False
    if q.title_is_other is not None and bool(row.get("title_is_other")) is not q.title_is_other:
        return False

    if q.skills_contains:
        row_skills = row.get("skills") if isinstance(row.get("skills"), list) else []
        row_skill_set = {str(s).strip().lower() for s in row_skills if str(s).strip()}
        for token in q.skills_contains:
            if token.strip().lower() not in row_skill_set:
                return False

    return True


def _sort_rows(rows: list[dict[str, Any]], sort_by: str) -> list[dict[str, Any]]:
    if sort_by == "updated_at_desc":
        return sorted(
            rows,
            key=lambda r: (
                _parse_dt(r.get("updated_at")) is not None,
                _parse_dt(r.get("updated_at")) or datetime.min,
                str(r.get("url") or ""),
            ),
            reverse=True,
        )
    if sort_by == "url":
        return sorted(rows, key=lambda r: str(r.get("url") or ""))

    # Default: published_at desc with deterministic url fallback.
    return sorted(
        rows,
        key=lambda r: (
            _parse_dt(r.get("published_at")) is not None,
            _parse_dt(r.get("published_at")) or datetime.min,
            str(r.get("url") or ""),
        ),
        reverse=True,
    )


def run_retrieval_query(
    *,
    input_path: str | Path,
    query: QueryParams,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    in_path = Path(input_path)
    rows_total = 0
    invalid_rows = 0
    matched: list[dict[str, Any]] = []

    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            obj = json.loads(s)
            if not isinstance(obj, dict):
                invalid_rows += 1
                continue
            rows_total += 1
            if _matches(obj, query):
                matched.append(obj)

    matched = _sort_rows(matched, query.sort_by)
    if query.limit is not None:
        matched = matched[: query.limit]

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as out_f:
            for row in matched:
                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return {
        "input_path": str(in_path),
        "rows_total": rows_total,
        "invalid_rows": invalid_rows,
        "matched_rows": len(matched),
        "query": {
            "normalized_title": query.normalized_title,
            "role_family": query.role_family,
            "language_bucket": query.language_bucket,
            "location_type": query.location_type,
            "employment_type": query.employment_type,
            "has_salary": query.has_salary,
            "has_skills": query.has_skills,
            "title_is_other": query.title_is_other,
            "skills_contains": query.skills_contains or [],
            "salary_currency": query.salary_currency,
            "sort_by": query.sort_by,
            "limit": query.limit,
        },
        "results": matched,
    }
