from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jobintel_next.app.api import create_app


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
            "has_skills": True,
            "skills": ["python"],
        }
    ]


def _client(tmp_path: Path) -> TestClient:
    idx = tmp_path / "idx.jsonl"
    saved = tmp_path / "saved.db"
    runs = tmp_path / "alerts" / "runs"
    _write(idx, _rows())
    client = TestClient(create_app(input_path=idx, saved_db_path=saved, alert_runs_dir=runs))
    login = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123", "next": "/admin"},
        follow_redirects=False,
    )
    assert login.status_code == 303
    return client


def test_pilot_flow_smoke_and_dashboard_diagnostics(tmp_path: Path) -> None:
    client = _client(tmp_path)

    # First run dashboard should show diagnostics and onboarding guidance.
    r0 = client.get("/admin")
    assert r0.status_code == 200
    assert "Diagnostics" in r0.text
    assert "Current user:" in r0.text
    assert "Default alert email:" in r0.text
    assert "not configured" in r0.text
    assert "Latest run status:" in r0.text

    # Create first saved search.
    r1 = client.post(
        "/admin/saved-searches/new",
        data={
            "name": "pilot se",
            "query_type": "filters",
            "filters_json": '{"normalized_title":"software_engineer"}',
            "frequency": "daily",
            "is_enabled": "on",
        },
        follow_redirects=True,
    )
    assert r1.status_code == 200
    assert "Saved search created" in r1.text

    # Run alerts and open inbox.
    r2 = client.post("/admin/alerts/run-all", follow_redirects=True)
    assert r2.status_code == 200
    assert "Alert Run" in r2.text

    r3 = client.get("/admin/inbox?state=new")
    assert r3.status_code == 200
    assert "Job Inbox" in r3.text

    # Mark one job to complete inbox triage signal.
    r4 = client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "seen", "next": "/admin/inbox?state=seen"},
        follow_redirects=True,
    )
    assert r4.status_code == 200
    assert "Job state updated: seen" in r4.text

    # Configure account default alert email.
    r5 = client.post(
        "/admin/account",
        data={
            "email": "admin@example.com",
            "default_alert_email": "alerts@example.com",
            "include_dismissed_default": "on",
        },
        follow_redirects=True,
    )
    assert r5.status_code == 200
    assert "Account settings updated" in r5.text

    # Diagnostics should now show configured email and 4/4 checklist.
    r6 = client.get("/admin")
    assert r6.status_code == 200
    assert "configured" in r6.text
    assert "alerts@example.com" in r6.text
    assert "Checklist progress:" in r6.text
    assert "4/4" in r6.text


def test_login_invalid_message_is_clear(tmp_path: Path) -> None:
    idx = tmp_path / "idx.jsonl"
    saved = tmp_path / "saved.db"
    _write(idx, _rows())
    client = TestClient(create_app(input_path=idx, saved_db_path=saved))

    bad = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "wrong", "next": "/admin"},
        follow_redirects=True,
    )
    assert bad.status_code == 200
    assert "Login failed: invalid email or password" in bad.text
