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
            "title_raw": "Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "published_at": "2026-03-10T00:00:00+00:00",
        },
        {
            "url": "https://e/2",
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "published_at": "2026-03-11T00:00:00+00:00",
        },
    ]


def test_job_state_api_set_get_clear(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    state_db = tmp_path / "job_state.db"
    _write(indexed, _rows())

    client = TestClient(create_app(input_path=indexed, saved_db_path=saved_db, job_state_db_path=state_db))

    r0 = client.get("/jobs/state", params={"job_url": "https://e/1"})
    assert r0.status_code == 200
    assert r0.json()["state"] == "new"

    r1 = client.post("/jobs/state", json={"job_url": "https://e/1", "state": "saved"})
    assert r1.status_code == 200
    assert r1.json()["state"] == "saved"

    r_jobs = client.get("/jobs", params={"normalized_title": "software_engineer"})
    assert r_jobs.status_code == 200
    assert r_jobs.json()["results"][0]["job_state"] == "saved"

    r_jobs_saved = client.get("/jobs", params={"job_state": "saved"})
    assert r_jobs_saved.status_code == 200
    assert r_jobs_saved.json()["total_count"] == 1
    assert r_jobs_saved.json()["results"][0]["url"] == "https://e/1"

    r_jobs_new = client.get("/jobs", params={"job_state": "new"})
    assert r_jobs_new.status_code == 200
    assert r_jobs_new.json()["total_count"] == 1
    assert r_jobs_new.json()["results"][0]["url"] == "https://e/2"

    r_count_saved = client.get("/jobs/count", params={"job_state": "saved"})
    assert r_count_saved.status_code == 200
    assert r_count_saved.json()["count"] == 1

    r_pack = client.get("/packs/account_executive_jobs")
    assert r_pack.status_code == 200
    assert r_pack.json()["results"][0]["job_state"] == "new"

    r_set_dismissed = client.post("/jobs/state", json={"job_url": "https://e/2", "state": "dismissed"})
    assert r_set_dismissed.status_code == 200

    r_without_dismissed = client.get("/jobs", params={"include_dismissed": "false"})
    assert r_without_dismissed.status_code == 200
    assert r_without_dismissed.json()["total_count"] == 1
    assert all(x["job_state"] != "dismissed" for x in r_without_dismissed.json()["results"])

    r_only_dismissed = client.get("/jobs", params={"job_state": "dismissed"})
    assert r_only_dismissed.status_code == 200
    assert r_only_dismissed.json()["total_count"] == 1
    assert r_only_dismissed.json()["results"][0]["url"] == "https://e/2"

    r2 = client.get("/jobs/state", params={"job_url": "https://e/1"})
    assert r2.status_code == 200
    assert r2.json()["state"] == "saved"

    r3 = client.post("/jobs/state/clear", params={"job_url": "https://e/1"})
    assert r3.status_code == 200
    assert r3.json()["deleted"] is True

    r4 = client.get("/jobs/state", params={"job_url": "https://e/1"})
    assert r4.status_code == 200
    assert r4.json()["state"] == "new"


def test_job_state_api_validation_422(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    _write(indexed, _rows())

    client = TestClient(create_app(input_path=indexed))

    r = client.post("/jobs/state", json={"job_url": "https://e/1", "state": "archived"})
    assert r.status_code == 422

    r2 = client.get("/jobs", params={"job_state": "archived"})
    assert r2.status_code == 422


def test_job_state_is_isolated_by_current_user_header(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    _write(indexed, _rows())
    client = TestClient(create_app(input_path=indexed))

    user_a = {"X-JobIntel-User-Id": "user-a", "X-JobIntel-User-Email": "a@example.com"}
    user_b = {"X-JobIntel-User-Id": "user-b", "X-JobIntel-User-Email": "b@example.com"}

    r_set_a = client.post("/jobs/state", headers=user_a, json={"job_url": "https://e/1", "state": "saved"})
    assert r_set_a.status_code == 200

    r_get_a = client.get("/jobs/state", headers=user_a, params={"job_url": "https://e/1"})
    assert r_get_a.status_code == 200
    assert r_get_a.json()["state"] == "saved"

    r_get_b = client.get("/jobs/state", headers=user_b, params={"job_url": "https://e/1"})
    assert r_get_b.status_code == 200
    assert r_get_b.json()["state"] == "new"
