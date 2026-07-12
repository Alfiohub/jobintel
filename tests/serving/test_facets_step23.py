from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.retrieval import QueryParams
from jobintel_next.serving import get_facets
from jobintel_next.storage import build_sqlite_index


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://e/1",
            "role_family": "sales",
            "normalized_title": "account_executive",
            "location_type": "remote",
            "employment_type": "full_time",
            "language_bucket": "en",
            "has_salary": False,
            "has_skills": False,
            "title_is_other": False,
            "salary_currency": None,
        },
        {
            "url": "https://e/2",
            "role_family": "software_engineering",
            "normalized_title": "software_engineer",
            "location_type": "hybrid",
            "employment_type": "full_time",
            "language_bucket": "en",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": False,
            "salary_currency": "USD",
        },
        {
            "url": "https://e/3",
            "role_family": "other",
            "normalized_title": "other",
            "location_type": "onsite",
            "employment_type": "contract",
            "language_bucket": "en",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": True,
            "salary_currency": "EUR",
            "skills": ["python"],
        },
    ]


def test_global_facets_sqlite(tmp_path: Path) -> None:
    inp = tmp_path / "jobs.jsonl"
    db = tmp_path / "jobs.db"
    _write(inp, _rows())
    build_sqlite_index(input_path=inp, sqlite_path=db)

    rep = get_facets(input_path=inp, sqlite_path=db, query=QueryParams())
    assert rep["backend"] == "sqlite"
    assert rep["total_count"] == 3
    role_total = sum(x["count"] for x in rep["facets"]["role_family"])
    assert role_total == rep["total_count"]


def test_subset_facets_sqlite_coherence(tmp_path: Path) -> None:
    inp = tmp_path / "jobs.jsonl"
    db = tmp_path / "jobs.db"
    _write(inp, _rows())
    build_sqlite_index(input_path=inp, sqlite_path=db)

    rep = get_facets(
        input_path=inp,
        sqlite_path=db,
        query=QueryParams(has_salary=True),
    )
    assert rep["total_count"] == 2
    buckets = {b["value"]: b["count"] for b in rep["facets"]["has_salary"]}
    assert buckets == {True: 2}
