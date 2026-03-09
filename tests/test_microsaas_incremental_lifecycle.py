from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from automation.microsaas import run_microsaas_pipeline as pipeline


def _write_input(path: Path, row: dict) -> None:
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")


def _run_pipeline(monkeypatch, *, input_path: Path, out_dir: Path, db_path: Path) -> None:
    argv = [
        "run_microsaas_pipeline.py",
        "--input",
        str(input_path),
        "--output-dir",
        str(out_dir),
        "--db",
        str(db_path),
        "--embedding-mode",
        "hash",
        "--max-rows",
        "10",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    pipeline.main()


def test_incremental_lifecycle_and_pipeline_runs(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "jobintel_microsaas.sqlite"
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    out3 = tmp_path / "run3"
    inp = tmp_path / "input.jsonl"

    base_row = {
        "source": "greenhouse",
        "external_id": "ext-1",
        "source_job_id": "ext-1",
        "source_org": "acme",
        "url": "https://example.com/jobs/1",
        "title": "Data Engineer",
        "company_name": "Acme",
        "location_raw": "Berlin, DE",
        "description_text": "Need 3+ years of experience. Bachelor's degree required. Python SQL.",
        "language": "en",
    }

    _write_input(inp, base_row)
    _run_pipeline(monkeypatch, input_path=inp, out_dir=out1, db_path=db_path)
    report1 = json.loads((out1 / "pipeline_report.json").read_text(encoding="utf-8"))
    assert report1["new"] == 1
    assert report1["processed"] == 1
    assert report1["skipped"] == 0
    assert report1["updated"] == 0
    assert report1["failed"] == 0

    _write_input(inp, base_row)
    _run_pipeline(monkeypatch, input_path=inp, out_dir=out2, db_path=db_path)
    report2 = json.loads((out2 / "pipeline_report.json").read_text(encoding="utf-8"))
    assert report2["new"] == 0
    assert report2["processed"] == 0
    assert report2["skipped"] == 1
    assert report2["updated"] == 0
    assert report2["failed"] == 0

    changed_row = dict(base_row)
    changed_row["description_text"] = (
        "Need 5+ years of experience. Master's degree preferred. Python SQL and Airflow."
    )
    _write_input(inp, changed_row)
    _run_pipeline(monkeypatch, input_path=inp, out_dir=out3, db_path=db_path)
    report3 = json.loads((out3 / "pipeline_report.json").read_text(encoding="utf-8"))
    assert report3["new"] == 0
    assert report3["processed"] == 0
    assert report3["skipped"] == 0
    assert report3["updated"] == 1
    assert report3["failed"] == 0

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    runs = con.execute(
        "SELECT processed, skipped, updated, failed FROM pipeline_runs ORDER BY id"
    ).fetchall()
    assert len(runs) == 3
    assert (runs[0]["processed"], runs[0]["skipped"], runs[0]["updated"], runs[0]["failed"]) == (
        1,
        0,
        0,
        0,
    )
    assert (runs[1]["processed"], runs[1]["skipped"], runs[1]["updated"], runs[1]["failed"]) == (
        0,
        1,
        0,
        0,
    )
    assert (runs[2]["processed"], runs[2]["skipped"], runs[2]["updated"], runs[2]["failed"]) == (
        0,
        0,
        1,
        0,
    )

    row = con.execute(
        "SELECT processing_state, first_seen_at, last_seen_at FROM jobs_indexed LIMIT 1"
    ).fetchone()
    assert row is not None
    assert row["processing_state"] == "updated"
    assert row["first_seen_at"]
    assert row["last_seen_at"]
    con.close()

