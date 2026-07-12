from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jobintel_next.app.api import create_app
from jobintel_next.product.auth import update_user_settings
from jobintel_next.product.saved_searches import create_saved_search


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
            "has_skills": True,
            "skills": ["python"],
        }
    ]


def _client_with_one_saved_search(tmp_path: Path) -> TestClient:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    runs_dir = tmp_path / "alerts" / "runs"
    _write(indexed, _rows())
    create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    return TestClient(create_app(input_path=indexed, saved_db_path=saved_db, alert_runs_dir=runs_dir))


def test_run_all_send_email_false(tmp_path: Path) -> None:
    client = _client_with_one_saved_search(tmp_path)
    r = client.post("/alerts/run-all", params={"send_email": "false"})
    assert r.status_code == 200
    data = r.json()
    assert data["processed_ok"] == 1
    assert data["email_delivery"] is None


def test_run_all_send_email_true_with_mock_sender(monkeypatch, tmp_path: Path) -> None:
    client = _client_with_one_saved_search(tmp_path)
    monkeypatch.setenv("JOBINTEL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_FROM", "from@example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_PORT", "587")

    def _fake_send_email_alerts_from_run(*, run_json_path, to_email, smtp_config):
        return {
            "run_json_path": str(run_json_path),
            "to_email": to_email,
            "attempted_count": 1,
            "sent_count": 1,
            "skipped_count": 0,
            "skipped_zero_count": 0,
            "error_count": 0,
            "email_attempted": True,
            "email_sent": True,
            "email_skipped": 0,
            "email_error": False,
            "errors": [],
        }

    monkeypatch.setattr("jobintel_next.app.api.router.send_email_alerts_from_run", _fake_send_email_alerts_from_run)

    r = client.post("/alerts/run-all", params={"send_email": "true", "email_to": "to@example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["processed_ok"] == 1
    assert data["email_delivery"]["to_email"] == "to@example.com"
    assert data["email_delivery"]["sent_count"] == 1
    assert data["email_delivery"]["attempted_count"] == 1
    assert data["email_delivery"]["email_attempted"] is True
    run_id = data["run_id"]
    detail = client.get(f"/alerts/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["email_delivery"]["to_email"] == "to@example.com"


def test_run_all_send_email_uses_default_alert_email_fallback(monkeypatch, tmp_path: Path) -> None:
    client = _client_with_one_saved_search(tmp_path)
    update_user_settings(
        db_path=tmp_path / "saved.db",
        user_id="local-user",
        email="admin@example.com",
        default_alert_email="default-alerts@example.com",
        include_dismissed_default=True,
    )

    monkeypatch.setenv("JOBINTEL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_FROM", "from@example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_PORT", "587")

    called = {}

    def _fake_send_email_alerts_from_run(*, run_json_path, to_email, smtp_config):
        called["to_email"] = to_email
        return {
            "run_json_path": str(run_json_path),
            "to_email": to_email,
            "attempted_count": 1,
            "sent_count": 1,
            "skipped_count": 0,
            "skipped_zero_count": 0,
            "error_count": 0,
            "email_attempted": True,
            "email_sent": True,
            "email_skipped": 0,
            "email_error": False,
            "errors": [],
        }

    monkeypatch.setattr("jobintel_next.app.api.router.send_email_alerts_from_run", _fake_send_email_alerts_from_run)

    r = client.post("/alerts/run-all", params={"send_email": "true"})
    assert r.status_code == 200
    assert called["to_email"] == "default-alerts@example.com"
    data = r.json()
    assert data["email_delivery"]["to_email"] == "default-alerts@example.com"


def test_alerts_summary_endpoint(tmp_path: Path) -> None:
    client = _client_with_one_saved_search(tmp_path)
    r1 = client.post("/alerts/run-all")
    assert r1.status_code == 200

    r2 = client.get("/alerts/summary")
    assert r2.status_code == 200
    summary = r2.json()
    assert summary["runs_count"] >= 1
    assert summary["latest_run_id"]
    assert "recent_searches_with_new_matches" in summary
