from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from jobintel_next.pipelines.retrieval import QueryParams, get_query_packs


SELECT_COLUMNS = """
url, source, source_org, company_name, title_raw, title_clean, normalized_title, role_family,
classification_status, match_method, confidence, language_bucket, language_reason, language_code,
language_confidence, published_at, updated_at, seniority, employment_type, location_type, city,
region, country, salary_min, salary_max, salary_currency, salary_period, has_salary, has_skills,
has_location, title_is_other, skills_json
"""

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


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    obj = dict(row)
    obj["has_salary"] = bool(obj.get("has_salary"))
    obj["has_skills"] = bool(obj.get("has_skills"))
    obj["has_location"] = bool(obj.get("has_location"))
    obj["title_is_other"] = bool(obj.get("title_is_other"))
    skills_raw = obj.pop("skills_json", "[]")
    try:
        parsed = json.loads(skills_raw)
        obj["skills"] = parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        obj["skills"] = []
    return obj


def _where_clause(q: QueryParams) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []

    def add(cond: str, value: Any) -> None:
        clauses.append(cond)
        params.append(value)

    if q.normalized_title:
        add("normalized_title = ?", q.normalized_title)
    if q.role_family:
        add("role_family = ?", q.role_family)
    if q.language_bucket:
        add("language_bucket = ?", q.language_bucket)
    if q.location_type:
        add("location_type = ?", q.location_type)
    if q.employment_type:
        add("employment_type = ?", q.employment_type)
    if q.salary_currency:
        add("salary_currency = ?", q.salary_currency)
    if q.has_salary is not None:
        add("has_salary = ?", 1 if q.has_salary else 0)
    if q.has_skills is not None:
        add("has_skills = ?", 1 if q.has_skills else 0)
    if q.title_is_other is not None:
        add("title_is_other = ?", 1 if q.title_is_other else 0)

    if q.skills_contains:
        for token in q.skills_contains:
            tok = str(token).strip().lower()
            if not tok:
                continue
            add("skills_json LIKE ?", f'%"{tok}"%')

    if not clauses:
        return "", params
    return " WHERE " + " AND ".join(clauses), params


def _order_clause(sort_by: str) -> str:
    if sort_by == "updated_at_desc":
        return " ORDER BY (updated_at IS NULL) ASC, updated_at DESC, url DESC "
    if sort_by == "url":
        return " ORDER BY url ASC "
    return " ORDER BY (published_at IS NULL) ASC, published_at DESC, url DESC "


def sqlite_list_jobs(
    *,
    sqlite_path: str | Path,
    query: QueryParams,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    db_path = Path(sqlite_path)
    where_sql, params = _where_clause(query)
    order_sql = _order_clause(query.sort_by)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        count_sql = "SELECT COUNT(*) FROM jobs_indexed" + where_sql
        total_count = int(conn.execute(count_sql, params).fetchone()[0])

        data_sql = (
            "SELECT "
            + SELECT_COLUMNS
            + " FROM jobs_indexed"
            + where_sql
            + order_sql
            + " LIMIT ? OFFSET ?"
        )
        rows = conn.execute(data_sql, [*params, int(limit), int(offset)]).fetchall()
        results = [_row_to_dict(r) for r in rows]
    finally:
        conn.close()

    return {
        "operation": "list_jobs",
        "input_path": str(db_path),
        "backend": "sqlite",
        "query": _query_dict(query),
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "returned_count": len(results),
        "results": results,
    }


def sqlite_count_jobs(*, sqlite_path: str | Path, query: QueryParams) -> dict[str, Any]:
    db_path = Path(sqlite_path)
    where_sql, params = _where_clause(query)
    conn = sqlite3.connect(db_path)
    try:
        count_sql = "SELECT COUNT(*) FROM jobs_indexed" + where_sql
        count = int(conn.execute(count_sql, params).fetchone()[0])
    finally:
        conn.close()
    return {
        "operation": "count_jobs",
        "input_path": str(db_path),
        "backend": "sqlite",
        "query": _query_dict(query),
        "count": count,
    }


def sqlite_run_pack(
    *,
    sqlite_path: str | Path,
    pack_name: str,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    packs = get_query_packs()
    if pack_name not in packs:
        raise ValueError(f"unknown query pack: {pack_name}")
    spec = packs[pack_name]

    by_url: dict[str, dict[str, Any]] = {}
    clauses: list[dict[str, Any]] = []
    for clause in spec.clauses:
        rep = sqlite_list_jobs(sqlite_path=sqlite_path, query=clause.query, limit=1_000_000, offset=0)
        clauses.append(
            {
                "clause_name": clause.name,
                "query": _query_dict(clause.query),
                "matched_rows": rep["total_count"],
            }
        )
        for row in rep["results"]:
            url = str(row.get("url") or "")
            if url and url not in by_url:
                by_url[url] = row

    all_rows = list(by_url.values())
    sort_query = QueryParams(sort_by=spec.clauses[0].query.sort_by if spec.clauses else "published_at_desc")
    # Reuse order by with SQLite by loading URLs into temp query would be complex; deterministic fallback.
    if sort_query.sort_by == "updated_at_desc":
        all_rows.sort(key=lambda r: ((r.get("updated_at") is None), r.get("updated_at") or "", r.get("url") or ""), reverse=False)
        all_rows.reverse()
    elif sort_query.sort_by == "url":
        all_rows.sort(key=lambda r: str(r.get("url") or ""))
    else:
        all_rows.sort(key=lambda r: ((r.get("published_at") is None), r.get("published_at") or "", r.get("url") or ""), reverse=False)
        all_rows.reverse()

    total = len(all_rows)
    paged = all_rows[offset : offset + limit]
    return {
        "operation": "run_pack",
        "input_path": str(sqlite_path),
        "backend": "sqlite",
        "pack_name": pack_name,
        "description": spec.description,
        "quality": spec.quality,
        "tradeoff": spec.tradeoff,
        "clauses": clauses,
        "total_count": total,
        "limit": limit,
        "offset": offset,
        "returned_count": len(paged),
        "results": paged,
    }


def sqlite_count_pack(*, sqlite_path: str | Path, pack_name: str) -> dict[str, Any]:
    rep = sqlite_run_pack(sqlite_path=sqlite_path, pack_name=pack_name, limit=1_000_000, offset=0)
    return {
        "operation": "count_pack",
        "input_path": str(sqlite_path),
        "backend": "sqlite",
        "pack_name": pack_name,
        "count": rep["total_count"],
    }


def sqlite_get_facets(
    *,
    sqlite_path: str | Path,
    query: QueryParams,
    include_fields: list[str] | None = None,
) -> dict[str, Any]:
    db_path = Path(sqlite_path)
    where_sql, params = _where_clause(query)
    fields = include_fields or FACET_FIELDS

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        total_count = int(conn.execute("SELECT COUNT(*) FROM jobs_indexed" + where_sql, params).fetchone()[0])
        facets: dict[str, list[dict[str, Any]]] = {}
        for field in fields:
            if field not in FACET_FIELDS:
                continue
            sql = f"SELECT {field} AS bucket_value, COUNT(*) AS c FROM jobs_indexed{where_sql} GROUP BY {field} ORDER BY c DESC"
            rows = conn.execute(sql, params).fetchall()
            buckets: list[dict[str, Any]] = []
            for r in rows:
                value: Any = r["bucket_value"]
                if field in {"has_salary", "has_skills", "title_is_other"} and value is not None:
                    value = bool(int(value))
                buckets.append({"value": value, "count": int(r["c"])})
            facets[field] = buckets
    finally:
        conn.close()

    return {
        "operation": "get_facets",
        "input_path": str(db_path),
        "backend": "sqlite",
        "query": _query_dict(query),
        "total_count": total_count,
        "facets": facets,
    }
