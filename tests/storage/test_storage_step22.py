from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.retrieval import QueryParams
from jobintel_next.storage import (
    build_sqlite_index,
    sqlite_count_jobs,
    sqlite_count_pack,
    sqlite_list_jobs,
    sqlite_run_pack,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://e/3",
            "source": "greenhouse",
            "source_org": "x",
            "title_raw": "Account Executive",
            "title_clean": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "employment_type": "full_time",
            "location_type": "remote",
            "has_salary": 0,
            "has_skills": 0,
            "title_is_other": 0,
            "salary_currency": None,
            "published_at": "2026-03-10T10:00:00+00:00",
            "updated_at": "2026-03-10T10:00:00+00:00",
            "skills": [],
        },
        {
            "url": "https://e/2",
            "source": "greenhouse",
            "source_org": "x",
            "title_raw": "Senior Software Engineer",
            "title_clean": "Senior Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "employment_type": "full_time",
            "location_type": "hybrid",
            "has_salary": 1,
            "has_skills": 1,
            "title_is_other": 0,
            "salary_currency": "USD",
            "published_at": "2026-03-09T10:00:00+00:00",
            "updated_at": "2026-03-11T10:00:00+00:00",
            "skills": ["python", "sql"],
        },
        {
            "url": "https://e/1",
            "source": "greenhouse",
            "source_org": "x",
            "title_raw": "General Role",
            "title_clean": "General Role",
            "normalized_title": "other",
            "role_family": "other",
            "language_bucket": "en",
            "employment_type": "contract",
            "location_type": "onsite",
            "has_salary": 1,
            "has_skills": 1,
            "title_is_other": 1,
            "salary_currency": "EUR",
            "published_at": "2026-03-08T10:00:00+00:00",
            "updated_at": "2026-03-12T10:00:00+00:00",
            "skills": ["python"],
        },
    ]


def test_build_sqlite_index_and_basic_queries(tmp_path: Path) -> None:
    inp = tmp_path / "indexed.jsonl"
    db = tmp_path / "jobs.db"
    _write_jsonl(inp, _rows())

    rep = build_sqlite_index(input_path=inp, sqlite_path=db)
    assert rep["rows_total"] == 3
    assert rep["inserted_rows"] == 3

    list_rep = sqlite_list_jobs(
        sqlite_path=db,
        query=QueryParams(has_skills=True, sort_by="updated_at_desc"),
        limit=1,
        offset=0,
    )
    assert list_rep["total_count"] == 2
    assert list_rep["returned_count"] == 1
    assert list_rep["results"][0]["url"] == "https://e/1"

    count_rep = sqlite_count_jobs(sqlite_path=db, query=QueryParams(normalized_title="software_engineer"))
    assert count_rep["count"] == 1


def test_pack_query_and_count_on_sqlite(tmp_path: Path) -> None:
    inp = tmp_path / "indexed.jsonl"
    db = tmp_path / "jobs.db"
    _write_jsonl(inp, _rows())
    build_sqlite_index(input_path=inp, sqlite_path=db)

    rep = sqlite_run_pack(sqlite_path=db, pack_name="account_executive_jobs", limit=10, offset=0)
    assert rep["total_count"] == 1
    assert rep["returned_count"] == 1
    assert rep["results"][0]["url"] == "https://e/3"

    cnt = sqlite_count_pack(sqlite_path=db, pack_name="account_executive_jobs")
    assert cnt["count"] == 1
