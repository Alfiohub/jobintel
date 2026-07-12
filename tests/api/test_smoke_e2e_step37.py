from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jobintel_next.app.api import create_app


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://smoke/1",
            "title_raw": "Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "location_type": "remote",
            "employment_type": "full_time",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": False,
            "skills": ["python", "sql"],
            "salary_currency": "EUR",
            "published_at": "2026-03-10T10:00:00+00:00",
            "updated_at": "2026-03-11T10:00:00+00:00",
        },
        {
            "url": "https://smoke/2",
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "location_type": "onsite",
            "employment_type": "full_time",
            "has_salary": False,
            "has_skills": False,
            "title_is_other": False,
            "skills": [],
            "salary_currency": None,
            "published_at": "2026-03-09T10:00:00+00:00",
            "updated_at": "2026-03-09T10:00:00+00:00",
        },
    ]


def test_smoke_e2e_step37(tmp_path: Path) -> None:
    indexed = tmp_path / "jobs_indexed.jsonl"
    saved_db = tmp_path / "saved.db"
    runs_dir = tmp_path / "alerts" / "runs"
    _write(indexed, _rows())

    client = TestClient(create_app(input_path=indexed, saved_db_path=saved_db, alert_runs_dir=runs_dir))

    r_login = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123", "next": "/admin"},
        follow_redirects=False,
    )
    assert r_login.status_code == 303

    # startup app + health
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    # render admin overview
    r_admin = client.get("/admin")
    assert r_admin.status_code == 200
    assert "Admin Overview" in r_admin.text

    # create saved search
    r_create = client.post(
        "/saved-searches",
        json={
            "name": "smoke software",
            "query_type": "filters",
            "filters_json": '{"normalized_title":"software_engineer"}',
            "is_enabled": True,
        },
    )
    assert r_create.status_code == 200
    sid = r_create.json()["saved_search"]["search_id"]

    # run-all alerts
    r_run_all = client.post("/alerts/run-all")
    assert r_run_all.status_code == 200
    run_id = r_run_all.json()["run_id"]
    assert r_run_all.json()["searches_enabled"] >= 1

    # list runs
    r_runs = client.get("/alerts/runs")
    assert r_runs.status_code == 200
    runs = r_runs.json()["runs"]
    assert any(x["run_id"] == run_id for x in runs)

    # run detail
    r_detail = client.get(f"/alerts/runs/{run_id}")
    assert r_detail.status_code == 200
    detail = r_detail.json()
    assert detail["run_id"] == run_id
    assert len(detail["results"]) >= 1
    assert any(x.get("search_id") == sid for x in detail["results"])
