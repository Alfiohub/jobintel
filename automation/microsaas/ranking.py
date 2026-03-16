from __future__ import annotations

import json
from typing import Any


def _s(value: Any) -> str:
    return str(value or "").strip()


def _norm(value: Any) -> str:
    return _s(value).lower()


def _norm_set(values: Any) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, (str, int, float, bool)):
        raw = [str(values)]
    elif isinstance(values, (list, tuple, set)):
        raw = [str(v) for v in values if _s(v)]
    else:
        return set()
    return {_norm(v) for v in raw if _s(v)}


def _get_query_value(query: dict[str, Any], keys: list[str], *, section: str | None = None) -> Any:
    if section:
        sub = query.get(section)
        if isinstance(sub, dict):
            for key in keys:
                if key in sub and sub.get(key) is not None:
                    return sub.get(key)
    for key in keys:
        if key in query and query.get(key) is not None:
            return query.get(key)
    return None


def _extract_skills(job: dict[str, Any]) -> set[str]:
    raw = job.get("skills_json")
    if isinstance(raw, list):
        return _norm_set(raw)
    if isinstance(raw, str):
        txt = raw.strip()
        if not txt:
            return set()
        try:
            parsed = json.loads(txt)
            if isinstance(parsed, list):
                return _norm_set(parsed)
        except Exception:
            pass
        return _norm_set([p for p in txt.split(";") if _s(p)])
    return set()


def _coerce_int(value: Any) -> int | None:
    try:
        return int(float(_s(value)))
    except Exception:
        return None


def _salary_score(job: dict[str, Any], user_query: dict[str, Any]) -> float:
    target = _coerce_int(
        _get_query_value(
            user_query,
            ["salary_min", "salary_target", "target_salary_min"],
            section="preferred",
        )
    )
    if target is None or target <= 0:
        return 0.0

    wanted_ccy = _norm(
        _get_query_value(
            user_query,
            ["salary_currency", "currency"],
            section="preferred",
        )
    )
    job_ccy = _norm(job.get("salary_currency"))
    if wanted_ccy and job_ccy and wanted_ccy != job_ccy:
        return 0.0

    job_min = _coerce_int(job.get("salary_min"))
    job_max = _coerce_int(job.get("salary_max"))
    if job_min is None and job_max is None:
        return 0.0

    upper = max(x for x in [job_min, job_max] if x is not None)
    if upper >= target:
        return 1.0
    return max(0.0, min(1.0, upper / float(target)))


def _hard_filter_pass(job: dict[str, Any], user_query: dict[str, Any]) -> bool:
    hard_country = _norm_set(
        _get_query_value(user_query, ["country", "countries", "country_required"], section="hard")
    )
    hard_location_type = _norm_set(
        _get_query_value(user_query, ["location_type", "location_type_required"], section="hard")
    )
    hard_employment_type = _norm_set(
        _get_query_value(user_query, ["employment_type", "employment_type_required"], section="hard")
    )

    if hard_country and _norm(job.get("country")) not in hard_country:
        return False
    if hard_location_type and _norm(job.get("location_type")) not in hard_location_type:
        return False
    if hard_employment_type and _norm(job.get("employment_type")) not in hard_employment_type:
        return False
    return True


def score_job(job: dict[str, Any], user_query: dict[str, Any]) -> dict[str, Any]:
    hard_passed = _hard_filter_pass(job, user_query)

    desired_titles = _norm_set(
        _get_query_value(user_query, ["normalized_title", "titles", "title"], section="preferred")
    )
    desired_roles = _norm_set(
        _get_query_value(user_query, ["role_family", "role_families"], section="preferred")
    )
    desired_countries = _norm_set(
        _get_query_value(user_query, ["country", "countries"], section="preferred")
    )
    desired_location_types = _norm_set(
        _get_query_value(user_query, ["location_type", "location_types"], section="preferred")
    )
    desired_seniority = _norm_set(
        _get_query_value(user_query, ["seniority", "seniority_levels"], section="preferred")
    )
    desired_employment = _norm_set(
        _get_query_value(user_query, ["employment_type", "employment_types"], section="preferred")
    )
    desired_skills = _norm_set(
        _get_query_value(user_query, ["skills", "required_skills"], section="preferred")
    )

    job_title = _norm(job.get("normalized_title"))
    job_role = _norm(job.get("role_family"))
    job_country = _norm(job.get("country"))
    job_location_type = _norm(job.get("location_type"))
    job_seniority = _norm(job.get("seniority"))
    job_employment = _norm(job.get("employment_type"))
    job_skills = _extract_skills(job)

    title_role_match = 0.0
    if desired_titles and job_title in desired_titles:
        title_role_match = 1.0
    elif desired_roles and job_role in desired_roles:
        title_role_match = 0.8
    elif desired_titles or desired_roles:
        title_role_match = 0.0

    country_match = 1.0 if (desired_countries and job_country in desired_countries) else 0.0
    location_type_match = 1.0 if (desired_location_types and job_location_type in desired_location_types) else 0.0
    seniority_match = 1.0 if (desired_seniority and job_seniority in desired_seniority) else 0.0
    employment_type_match = 1.0 if (desired_employment and job_employment in desired_employment) else 0.0

    skills_overlap = 0.0
    if desired_skills:
        skills_overlap = len(job_skills & desired_skills) / float(len(desired_skills))

    salary_match = _salary_score(job, user_query)

    score_breakdown = {
        "title_role_match": round(title_role_match * 30.0, 4),
        "country_match": round(country_match * 10.0, 4),
        "location_type_match": round(location_type_match * 10.0, 4),
        "seniority_match": round(seniority_match * 10.0, 4),
        "employment_type_match": round(employment_type_match * 10.0, 4),
        "salary_match": round(salary_match * 15.0, 4),
        "skills_overlap": round(skills_overlap * 15.0, 4),
    }
    total_score = round(sum(score_breakdown.values()), 4)

    return {
        "total_score": total_score,
        "score_breakdown": score_breakdown,
        "hard_filter_passed": hard_passed,
    }


def rank_jobs(jobs: list[dict[str, Any]], user_query: dict[str, Any]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for job in jobs:
        scored = score_job(job, user_query)
        out = dict(job)
        out.update(scored)
        ranked.append(out)
    ranked.sort(key=lambda r: (bool(r.get("hard_filter_passed")), float(r.get("total_score") or 0.0)), reverse=True)
    return ranked

