from __future__ import annotations

from datetime import datetime, timezone

from jobintel_next.product.ranking import compute_job_rank_score, rank_jobs


NOW = datetime(2026, 3, 31, 12, 0, tzinfo=timezone.utc)


def _job(
    *,
    url: str,
    published_at: str,
    normalized_title: str = "software_engineer",
    role_family: str = "software_engineering",
    has_salary: bool = False,
    has_skills: bool = False,
    location_type: str | None = None,
    title_is_other: bool = False,
) -> dict:
    return {
        "url": url,
        "published_at": published_at,
        "normalized_title": normalized_title,
        "role_family": role_family,
        "has_salary": has_salary,
        "has_skills": has_skills,
        "location_type": location_type,
        "title_is_other": title_is_other,
    }


def test_rank_score_prefers_new_over_dismissed() -> None:
    j = _job(url="https://e/1", published_at="2026-03-30T00:00:00+00:00", has_skills=True)
    s_new = compute_job_rank_score(job=j, job_state="new", now=NOW)["rank_score"]
    s_dismissed = compute_job_rank_score(job=j, job_state="dismissed", now=NOW)["rank_score"]
    assert s_new > s_dismissed


def test_rank_score_prefers_title_fit_when_expected_title_set() -> None:
    good = _job(url="https://e/1", published_at="2026-03-29T00:00:00+00:00", normalized_title="software_engineer")
    bad = _job(url="https://e/2", published_at="2026-03-30T00:00:00+00:00", normalized_title="account_executive")

    good_score = compute_job_rank_score(
        job=good,
        job_state="new",
        expected_normalized_title="software_engineer",
        now=NOW,
    )["rank_score"]
    bad_score = compute_job_rank_score(
        job=bad,
        job_state="new",
        expected_normalized_title="software_engineer",
        now=NOW,
    )["rank_score"]
    assert good_score > bad_score


def test_rank_jobs_orders_by_score_desc() -> None:
    rows = [
        _job(url="https://e/1", published_at="2026-03-30T00:00:00+00:00", has_skills=True),
        _job(url="https://e/2", published_at="2026-03-31T00:00:00+00:00", has_skills=False),
    ]
    ranked = rank_jobs(
        rows=rows,
        states_by_url={"https://e/1": "saved", "https://e/2": "dismissed"},
        now=NOW,
    )
    assert ranked[0]["url"] == "https://e/1"
    assert ranked[0]["rank_score"] >= ranked[1]["rank_score"]
