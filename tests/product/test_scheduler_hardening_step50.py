from __future__ import annotations

import argparse
import json
from pathlib import Path

from jobintel_next.cli import _cmd_alerts_run_due
from jobintel_next.product.saved_searches import create_saved_search, run_due_saved_searches
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


def test_run_due_lock_acquired_and_released_with_consistent_artifact(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"
    _write(jobs_jsonl, _rows())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)
    create_saved_search(
        db_path=saved_db,
        name="daily se",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
    )

    rep = run_due_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        outdir=outdir,
    )
    assert rep["lock_acquired"] is True
    assert rep["status"] == "ok"
    assert rep["started_at"]
    assert rep["finished_at"]
    assert isinstance(rep["duration_seconds"], float)
    assert Path(rep["json_report_path"]).exists()
    assert Path(rep["md_report_path"]).exists()
    lock_path = Path(rep["lock_path"])
    assert not lock_path.exists()

    obj = json.loads(Path(rep["json_report_path"]).read_text(encoding="utf-8"))
    assert obj["lock_acquired"] is True
    assert obj["status"] == "ok"
    assert "duration_seconds" in obj


def test_run_due_is_blocked_when_lock_exists(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"
    _write(jobs_jsonl, _rows())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)
    create_saved_search(
        db_path=saved_db,
        name="daily se",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
    )

    lock_path = outdir / "local-user" / ".run_due.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text('{"pid":123}', encoding="utf-8")

    rep = run_due_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        outdir=outdir,
    )
    assert rep["lock_acquired"] is False
    assert rep["status"] == "skipped_locked"
    assert rep["json_report_path"] is None
    assert rep["md_report_path"] is None
    assert lock_path.exists()
    assert list((outdir / "local-user").glob("*.json")) == []


def test_cli_run_due_returns_non_zero_when_locked(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"
    _write(jobs_jsonl, _rows())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)
    create_saved_search(
        db_path=saved_db,
        name="daily se",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
    )

    lock_path = outdir / "local-user" / ".run_due.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text('{"pid":123}', encoding="utf-8")

    rc = _cmd_alerts_run_due(
        argparse.Namespace(
            saved_db=str(saved_db),
            input=str(jobs_jsonl),
            sqlite=str(jobs_db),
            outdir=str(outdir),
            scan_limit=5000,
            limit=200,
            sample_size=5,
            user_id="local-user",
            user_email="local@example.com",
            send_digest_email=False,
            email_to=None,
        )
    )
    assert rc == 2
