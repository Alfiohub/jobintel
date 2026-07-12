from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.product.saved_searches import create_saved_search, run_enabled_saved_searches
from jobintel_next.storage import build_sqlite_index


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows_v1() -> list[dict]:
    return [
        {
            "url": "https://e/1",
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "published_at": "2026-03-10T00:00:00+00:00",
        },
        {
            "url": "https://e/2",
            "title_raw": "Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "skills": ["python"],
            "has_skills": True,
            "published_at": "2026-03-11T00:00:00+00:00",
        },
    ]


def _rows_v2() -> list[dict]:
    return [
        *_rows_v1(),
        {
            "url": "https://e/3",
            "title_raw": "Senior Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "skills": ["python"],
            "has_skills": True,
            "published_at": "2026-03-12T00:00:00+00:00",
        },
    ]


def test_runner_enabled_only_and_artifacts(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"

    _write(jobs_jsonl, _rows_v1())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    create_saved_search(
        db_path=saved_db,
        name="AE pack",
        query_type="pack",
        pack_name="account_executive_jobs",
    )
    create_saved_search(
        db_path=saved_db,
        name="SE filters",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    create_saved_search(
        db_path=saved_db,
        name="Disabled one",
        query_type="filters",
        filters_json='{"role_family":"marketing"}',
        is_enabled=False,
    )

    rep = run_enabled_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        outdir=outdir,
        scan_limit=1000,
        return_limit=100,
        sample_size=3,
    )
    assert rep["searches_total"] == 3
    assert rep["searches_enabled"] == 2
    assert rep["searches_disabled"] == 1
    assert rep["processed_ok"] == 2
    assert Path(rep["json_report_path"]).exists()
    assert Path(rep["md_report_path"]).exists()


def test_runner_new_matches_delta_coherent(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"

    _write(jobs_jsonl, _rows_v1())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)
    create_saved_search(
        db_path=saved_db,
        name="SE filters",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )

    first = run_enabled_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        outdir=outdir,
    )
    assert first["total_new_matches"] == 1

    second = run_enabled_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        outdir=outdir,
    )
    assert second["total_new_matches"] == 0

    _write(jobs_jsonl, _rows_v2())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)
    third = run_enabled_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        outdir=outdir,
    )
    assert third["total_new_matches"] == 1
