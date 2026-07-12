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
            "url": "https://e/1",
            "title_raw": "Senior Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
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
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "location_type": "hybrid",
            "employment_type": "full_time",
            "has_salary": False,
            "has_skills": False,
            "title_is_other": False,
            "skills": [],
            "salary_currency": None,
            "published_at": "2026-03-09T10:00:00+00:00",
            "updated_at": "2026-03-10T10:00:00+00:00",
        },
    ]


def test_saved_searches_create_list_enable_disable(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "saved.db"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p, saved_db_path=db, job_state_db_path=tmp_path / "job_state.db"))

    r_create = client.post(
        "/saved-searches",
        json={
            "name": "python tech",
            "query_type": "filters",
            "filters_json": "{\"skills_contains\": [\"python\"], \"title_is_other\": false}",
            "is_enabled": True,
        },
    )
    assert r_create.status_code == 200
    created = r_create.json()["saved_search"]
    sid = created["search_id"]
    assert created["is_enabled"] is True
    assert created["frequency"] == "daily"

    r_list = client.get("/saved-searches")
    assert r_list.status_code == 200
    assert len(r_list.json()["saved_searches"]) == 1

    r_disable = client.post(f"/saved-searches/{sid}/disable")
    assert r_disable.status_code == 200
    assert r_disable.json()["saved_search"]["is_enabled"] is False

    r_enable = client.post(f"/saved-searches/{sid}/enable")
    assert r_enable.status_code == 200
    assert r_enable.json()["saved_search"]["is_enabled"] is True


def test_saved_searches_run_and_check_new(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "saved.db"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p, saved_db_path=db, job_state_db_path=tmp_path / "job_state.db"))

    r_create = client.post(
        "/saved-searches",
        json={
            "name": "python tech",
            "query_type": "filters",
            "filters_json": "{\"skills_contains\": [\"python\"], \"title_is_other\": false}",
            "frequency": "twice_daily",
        },
    )
    sid = r_create.json()["saved_search"]["search_id"]

    r_run = client.post(f"/saved-searches/{sid}/run", params={"limit": 20, "offset": 0})
    assert r_run.status_code == 200
    run_payload = r_run.json()
    assert run_payload["saved_search"]["search_id"] == sid
    assert run_payload["saved_search"]["frequency"] == "twice_daily"
    assert run_payload["run_result"]["total_count"] == 1

    r_check_1 = client.post(f"/saved-searches/{sid}/check-new", params={"scan_limit": 100, "limit": 20})
    assert r_check_1.status_code == 200
    assert r_check_1.json()["new_count"] == 1

    r_check_2 = client.post(f"/saved-searches/{sid}/check-new", params={"scan_limit": 100, "limit": 20})
    assert r_check_2.status_code == 200
    assert r_check_2.json()["new_count"] == 0


def test_saved_searches_results_endpoint_current_and_new_modes(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "saved.db"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p, saved_db_path=db, job_state_db_path=tmp_path / "job_state.db"))

    r_create = client.post(
        "/saved-searches",
        json={
            "name": "python tech",
            "query_type": "filters",
            "filters_json": "{\"skills_contains\": [\"python\"], \"title_is_other\": false}",
        },
    )
    sid = r_create.json()["saved_search"]["search_id"]

    r_current = client.get(f"/saved-searches/{sid}/results", params={"mode": "current", "limit": 20, "offset": 0})
    assert r_current.status_code == 200
    payload = r_current.json()
    assert payload["mode"] == "current"
    assert payload["current_count"] == 1
    assert payload["returned_count"] == 1
    assert payload["results"][0]["job_state"] == "new"

    r_new = client.get(f"/saved-searches/{sid}/results", params={"mode": "new", "scan_limit": 100})
    assert r_new.status_code == 200
    assert r_new.json()["mode"] == "new_only"
    assert r_new.json()["new_count"] == 1

    # Mark as seen in saved_search_seen via check-new, then new mode should be zero.
    client.post(f"/saved-searches/{sid}/check-new", params={"scan_limit": 100, "limit": 20})
    r_new_after = client.get(f"/saved-searches/{sid}/results", params={"mode": "new", "scan_limit": 100})
    assert r_new_after.status_code == 200
    assert r_new_after.json()["new_count"] == 0


def test_saved_searches_not_found_404(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "saved.db"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p, saved_db_path=db, job_state_db_path=tmp_path / "job_state.db"))

    r = client.post("/saved-searches/not-found/run")
    assert r.status_code == 404
    assert "saved search not found" in r.json()["detail"]


def test_saved_searches_are_isolated_by_current_user_header(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "saved.db"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p, saved_db_path=db, job_state_db_path=tmp_path / "job_state.db"))

    r_create_a = client.post(
        "/saved-searches",
        json={
            "name": "user-a search",
            "query_type": "filters",
            "filters_json": "{\"normalized_title\":\"software_engineer\"}",
        },
    )
    assert r_create_a.status_code == 200
    sid_a = r_create_a.json()["saved_search"]["search_id"]

    r_list_a = client.get("/saved-searches")
    assert r_list_a.status_code == 200
    assert len(r_list_a.json()["saved_searches"]) == 1

    headers_b = {"X-JobIntel-User-Id": "user-b", "X-JobIntel-User-Email": "b@example.com"}
    r_list_b_0 = client.get("/saved-searches", headers=headers_b)
    assert r_list_b_0.status_code == 200
    assert r_list_b_0.json()["saved_searches"] == []

    r_create_b = client.post(
        "/saved-searches",
        headers=headers_b,
        json={
            "name": "user-b search",
            "query_type": "filters",
            "filters_json": "{\"normalized_title\":\"account_executive\"}",
        },
    )
    assert r_create_b.status_code == 200

    r_list_b = client.get("/saved-searches", headers=headers_b)
    assert r_list_b.status_code == 200
    assert len(r_list_b.json()["saved_searches"]) == 1
    assert r_list_b.json()["saved_searches"][0]["name"] == "user-b search"

    # user-b cannot run user-a saved search
    r_cross = client.post(f"/saved-searches/{sid_a}/run", headers=headers_b)
    assert r_cross.status_code == 404


def test_saved_searches_respect_default_current_user_config(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "saved.db"
    _write(p, _rows())
    client_a = TestClient(create_app(input_path=p, saved_db_path=db, default_user_id="alpha", default_user_email="a@example.com"))
    client_b = TestClient(create_app(input_path=p, saved_db_path=db, default_user_id="beta", default_user_email="b@example.com"))

    r_create = client_a.post(
        "/saved-searches",
        json={
            "name": "alpha-search",
            "query_type": "filters",
            "filters_json": "{\"normalized_title\":\"software_engineer\"}",
        },
    )
    assert r_create.status_code == 200

    r_list_a = client_a.get("/saved-searches")
    assert r_list_a.status_code == 200
    assert len(r_list_a.json()["saved_searches"]) == 1

    r_list_b = client_b.get("/saved-searches")
    assert r_list_b.status_code == 200
    assert r_list_b.json()["saved_searches"] == []


def test_saved_searches_payload_invalid_422(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "saved.db"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p, saved_db_path=db, job_state_db_path=tmp_path / "job_state.db"))

    r = client.post(
        "/saved-searches",
        json={
            "name": "bad pack",
            "query_type": "pack",
            "is_enabled": True,
        },
    )
    assert r.status_code == 422
    assert "pack_name is required for query_type=pack" in r.json()["detail"]


def test_saved_searches_update_and_delete(tmp_path: Path) -> None:
    p = tmp_path / "idx.jsonl"
    db = tmp_path / "saved.db"
    _write(p, _rows())
    client = TestClient(create_app(input_path=p, saved_db_path=db, job_state_db_path=tmp_path / "job_state.db"))

    r_create = client.post(
        "/saved-searches",
        json={
            "name": "python tech",
            "query_type": "filters",
            "filters_json": "{\"skills_contains\": [\"python\"], \"title_is_other\": false}",
        },
    )
    sid = r_create.json()["saved_search"]["search_id"]

    r_upd = client.post(
        f"/saved-searches/{sid}/update",
        json={
            "name": "ae pack",
            "query_type": "pack",
            "pack_name": "account_executive_jobs",
            "frequency": "manual",
            "is_enabled": False,
        },
    )
    assert r_upd.status_code == 200
    saved = r_upd.json()["saved_search"]
    assert saved["name"] == "ae pack"
    assert saved["query_type"] == "pack"
    assert saved["frequency"] == "manual"
    assert saved["is_enabled"] is False

    r_del = client.post(f"/saved-searches/{sid}/delete")
    assert r_del.status_code == 200
    assert r_del.json()["deleted"] is True

    r_list = client.get("/saved-searches")
    assert r_list.status_code == 200
    assert r_list.json()["saved_searches"] == []
