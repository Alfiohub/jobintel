from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


STATE_WEIGHT = {
    "new": 20.0,
    "seen": 8.0,
    "saved": 14.0,
    "dismissed": -60.0,
}


def _now_utc(now: datetime | None = None) -> datetime:
    return now if now is not None else datetime.now(timezone.utc)


def _parse_ts(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _freshness_points(ts: datetime | None, *, now: datetime) -> float:
    if ts is None:
        return 0.0
    age_days = max(0.0, (now - ts).total_seconds() / 86400.0)
    # Linear decay over 30 days.
    return max(0.0, 30.0 - age_days)


def compute_job_rank_score(
    *,
    job: dict[str, Any],
    job_state: str = "new",
    expected_normalized_title: str | None = None,
    expected_role_family: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now_dt = _now_utc(now)

    published_points = _freshness_points(_parse_ts(job.get("published_at")), now=now_dt)
    updated_points = _freshness_points(_parse_ts(job.get("updated_at")), now=now_dt) * 0.35

    state = str(job_state or "new").strip().lower()
    state_points = float(STATE_WEIGHT.get(state, 0.0))

    has_salary_points = 7.0 if bool(job.get("has_salary")) else 0.0
    has_skills_points = 6.0 if bool(job.get("has_skills")) else 0.0

    location_type = str(job.get("location_type") or "").strip().lower()
    location_points = 0.0
    if location_type == "remote":
        location_points = 4.0
    elif location_type == "hybrid":
        location_points = 1.5

    title_other_penalty = -9.0 if bool(job.get("title_is_other")) else 0.0

    title_fit_points = 0.0
    expected_title = (expected_normalized_title or "").strip().lower()
    if expected_title:
        actual_title = str(job.get("normalized_title") or "").strip().lower()
        if actual_title and actual_title == expected_title:
            title_fit_points = 10.0

    role_fit_points = 0.0
    expected_role = (expected_role_family or "").strip().lower()
    if expected_role:
        actual_role = str(job.get("role_family") or "").strip().lower()
        if actual_role and actual_role == expected_role:
            role_fit_points = 6.0

    score = (
        published_points
        + updated_points
        + state_points
        + has_salary_points
        + has_skills_points
        + location_points
        + title_other_penalty
        + title_fit_points
        + role_fit_points
    )

    factors = {
        "freshness_published": round(published_points, 3),
        "freshness_updated": round(updated_points, 3),
        "job_state": round(state_points, 3),
        "has_salary": round(has_salary_points, 3),
        "has_skills": round(has_skills_points, 3),
        "location_type": round(location_points, 3),
        "title_is_other": round(title_other_penalty, 3),
        "title_fit": round(title_fit_points, 3),
        "role_fit": round(role_fit_points, 3),
    }

    return {
        "rank_score": round(score, 3),
        "rank_factors": factors,
    }


def rank_jobs(
    *,
    rows: list[dict[str, Any]],
    states_by_url: dict[str, str] | None = None,
    expected_normalized_title: str | None = None,
    expected_role_family: str | None = None,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    states = states_by_url or {}
    enriched: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        url = str(item.get("url") or "")
        st = states.get(url, str(item.get("job_state") or "new"))
        rank = compute_job_rank_score(
            job=item,
            job_state=st,
            expected_normalized_title=expected_normalized_title,
            expected_role_family=expected_role_family,
            now=now,
        )
        item["job_state"] = st
        item["rank_score"] = rank["rank_score"]
        item["rank_factors"] = rank["rank_factors"]
        enriched.append(item)

    # Stable sort: highest score first, then newer published_at, then URL.
    def _sort_key(x: dict[str, Any]) -> tuple[float, float, str]:
        pub = _parse_ts(x.get("published_at"))
        pub_ts = pub.timestamp() if pub is not None else 0.0
        return (float(x.get("rank_score") or 0.0), pub_ts, str(x.get("url") or ""))

    return sorted(enriched, key=_sort_key, reverse=True)
