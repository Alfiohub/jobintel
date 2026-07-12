from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.retrieval import QueryParams
from jobintel_next.serving import count_jobs, count_pack, list_jobs, run_pack


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://e/3",
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "location_type": "remote",
            "employment_type": "full_time",
            "has_salary": False,
            "has_skills": False,
            "title_is_other": False,
            "skills": [],
            "salary_currency": None,
            "published_at": "2026-03-10T10:00:00+00:00",
            "updated_at": "2026-03-12T10:00:00+00:00",
        },
        {
            "url": "https://e/2",
            "title_raw": "Senior Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "location_type": "hybrid",
            "employment_type": "full_time",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": False,
            "skills": ["python", "sql"],
            "salary_currency": "USD",
            "published_at": "2026-03-09T10:00:00+00:00",
            "updated_at": "2026-03-13T10:00:00+00:00",
        },
        {
            "url": "https://e/1",
            "title_raw": "General Role",
            "normalized_title": "other",
            "role_family": "other",
            "language_bucket": "en",
            "location_type": "onsite",
            "employment_type": "contract",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": True,
            "skills": ["python"],
            "salary_currency": "EUR",
            "published_at": "2026-03-08T10:00:00+00:00",
            "updated_at": "2026-03-09T10:00:00+00:00",
        },
    ]


def test_list_jobs_with_filters_and_pagination(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    rep = list_jobs(
        input_path=p,
        query=QueryParams(has_skills=True, language_bucket="en", sort_by="updated_at_desc"),
        limit=1,
        offset=1,
    )
    assert rep["total_count"] == 2
    assert rep["returned_count"] == 1
    assert rep["results"][0]["url"] == "https://e/1"


def test_count_jobs_with_filters(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    rep = count_jobs(input_path=p, query=QueryParams(normalized_title="software_engineer"))
    assert rep["count"] == 1


def test_pack_query_and_count(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    pack_rep = run_pack(input_path=p, pack_name="account_executive_jobs", limit=10, offset=0)
    count_rep = count_pack(input_path=p, pack_name="account_executive_jobs")
    assert pack_rep["total_count"] == 1
    assert pack_rep["returned_count"] == 1
    assert count_rep["count"] == 1
