from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.product.job_state import set_job_state
from jobintel_next.product.saved_searches import build_saved_search_insight, create_saved_search
from jobintel_next.storage import build_sqlite_index


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://e/1",
            "title_raw": "Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "published_at": "2026-03-10T00:00:00+00:00",
        },
        {
            "url": "https://e/2",
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "published_at": "2026-03-11T00:00:00+00:00",
        },
    ]


def test_saved_search_insight_counts_and_rates(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    state_db = tmp_path / "state.db"
    jobs_json = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    _write(jobs_json, _rows())
    build_sqlite_index(input_path=jobs_json, sqlite_path=jobs_db)

    s = create_saved_search(
        db_path=saved_db,
        name="all jobs",
        query_type="filters",
        filters_json="{}",
        user_id="u1",
        user_email="u1@example.com",
    )
    set_job_state(db_path=state_db, user_id="u1", user_email="u1@example.com", job_url="https://e/1", state="saved")
    set_job_state(db_path=state_db, user_id="u1", user_email="u1@example.com", job_url="https://e/2", state="dismissed")

    insight = build_saved_search_insight(
        db_path=str(saved_db),
        job_state_db_path=str(state_db),
        search_id=str(s["search_id"]),
        indexed_input_path=str(jobs_json),
        indexed_sqlite_path=str(jobs_db),
        user_id="u1",
        latest_new_count=1,
        scan_limit=100,
    )
    assert insight["current_count"] == 2
    assert insight["saved_marked_count"] == 1
    assert insight["dismissed_marked_count"] == 1
    assert insight["saved_rate"] == 0.5
    assert insight["dismiss_rate"] == 0.5


def test_saved_search_insight_handles_no_state_and_no_history(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    state_db = tmp_path / "state.db"
    jobs_json = tmp_path / "jobs.jsonl"
    _write(jobs_json, _rows())

    s = create_saved_search(
        db_path=saved_db,
        name="se only",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        user_id="u1",
        user_email="u1@example.com",
    )

    insight = build_saved_search_insight(
        db_path=str(saved_db),
        job_state_db_path=str(state_db),
        search_id=str(s["search_id"]),
        indexed_input_path=str(jobs_json),
        indexed_sqlite_path=None,
        user_id="u1",
        latest_new_count=None,
        scan_limit=100,
    )
    assert insight["current_count"] == 1
    assert insight["latest_new_count"] is None
    assert insight["saved_marked_count"] == 0
    assert insight["dismissed_marked_count"] == 0
