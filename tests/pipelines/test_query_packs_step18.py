from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.retrieval.query_packs import (
    build_query_packs_report,
    get_query_packs,
    run_query_pack,
)


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://e/1",
            "title_raw": "Data Engineer",
            "normalized_title": "data_engineer",
            "role_family": "data_engineering",
            "language_bucket": "en",
            "location_type": "remote",
            "employment_type": "full_time",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": False,
            "skills": ["python", "sql"],
            "salary_currency": "USD",
            "published_at": "2026-03-10T10:00:00+00:00",
            "updated_at": "2026-03-12T10:00:00+00:00",
        },
        {
            "url": "https://e/2",
            "title_raw": "Marketing Manager",
            "normalized_title": "marketing_specialist",
            "role_family": "marketing",
            "language_bucket": "en",
            "location_type": "hybrid",
            "employment_type": "full_time",
            "has_salary": True,
            "has_skills": False,
            "title_is_other": False,
            "skills": [],
            "salary_currency": "USD",
            "published_at": "2026-03-09T10:00:00+00:00",
            "updated_at": "2026-03-13T10:00:00+00:00",
        },
        {
            "url": "https://e/3",
            "title_raw": "Generalist role",
            "normalized_title": "other",
            "role_family": "other",
            "language_bucket": "en",
            "location_type": "remote",
            "employment_type": "contract",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": True,
            "skills": ["python"],
            "salary_currency": "USD",
            "published_at": "2026-03-08T10:00:00+00:00",
            "updated_at": "2026-03-08T10:00:00+00:00",
        },
    ]


def test_query_pack_names_include_expected() -> None:
    names = set(get_query_packs().keys())
    assert "python_tech_jobs" in names
    assert "remote_data_jobs" in names
    assert "other_with_strong_signals" in names


def test_run_query_pack_python_tech_jobs_filters_out_other(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    rep = run_query_pack(input_path=p, pack_name="python_tech_jobs")
    assert rep["matched_rows"] == 1
    assert rep["results"][0]["url"] == "https://e/1"


def test_build_query_packs_report_writes_files(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    d = tmp_path / "docs"
    _write(p, _rows())
    rep = build_query_packs_report(input_path=p, report_dir=d, sample_limit=3)
    assert "packs" in rep
    assert (d / "query_packs_step18.json").exists()
    assert (d / "query_packs_step18.md").exists()
