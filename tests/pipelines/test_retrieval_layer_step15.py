from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.retrieval import QueryParams, run_retrieval_query


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://e/3",
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
            "url": "https://e/1",
            "normalized_title": "other",
            "role_family": "other",
            "language_bucket": "en",
            "location_type": "onsite",
            "employment_type": "contract",
            "has_salary": False,
            "has_skills": False,
            "title_is_other": True,
            "skills": [],
            "salary_currency": None,
            "published_at": "2026-03-08T10:00:00+00:00",
            "updated_at": "2026-03-09T10:00:00+00:00",
        },
        {
            "url": "https://e/2",
            "normalized_title": "marketing_specialist",
            "role_family": "marketing",
            "language_bucket": "en",
            "location_type": "hybrid",
            "employment_type": "full_time",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": False,
            "skills": ["seo", "python"],
            "salary_currency": "EUR",
            "published_at": "2026-03-09T10:00:00+00:00",
            "updated_at": "2026-03-13T10:00:00+00:00",
        },
    ]


def test_filter_by_normalized_title(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    rep = run_retrieval_query(input_path=p, query=QueryParams(normalized_title="data_engineer"))
    assert rep["matched_rows"] == 1
    assert rep["results"][0]["url"] == "https://e/3"


def test_filter_by_role_family_and_flags(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    rep = run_retrieval_query(
        input_path=p,
        query=QueryParams(role_family="other", has_salary=False, title_is_other=True),
    )
    assert rep["matched_rows"] == 1
    assert rep["results"][0]["url"] == "https://e/1"


def test_filter_by_skills_contains(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    rep = run_retrieval_query(input_path=p, query=QueryParams(skills_contains=["python"]))
    urls = [r["url"] for r in rep["results"]]
    assert urls == ["https://e/3", "https://e/2"]


def test_sorting_updated_desc_and_fallback_url(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    rep = run_retrieval_query(input_path=p, query=QueryParams(sort_by="updated_at_desc"))
    urls = [r["url"] for r in rep["results"]]
    assert urls == ["https://e/2", "https://e/3", "https://e/1"]
