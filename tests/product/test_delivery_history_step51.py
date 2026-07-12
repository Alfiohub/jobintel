from __future__ import annotations

import argparse
import json
from pathlib import Path

from jobintel_next.cli import _cmd_alerts_resend_digest


def _run_with_new(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "run_id": "run-new",
                "run_timestamp": "2026-03-31T10:00:00+00:00",
                "total_new_matches": 2,
                "searches_total": 1,
                "processed_ok": 1,
                "results": [
                    {
                        "name": "daily se",
                        "status": "ok",
                        "new_matches_count": 2,
                        "sample_new_matches": [{"title_raw": "Software Engineer", "url": "https://e/1"}],
                    }
                ],
                "digest_delivery": {
                    "to_email": "digest@example.com",
                },
            }
        ),
        encoding="utf-8",
    )


def _run_without_new(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "run_id": "run-zero",
                "run_timestamp": "2026-03-31T10:00:00+00:00",
                "total_new_matches": 0,
                "searches_total": 1,
                "processed_ok": 1,
                "results": [
                    {
                        "name": "daily se",
                        "status": "ok",
                        "new_matches_count": 0,
                        "sample_new_matches": [],
                    }
                ],
                "digest_delivery": {
                    "to_email": "digest@example.com",
                },
            }
        ),
        encoding="utf-8",
    )


def test_resend_digest_from_valid_run_artifact(monkeypatch, tmp_path: Path) -> None:
    run_json = tmp_path / "run.json"
    _run_with_new(run_json)
    monkeypatch.setenv("JOBINTEL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_FROM", "from@example.com")

    sent: dict[str, str] = {}

    def _fake_send_email_message(*, smtp, to_email, subject, body_text, body_html=None):
        sent["to_email"] = to_email
        sent["subject"] = subject

    monkeypatch.setattr("jobintel_next.product.alerts.digest.send_email_message", _fake_send_email_message)
    rc = _cmd_alerts_resend_digest(argparse.Namespace(run_json=str(run_json), to=None))
    assert rc == 0
    assert sent["to_email"] == "digest@example.com"
    assert "[JobIntel] Daily digest" in sent["subject"]

    obj = json.loads(run_json.read_text(encoding="utf-8"))
    delivery = obj.get("digest_delivery")
    assert isinstance(delivery, dict)
    assert delivery["resend"] is True
    assert delivery["email_sent"] is True
    assert delivery["sent_count"] == 1
    assert delivery["attempted_at"]
    assert delivery["delivery_timestamp"]


def test_resend_digest_skips_when_no_new_matches(monkeypatch, tmp_path: Path) -> None:
    run_json = tmp_path / "run_zero.json"
    _run_without_new(run_json)
    monkeypatch.setenv("JOBINTEL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_FROM", "from@example.com")
    rc = _cmd_alerts_resend_digest(argparse.Namespace(run_json=str(run_json), to=None))
    assert rc == 0
    obj = json.loads(run_json.read_text(encoding="utf-8"))
    delivery = obj.get("digest_delivery")
    assert isinstance(delivery, dict)
    assert delivery["sent_count"] == 0
    assert delivery["skipped_count"] == 1
    assert delivery["skip_reason"] == "no_new_matches"


def test_resend_digest_errors_when_destination_missing(monkeypatch, tmp_path: Path) -> None:
    run_json = tmp_path / "run_missing_dest.json"
    run_json.write_text(
        json.dumps(
            {
                "run_id": "run-missing",
                "run_timestamp": "2026-03-31T10:00:00+00:00",
                "total_new_matches": 2,
                "results": [
                    {"name": "daily se", "status": "ok", "new_matches_count": 2, "sample_new_matches": []},
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("JOBINTEL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_FROM", "from@example.com")
    rc = _cmd_alerts_resend_digest(argparse.Namespace(run_json=str(run_json), to=None))
    assert rc == 1
