from __future__ import annotations

import json
import sqlite3
from typing import Any

from fastapi import FastAPI, Query

try:
    from automation.microsaas.ranking import rank_jobs
except ModuleNotFoundError:
    from ranking import rank_jobs


app = FastAPI(title="microsaas-search-mvp")


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def _to_job_dict(row: sqlite3.Row) -> dict[str, Any]:
    out = dict(row)
    skills_json = out.get("skills_json")
    if isinstance(skills_json, str):
        try:
            out["skills"] = json.loads(skills_json)
        except Exception:
            out["skills"] = []
    else:
        out["skills"] = []
    return out


def _skills_from_param(skills: str | None) -> list[str]:
    if not skills:
        return []
    return [s.strip().lower() for s in skills.split(",") if s.strip()]


def search_jobs(
    *,
    db_path: str,
    normalized_title: str | None = None,
    role_family: str | None = None,
    country: str | None = None,
    location_type: str | None = None,
    seniority: str | None = None,
    employment_type: str | None = None,
    min_salary: int | None = None,
    skills: str | None = None,
    limit: int = 20,
    use_ranking: bool = True,
) -> dict[str, Any]:
    where: list[str] = []
    params: list[Any] = []

    if normalized_title:
        where.append("LOWER(normalized_title) = LOWER(?)")
        params.append(normalized_title)
    if role_family:
        where.append("LOWER(role_family) = LOWER(?)")
        params.append(role_family)
    if country:
        where.append("LOWER(country) = LOWER(?)")
        params.append(country)
    if location_type:
        where.append("LOWER(location_type) = LOWER(?)")
        params.append(location_type)
    if seniority:
        where.append("LOWER(seniority) = LOWER(?)")
        params.append(seniority)
    if employment_type:
        where.append("LOWER(employment_type) = LOWER(?)")
        params.append(employment_type)
    if min_salary is not None:
        where.append("salary_max IS NOT NULL AND salary_max >= ?")
        params.append(int(min_salary))

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with _connect(db_path) as con:
        count_row = con.execute(f"SELECT COUNT(*) AS c FROM jobs_indexed {where_sql}", params).fetchone()
        total_matched = int(count_row["c"]) if count_row else 0

        sql = (
            "SELECT id, url, company_name, title_raw, title_clean, normalized_title, role_family, occupation_group, "
            "seniority, employment_type, location_type, city, region, country, salary_min, salary_max, salary_currency, "
            "skills_json, indexed_at "
            f"FROM jobs_indexed {where_sql} "
            "ORDER BY indexed_at DESC "
            "LIMIT ?"
        )
        query_params = [*params, max(1, min(200, int(limit)))]
        rows = con.execute(sql, query_params).fetchall()

    jobs = [_to_job_dict(r) for r in rows]
    requested_skills = _skills_from_param(skills)

    if use_ranking:
        user_query = {
            "hard": {
                "country": country,
                "location_type": location_type,
                "employment_type": employment_type,
            },
            "preferred": {
                "normalized_title": normalized_title,
                "role_family": role_family,
                "country": country,
                "location_type": location_type,
                "seniority": seniority,
                "employment_type": employment_type,
                "salary_min": min_salary,
                "skills": requested_skills,
            },
        }
        jobs = rank_jobs(jobs, user_query)
    else:
        for job in jobs:
            job["total_score"] = 0.0
            job["score_breakdown"] = {}
            job["hard_filter_passed"] = True

    return {
        "total_matched": total_matched,
        "returned_count": len(jobs),
        "results": jobs,
    }


@app.get("/search")
def search(
    normalized_title: str | None = Query(default=None),
    role_family: str | None = Query(default=None),
    country: str | None = Query(default=None),
    location_type: str | None = Query(default=None),
    seniority: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    min_salary: int | None = Query(default=None, ge=0),
    skills: str | None = Query(default=None, description="Comma-separated, e.g. python,sql,aws"),
    limit: int = Query(default=20, ge=1, le=200),
    use_ranking: bool = Query(default=True),
    db_path: str = Query(default="data/jobintel_microsaas.sqlite"),
) -> dict[str, Any]:
    return search_jobs(
        db_path=db_path,
        normalized_title=normalized_title,
        role_family=role_family,
        country=country,
        location_type=location_type,
        seniority=seniority,
        employment_type=employment_type,
        min_salary=min_salary,
        skills=skills,
        limit=limit,
        use_ranking=use_ranking,
    )

