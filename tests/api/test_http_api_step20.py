from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jobintel_next.app.api import create_app
from jobintel_next.storage import build_sqlite_index


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://e/3",
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "location_type": "remote",
            "employment_type": "full_time",
            "has_salary": False,
            "has_skills": False,
            "title_is_other": False,
            "skills": [],
            "salary_currency": None,
            "published_at": "2026-03-10T10:00:00+00:00",
            "updated_at": "2026-03-12T10:00:00+00:00",
        },
        {
            "url": "https://e/2",
            "title_raw": "Senior Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "location_type": "hybrid",
            "employment_type": "full_time",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": False,
            "skills": ["python", "sql"],
            "salary_currency": "USD",
            "published_at": "2026-03-09T10:00:00+00:00",
            "updated_at": "2026-03-13T10:00:00+00:00",
        },
        {
            "url": "https://e/1",
            "title_raw": "General Role",
            "normalized_title": "other",
            "role_family": "other",
            "language_bucket": "en",
            "location_type": "onsite",
            "employment_type": "contract",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": True,
            "skills": ["python"],
            "salary_currency": "EUR",
            "published_at": "2026-03-08T10:00:00+00:00",
            "updated_at": "2026-03-09T10:00:00+00:00",
        },
        {
            "url": "https://e/4",
            "title_raw": "Data Engineer",
            "normalized_title": "data_engineer",
            "role_family": "data_engineering",
            "language_bucket": "en",
            "location_type": "remote",
            "employment_type": "full_time",
            "has_salary": False,
            "has_skills": True,
            "title_is_other": False,
            "skills": ["python", "sql"],
            "salary_currency": None,
            "published_at": "2026-03-11T10:00:00+00:00",
            "updated_at": "2026-03-11T10:00:00+00:00",
        },
    ]


def test_health_endpoint(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p))
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "dataset_path": str(p)}


def test_jobs_list_with_filters_and_pagination(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p))
    r = client.get(
        "/jobs",
        params={
            "has_skills": "true",
            "sort_by": "updated_at_desc",
            "limit": 1,
            "offset": 1,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total_count"] == 3
    assert data["returned_count"] == 1
    assert data["results"][0]["url"] == "https://e/4"


def test_jobs_count(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p))
    r = client.get("/jobs/count", params={"normalized_title": "software_engineer"})
    assert r.status_code == 200
    assert r.json()["count"] == 1


def test_packs_list_and_pack_run(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p))

    r1 = client.get("/packs")
    assert r1.status_code == 200
    names = {x["name"] for x in r1.json()["packs"]}
    assert "account_executive_jobs" in names

    r2 = client.get("/packs/account_executive_jobs", params={"limit": 10, "offset": 0})
    assert r2.status_code == 200
    data = r2.json()
    assert data["total_count"] == 1
    assert data["returned_count"] == 1
    assert data["results"][0]["url"] == "https://e/3"


def test_pack_pagination_and_count(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p))

    r1 = client.get("/packs/python_tech_jobs", params={"limit": 1, "offset": 1})
    assert r1.status_code == 200
    assert r1.json()["returned_count"] == 1

    r2 = client.get("/packs/python_tech_jobs/count")
    assert r2.status_code == 200
    assert r2.json()["count"] == 2


def test_invalid_limit_validation_422(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p))
    r = client.get("/jobs", params={"limit": -1})
    assert r.status_code == 422


def test_pack_not_found_404(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p))
    r = client.get("/packs/not_a_real_pack")
    assert r.status_code == 404
    assert "unknown query pack" in r.json()["detail"]


def test_startup_config_dataset_path_from_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "idx.jsonl"
    _write(p, _rows())
    monkeypatch.setenv("JOBINTEL_INDEXED_INPUT", str(p))
    client = TestClient(create_app())
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["dataset_path"] == str(p)


def test_startup_invalid_dataset_path_raises(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    with pytest.raises(RuntimeError):
        with TestClient(create_app(input_path=missing)) as _client:
            pass


def test_facets_endpoint_with_sqlite_subset(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "idx.db"
    _write(p, _rows())
    build_sqlite_index(input_path=p, sqlite_path=db)
    client = TestClient(create_app(input_path=p, sqlite_path=db))

    r = client.get("/facets", params={"has_salary": "true"})
    assert r.status_code == 200
    data = r.json()
    assert data["backend"] == "sqlite"
    assert data["total_count"] == 2
    assert "role_family" in data["facets"]
    has_salary_buckets = {x["value"]: x["count"] for x in data["facets"]["has_salary"]}
    assert has_salary_buckets == {True: 2}
