from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3

from jobintel_next.product.saved_searches import archive_saved_search, create_saved_search, get_saved_search, is_saved_search_due, run_due_saved_searches
from jobintel_next.storage import build_sqlite_index


def _write(path: Path, rows: list[dict]) -> None:
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
            "has_skills": True,
            "skills": ["python"],
        }
    ]


def test_is_saved_search_due_logic_manual_daily_twice_daily() -> None:
    now = datetime(2026, 3, 31, 12, 0, tzinfo=timezone.utc)

    assert is_saved_search_due({"is_enabled": True, "frequency": "manual", "last_run_at": None}, now=now) is False
    assert is_saved_search_due({"is_enabled": False, "frequency": "daily", "last_run_at": None}, now=now) is False
    assert is_saved_search_due({"is_enabled": True, "frequency": "daily", "last_run_at": None}, now=now) is True
    assert (
        is_saved_search_due(
            {"is_enabled": True, "frequency": "daily", "last_run_at": (now - timedelta(hours=23)).isoformat()},
            now=now,
        )
        is False
    )
    assert (
        is_saved_search_due(
            {"is_enabled": True, "frequency": "daily", "last_run_at": (now - timedelta(hours=25)).isoformat()},
            now=now,
        )
        is True
    )
    assert (
        is_saved_search_due(
            {"is_enabled": True, "frequency": "twice_daily", "last_run_at": (now - timedelta(hours=11)).isoformat()},
            now=now,
        )
        is False
    )
    assert (
        is_saved_search_due(
            {"is_enabled": True, "frequency": "twice_daily", "last_run_at": (now - timedelta(hours=13)).isoformat()},
            now=now,
        )
        is True
    )


def test_run_due_saved_searches_runs_only_due(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"
    _write(jobs_jsonl, _rows())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    s_manual = create_saved_search(
        db_path=saved_db,
        name="manual search",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="manual",
    )
    s_due = create_saved_search(
        db_path=saved_db,
        name="due daily search",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
    )
    s_not_due = create_saved_search(
        db_path=saved_db,
        name="not due daily search",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
    )

    now = datetime.now(timezone.utc)
    with sqlite3.connect(saved_db) as conn:
        conn.execute(
            "UPDATE saved_searches SET last_run_at = ? WHERE search_id = ?",
            ((now - timedelta(days=2)).isoformat(), s_due["search_id"]),
        )
        conn.execute(
            "UPDATE saved_searches SET last_run_at = ? WHERE search_id = ?",
            ((now - timedelta(hours=2)).isoformat(), s_not_due["search_id"]),
        )
        conn.commit()

    rep = run_due_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        outdir=outdir,
    )
    assert rep["run_scope"] == "due_only"
    assert rep["searches_total"] == 3
    assert rep["searches_due"] == 1
    assert rep["searches_skipped_not_due"] == 2
    assert rep["processed_ok"] == 1
    assert rep["processed_error"] == 0
    assert len(rep["results"]) == 1
    assert rep["results"][0]["name"] == "due daily search"
    assert rep["results"][0]["frequency"] == "daily"
    assert Path(rep["json_report_path"]).exists()
    assert Path(rep["md_report_path"]).exists()

    after_due = get_saved_search(db_path=saved_db, search_id=s_due["search_id"])
    after_manual = get_saved_search(db_path=saved_db, search_id=s_manual["search_id"])
    after_not_due = get_saved_search(db_path=saved_db, search_id=s_not_due["search_id"])
    assert after_due["last_run_at"] is not None
    assert after_manual["last_run_at"] is None
    assert after_not_due["last_run_at"] is not None


def test_run_due_ignores_archived_saved_search(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"
    _write(jobs_jsonl, _rows())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    active = create_saved_search(
        db_path=saved_db,
        name="active due",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
    )
    archived = create_saved_search(
        db_path=saved_db,
        name="archived due",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
    )
    archive_saved_search(db_path=saved_db, search_id=archived["search_id"])

    rep = run_due_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        outdir=outdir,
    )
    assert rep["searches_total"] == 2
    assert rep["searches_due"] == 1
    assert len(rep["results"]) == 1
    assert rep["results"][0]["search_id"] == active["search_id"]
