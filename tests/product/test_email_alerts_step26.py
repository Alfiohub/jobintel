from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.product.alerts.email import (
    SMTPConfig,
    build_email_body_html,
    build_email_body_text,
    build_email_subject,
    send_email_alerts_from_run,
)


def _run_artifact(tmp_path: Path) -> Path:
    p = tmp_path / "run.json"
    p.write_text(
        json.dumps(
            {
                "run_timestamp": "2026-03-30T10:00:00+00:00",
                "results": [
                    {
                        "search_id": "a",
                        "name": "high confidence tech",
                        "status": "ok",
                        "run_timestamp": "2026-03-30T10:00:00+00:00",
                        "new_matches_count": 2,
                        "sample_new_matches": [
                            {"title_raw": "Software Engineer", "url": "https://e/1"},
                            {"title_raw": "Data Engineer", "url": "https://e/2"},
                        ],
                    },
                    {
                        "search_id": "b",
                        "name": "marketing",
                        "status": "ok",
                        "run_timestamp": "2026-03-30T10:00:00+00:00",
                        "new_matches_count": 0,
                        "sample_new_matches": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return p


def test_render_subject_and_body() -> None:
    subject = build_email_subject(search_name="high confidence tech", new_matches_count=4)
    body_text = build_email_body_text(
        search_name="high confidence tech",
        new_matches_count=4,
        run_timestamp="2026-03-30T10:00:00+00:00",
        sample_new_matches=[{"title_raw": "Software Engineer", "url": "https://e/1"}],
    )
    body_html = build_email_body_html(
        search_name="high confidence tech",
        new_matches_count=4,
        run_timestamp="2026-03-30T10:00:00+00:00",
        sample_new_matches=[{"title_raw": "Software Engineer", "url": "https://e/1"}],
    )
    assert subject == "[JobIntel] 4 new matches · high confidence tech"
    assert "Saved search: high confidence tech" in body_text
    assert "Software Engineer" in body_text
    assert "https://e/1" in body_text
    assert "<strong>Saved search:</strong> high confidence tech" in body_html
    assert "<a href=\"https://e/1\">https://e/1</a>" in body_html


def test_send_email_from_run_skips_zero_new(monkeypatch, tmp_path: Path) -> None:
    run_json = _run_artifact(tmp_path)
    sent_subjects: list[str] = []

    def _fake_send_email_message(*, smtp, to_email, subject, body_text, body_html=None):
        sent_subjects.append(subject)

    monkeypatch.setattr("jobintel_next.product.alerts.email.send_email_message", _fake_send_email_message)
    rep = send_email_alerts_from_run(
        run_json_path=run_json,
        to_email="to@example.com",
        smtp_config=SMTPConfig(host="smtp.example.com", port=587, from_email="from@example.com"),
    )
    assert rep["sent_count"] == 1
    assert rep["skipped_zero_count"] == 1
    assert rep["attempted_count"] == 1
    assert rep["skipped_count"] == 1
    assert rep["email_attempted"] is True
    assert rep["attempted_at"]
    assert rep["delivery_timestamp"]
    assert len(sent_subjects) == 1
    assert "high confidence tech" in sent_subjects[0]


def test_send_email_from_run_with_mock_sender_error(monkeypatch, tmp_path: Path) -> None:
    run_json = _run_artifact(tmp_path)

    def _fake_send_email_message(*, smtp, to_email, subject, body_text, body_html=None):
        raise RuntimeError("smtp down")

    monkeypatch.setattr("jobintel_next.product.alerts.email.send_email_message", _fake_send_email_message)
    rep = send_email_alerts_from_run(
        run_json_path=run_json,
        to_email="to@example.com",
        smtp_config=SMTPConfig(host="smtp.example.com", port=587, from_email="from@example.com"),
    )
    assert rep["sent_count"] == 0
    assert rep["error_count"] == 1
    assert rep["email_error"] is True
    assert rep["attempted_at"]
    assert rep["delivery_timestamp"]
