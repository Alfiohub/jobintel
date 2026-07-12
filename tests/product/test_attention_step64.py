from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.product.application_tracking import update_application_details
from jobintel_next.product.attention import build_attention_items_for_user
from jobintel_next.product.auth import create_local_user, update_user_settings
from jobintel_next.product.job_state import set_job_state
from jobintel_next.product.saved_searches import create_saved_search
from jobintel_next.storage import build_sqlite_index


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_attention_items_generation_high_roi_signals(tmp_path: Path) -> None:
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    saved_db = tmp_path / "saved.db"
    job_state_db = tmp_path / "job_state.db"
    runs_dir = tmp_path / "alerts" / "runs"
    runs_user = runs_dir / "u1"
    runs_user.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "url": f"https://e/{i}",
            "title_raw": "Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "published_at": "2026-03-10T00:00:00+00:00",
        }
        for i in range(1, 7)
    ]
    _write(jobs_jsonl, rows)
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    s = create_saved_search(
        db_path=saved_db,
        name="SE daily",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
        user_id="u1",
        user_email="u1@example.com",
    )

    for i in range(1, 5):
        set_job_state(
            db_path=job_state_db,
            job_url=f"https://e/{i}",
            state="dismissed",
            user_id="u1",
            user_email="u1@example.com",
        )

    set_job_state(
        db_path=job_state_db,
        job_url="https://e/6",
        state="saved",
        user_id="u1",
        user_email="u1@example.com",
    )
    update_application_details(
        db_path=job_state_db,
        job_url="https://e/6",
        notes="",
        follow_up_at="2020-01-01",
        follow_up_note="send follow-up",
        user_id="u1",
        user_email="u1@example.com",
    )

    run_id = "run_digest_err"
    (runs_user / f"{run_id}.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "user_id": "u1",
                "run_timestamp": "2026-04-01T10:00:00+00:00",
                "processed_ok": 1,
                "processed_error": 0,
                "searches_total": 1,
                "total_new_matches": 0,
                "results": [],
                "digest_delivery": {"email_error": True},
            }
        ),
        encoding="utf-8",
    )

    items = build_attention_items_for_user(
        saved_db_path=str(saved_db),
        job_state_db_path=str(job_state_db),
        runs_dir=str(runs_dir),
        indexed_input_path=str(jobs_jsonl),
        indexed_sqlite_path=str(jobs_db),
        user_id="u1",
        max_items=20,
    )
    assert items
    types = {str(x.get("type") or "") for x in items}
    assert "follow_up" in types
    assert "saved_search_due" in types
    assert "digest_error" in types
    # high dismiss flag from insights should appear
    assert any("high dismiss rate" in str(x.get("title") or "") for x in items)
    assert any(str(x.get("href") or "").startswith("/admin/") for x in items)

    # sanity: entry has stable fields
    first = items[0]
    assert str(first.get("priority") or "") in {"high", "medium", "low"}


def test_attention_items_respect_user_preferences(tmp_path: Path) -> None:
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    saved_db = tmp_path / "saved.db"
    job_state_db = tmp_path / "job_state.db"
    runs_dir = tmp_path / "alerts" / "runs"
    runs_user = runs_dir / "u1"
    runs_user.mkdir(parents=True, exist_ok=True)

    _write(
        jobs_jsonl,
        [
            {
                "url": "https://e/1",
                "title_raw": "Software Engineer",
                "normalized_title": "software_engineer",
                "role_family": "software_engineering",
                "language_bucket": "en",
                "published_at": "2026-03-10T00:00:00+00:00",
            }
        ],
    )
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)
    create_local_user(db_path=saved_db, email="u1@example.com", password="password1", user_id="u1")
    create_saved_search(
        db_path=saved_db,
        name="SE daily",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
        user_id="u1",
        user_email="u1@example.com",
    )
    set_job_state(
        db_path=job_state_db,
        job_url="https://e/1",
        state="saved",
        user_id="u1",
        user_email="u1@example.com",
    )
    update_application_details(
        db_path=job_state_db,
        job_url="https://e/1",
        notes="",
        follow_up_at="2020-01-01",
        follow_up_note="follow",
        user_id="u1",
        user_email="u1@example.com",
    )
    (runs_user / "r1.json").write_text(
        json.dumps(
            {
                "run_id": "r1",
                "user_id": "u1",
                "run_timestamp": "2026-04-01T10:00:00+00:00",
                "processed_ok": 1,
                "processed_error": 0,
                "searches_total": 1,
                "total_new_matches": 0,
                "results": [],
                "digest_delivery": {"email_error": True},
            }
        ),
        encoding="utf-8",
    )

    update_user_settings(
        db_path=saved_db,
        user_id="u1",
        email="u1@example.com",
        show_saved_search_quality_attention=False,
        show_due_saved_search_attention=False,
        show_follow_up_attention=True,
        show_digest_error_attention=False,
        digest_include_attention=False,
    )

    items = build_attention_items_for_user(
        saved_db_path=str(saved_db),
        job_state_db_path=str(job_state_db),
        runs_dir=str(runs_dir),
        indexed_input_path=str(jobs_jsonl),
        indexed_sqlite_path=str(jobs_db),
        user_id="u1",
        max_items=20,
    )
    assert items
    types = {str(x.get("type") or "") for x in items}
    assert "follow_up" in types
    assert "saved_search_due" not in types
    assert "digest_error" not in types
    assert "saved_search_quality" not in types
