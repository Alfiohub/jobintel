from __future__ import annotations

import argparse
import json
from pathlib import Path

from jobintel_next.cli import _cmd_alerts_run_due
from jobintel_next.product.application_tracking import update_application_details
from jobintel_next.product.alerts.digest import (
    build_digest_body_html,
    build_digest_body_text,
    build_digest_subject,
    send_digest_email_from_run,
)
from jobintel_next.product.alerts.email import SMTPConfig
from jobintel_next.product.auth import update_user_settings
from jobintel_next.product.job_state import set_job_state
from jobintel_next.product.saved_searches import create_saved_search
from jobintel_next.storage import build_sqlite_index


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


def _run_artifact(tmp_path: Path) -> Path:
    p = tmp_path / "run.json"
    p.write_text(
        json.dumps(
            {
                "run_timestamp": "2026-03-31T10:00:00+00:00",
                "searches_total": 2,
                "processed_ok": 2,
                "total_new_matches": 3,
                "results": [
                    {
                        "name": "SE",
                        "status": "ok",
                        "new_matches_count": 2,
                        "sample_new_matches": [
                            {"title_raw": "Software Engineer", "url": "https://e/1"},
                            {"title_raw": "Staff Software Engineer", "url": "https://e/2"},
                        ],
                    },
                    {
                        "name": "AE",
                        "status": "ok",
                        "new_matches_count": 1,
                        "sample_new_matches": [{"title_raw": "Account Executive", "url": "https://e/3"}],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return p


def test_digest_render_subject_and_body() -> None:
    subject = build_digest_subject(total_new_matches=7, searches_with_new_matches=3)
    body_text = build_digest_body_text(
        run_timestamp="2026-03-31T10:00:00+00:00",
        searches_total=5,
        searches_processed=4,
        searches_with_new_matches=3,
        total_new_matches=7,
        results=[
            {
                "name": "high confidence tech",
                "status": "ok",
                "new_matches_count": 2,
                "sample_new_matches": [{"title_raw": "Software Engineer", "url": "https://e/1"}],
            }
        ],
    )
    body_html = build_digest_body_html(
        run_timestamp="2026-03-31T10:00:00+00:00",
        searches_total=5,
        searches_processed=4,
        searches_with_new_matches=3,
        total_new_matches=7,
        results=[
            {
                "name": "high confidence tech",
                "status": "ok",
                "new_matches_count": 2,
                "sample_new_matches": [{"title_raw": "Software Engineer", "url": "https://e/1"}],
            }
        ],
    )
    assert subject == "[JobIntel] Daily digest · 7 new matches across 3 searches"
    assert "Saved searches total: 5" in body_text
    assert "high confidence tech: 2 new" in body_text
    assert "https://e/1" in body_text
    assert "<h3>JobIntel Daily Digest</h3>" in body_html
    assert "high confidence tech" in body_html


def test_digest_render_includes_needs_attention_section() -> None:
    body_text = build_digest_body_text(
        run_timestamp="2026-03-31T10:00:00+00:00",
        searches_total=1,
        searches_processed=1,
        searches_with_new_matches=1,
        total_new_matches=2,
        results=[
            {
                "name": "SE",
                "status": "ok",
                "new_matches_count": 2,
                "sample_new_matches": [{"title_raw": "Software Engineer", "url": "https://e/1"}],
            }
        ],
        attention_items=[
            {"priority": "high", "title": "Follow-up overdue: https://e/1", "href": "/admin/shortlist?only_follow_up_due=true"}
        ],
    )
    body_html = build_digest_body_html(
        run_timestamp="2026-03-31T10:00:00+00:00",
        searches_total=1,
        searches_processed=1,
        searches_with_new_matches=1,
        total_new_matches=2,
        results=[
            {
                "name": "SE",
                "status": "ok",
                "new_matches_count": 2,
                "sample_new_matches": [{"title_raw": "Software Engineer", "url": "https://e/1"}],
            }
        ],
        attention_items=[
            {"priority": "high", "title": "Follow-up overdue: https://e/1", "href": "/admin/shortlist?only_follow_up_due=true"}
        ],
    )
    assert "Needs attention:" in body_text
    assert "Follow-up overdue" in body_text
    assert "Needs attention" in body_html
    assert "/admin/shortlist?only_follow_up_due=true" in body_html


def test_digest_send_skips_when_no_new_matches(tmp_path: Path) -> None:
    run_json = tmp_path / "run_zero.json"
    run_json.write_text(
        json.dumps(
            {
                "run_timestamp": "2026-03-31T10:00:00+00:00",
                "searches_total": 1,
                "processed_ok": 1,
                "total_new_matches": 0,
                "results": [{"name": "SE", "status": "ok", "new_matches_count": 0, "sample_new_matches": []}],
            }
        ),
        encoding="utf-8",
    )
    rep = send_digest_email_from_run(
        run_json_path=run_json,
        to_email="digest@example.com",
        smtp_config=SMTPConfig(host="smtp.example.com", port=587, from_email="from@example.com"),
    )
    assert rep["sent_count"] == 0
    assert rep["skipped_count"] == 1
    assert rep["skip_reason"] == "no_new_matches"


def test_run_due_digest_uses_default_alert_email_and_persists_metadata(monkeypatch, tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"
    _write(jobs_jsonl, _rows())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    create_saved_search(
        db_path=saved_db,
        name="daily se",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
        user_id="local-user",
        user_email="local@example.com",
    )
    update_user_settings(
        db_path=saved_db,
        user_id="local-user",
        email="local@example.com",
        default_alert_email="digest@example.com",
        include_dismissed_default=True,
    )

    monkeypatch.setenv("JOBINTEL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_FROM", "from@example.com")
    sent_to: dict[str, str] = {}

    def _fake_send_email_message(*, smtp, to_email, subject, body_text, body_html=None):
        sent_to["to_email"] = to_email
        sent_to["subject"] = subject

    monkeypatch.setattr("jobintel_next.product.alerts.digest.send_email_message", _fake_send_email_message)

    rc = _cmd_alerts_run_due(
        argparse.Namespace(
            saved_db=str(saved_db),
            job_state_db=str(tmp_path / "job_state.db"),
            input=str(jobs_jsonl),
            sqlite=str(jobs_db),
            outdir=str(outdir),
            scan_limit=5000,
            limit=200,
            sample_size=5,
            user_id="local-user",
            user_email="local@example.com",
            send_digest_email=True,
            email_to=None,
        )
    )
    assert rc == 0
    assert sent_to["to_email"] == "digest@example.com"
    assert "[JobIntel] Daily digest" in sent_to["subject"]

    run_files = sorted((outdir / "local-user").glob("*.json"))
    assert run_files
    obj = json.loads(run_files[-1].read_text(encoding="utf-8"))
    delivery = obj.get("digest_delivery")
    assert isinstance(delivery, dict)
    assert delivery["to_email"] == "digest@example.com"
    assert delivery["email_sent"] is True
    assert delivery["attempted_at"]
    assert delivery["delivery_timestamp"]


def test_run_due_digest_persists_error_metadata_when_smtp_send_fails(monkeypatch, tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"
    _write(jobs_jsonl, _rows())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    create_saved_search(
        db_path=saved_db,
        name="daily se",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
        user_id="local-user",
        user_email="local@example.com",
    )
    update_user_settings(
        db_path=saved_db,
        user_id="local-user",
        email="local@example.com",
        default_alert_email="digest@example.com",
        include_dismissed_default=True,
    )

    monkeypatch.setenv("JOBINTEL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_FROM", "from@example.com")

    def _fake_send_email_message(*, smtp, to_email, subject, body_text, body_html=None):
        raise RuntimeError("smtp boom")

    monkeypatch.setattr(
        "jobintel_next.product.alerts.digest.send_email_message",
        _fake_send_email_message,
    )

    rc = _cmd_alerts_run_due(
        argparse.Namespace(
            saved_db=str(saved_db),
            job_state_db=str(tmp_path / "job_state.db"),
            input=str(jobs_jsonl),
            sqlite=str(jobs_db),
            outdir=str(outdir),
            scan_limit=5000,
            limit=200,
            sample_size=5,
            user_id="local-user",
            user_email="local@example.com",
            send_digest_email=True,
            email_to=None,
        )
    )
    assert rc == 0

    run_files = sorted((outdir / "local-user").glob("*.json"))
    assert run_files, "expected run artifact json to be created"
    obj = json.loads(run_files[-1].read_text(encoding="utf-8"))
    delivery = obj.get("digest_delivery")
    assert isinstance(delivery, dict)
    assert delivery["to_email"] == "digest@example.com"
    assert delivery["email_attempted"] is True
    assert delivery["email_sent"] is False
    assert delivery["error_count"] >= 1
    assert delivery["email_error"] is True
    assert delivery["attempted_at"]
    assert delivery["delivery_timestamp"]
    errors = delivery.get("errors") or []
    assert errors and "smtp boom" in str(errors[0].get("error") or "")


def test_run_due_digest_respects_digest_include_attention_preference(monkeypatch, tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    job_state_db = tmp_path / "job_state.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    outdir = tmp_path / "alerts"
    _write(jobs_jsonl, _rows())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    create_saved_search(
        db_path=saved_db,
        name="daily se",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        frequency="daily",
        user_id="local-user",
        user_email="local@example.com",
    )
    set_job_state(
        db_path=job_state_db,
        job_url="https://e/1",
        state="saved",
        user_id="local-user",
        user_email="local@example.com",
    )
    update_application_details(
        db_path=job_state_db,
        job_url="https://e/1",
        notes="",
        follow_up_at="2020-01-01",
        follow_up_note="follow",
        user_id="local-user",
        user_email="local@example.com",
    )
    update_user_settings(
        db_path=saved_db,
        user_id="local-user",
        email="local@example.com",
        default_alert_email="digest@example.com",
        include_dismissed_default=True,
        digest_include_attention=False,
    )

    monkeypatch.setenv("JOBINTEL_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("JOBINTEL_SMTP_FROM", "from@example.com")
    captured: dict[str, str] = {}

    def _fake_send_email_message(*, smtp, to_email, subject, body_text, body_html=None):
        captured["body_text"] = body_text
        captured["body_html"] = body_html or ""

    monkeypatch.setattr("jobintel_next.product.alerts.digest.send_email_message", _fake_send_email_message)

    rc = _cmd_alerts_run_due(
        argparse.Namespace(
            saved_db=str(saved_db),
            job_state_db=str(job_state_db),
            input=str(jobs_jsonl),
            sqlite=str(jobs_db),
            outdir=str(outdir),
            scan_limit=5000,
            limit=200,
            sample_size=5,
            user_id="local-user",
            user_email="local@example.com",
            send_digest_email=True,
            email_to=None,
        )
    )
    assert rc == 0
    assert "Needs attention:" not in captured.get("body_text", "")
