from __future__ import annotations

from pathlib import Path

from jobintel_next.product.application_tracking import (
    clear_application_details,
    clear_application_state,
    get_application_details,
    get_many_application_details,
    get_application_state,
    get_many_application_states,
    update_application_details,
    set_application_state,
)


def test_application_state_persistence_and_default_saved(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    url = "https://e/1"

    default = get_application_state(db_path=db, job_url=url, user_id="u1")
    assert default["state"] == "saved"

    set_application_state(db_path=db, job_url=url, state="applied", user_id="u1", user_email="u1@example.com")
    row = get_application_state(db_path=db, job_url=url, user_id="u1")
    assert row["state"] == "applied"

    clear_application_state(db_path=db, job_url=url, user_id="u1")
    reset = get_application_state(db_path=db, job_url=url, user_id="u1")
    assert reset["state"] == "saved"


def test_application_state_isolation_per_user(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    url = "https://e/1"

    set_application_state(db_path=db, job_url=url, state="interview", user_id="u1", user_email="u1@example.com")
    set_application_state(db_path=db, job_url=url, state="rejected", user_id="u2", user_email="u2@example.com")

    u1 = get_application_state(db_path=db, job_url=url, user_id="u1")
    u2 = get_application_state(db_path=db, job_url=url, user_id="u2")
    assert u1["state"] == "interview"
    assert u2["state"] == "rejected"

    many_u1 = get_many_application_states(db_path=db, job_urls=[url, "https://e/2"], user_id="u1")
    assert many_u1[url] == "interview"
    assert many_u1["https://e/2"] == "saved"


def test_application_details_persistence_and_clear(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    url = "https://e/1"

    update_application_details(
        db_path=db,
        job_url=url,
        notes="sent referral",
        applied_at="2026-04-01",
        interview_at="",
        follow_up_at="2026-04-04",
        follow_up_note="check reply",
        application_channel="linkedin",
        contact_name="Alice Recruiter",
        contact_email="alice@example.com",
        compensation_note="target 70k+",
        external_application_url="https://apply.example.com/123",
        resume_label="CV backend v2",
        cover_letter_label="CL generic data role",
        submission_note="submitted through company site with custom answers",
        user_id="u1",
        user_email="u1@example.com",
    )
    row = get_application_details(db_path=db, job_url=url, user_id="u1")
    assert row["notes"] == "sent referral"
    assert row["applied_at"] == "2026-04-01"
    assert row["interview_at"] == ""
    assert row["follow_up_at"] == "2026-04-04"
    assert row["follow_up_note"] == "check reply"
    assert row["application_channel"] == "linkedin"
    assert row["contact_name"] == "Alice Recruiter"
    assert row["contact_email"] == "alice@example.com"
    assert row["compensation_note"] == "target 70k+"
    assert row["external_application_url"] == "https://apply.example.com/123"
    assert row["resume_label"] == "CV backend v2"
    assert row["cover_letter_label"] == "CL generic data role"
    assert "custom answers" in row["submission_note"]

    clear_application_details(db_path=db, job_url=url, user_id="u1")
    reset = get_application_details(db_path=db, job_url=url, user_id="u1")
    assert reset["notes"] == ""
    assert reset["applied_at"] == ""
    assert reset["interview_at"] == ""
    assert reset["follow_up_at"] == ""
    assert reset["follow_up_note"] == ""
    assert reset["application_channel"] == ""
    assert reset["contact_name"] == ""
    assert reset["contact_email"] == ""
    assert reset["compensation_note"] == ""
    assert reset["external_application_url"] == ""
    assert reset["resume_label"] == ""
    assert reset["cover_letter_label"] == ""
    assert reset["submission_note"] == ""


def test_application_details_isolation_per_user(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    url = "https://e/1"

    update_application_details(
        db_path=db,
        job_url=url,
        notes="u1-note",
        applied_at="2026-04-01",
        interview_at="",
        follow_up_at="2026-04-02",
        follow_up_note="u1-fup",
        application_channel="referral",
        contact_name="U1 Recruiter",
        contact_email="u1@example.com",
        compensation_note="u1 comp",
        external_application_url="https://u1.example.com",
        resume_label="u1-cv",
        cover_letter_label="u1-cl",
        submission_note="u1 submitted",
        user_id="u1",
        user_email="u1@example.com",
    )
    update_application_details(
        db_path=db,
        job_url=url,
        notes="u2-note",
        applied_at="",
        interview_at="2026-04-10",
        follow_up_at="2026-04-12",
        follow_up_note="u2-fup",
        application_channel="company_site",
        contact_name="U2 Recruiter",
        contact_email="u2@example.com",
        compensation_note="u2 comp",
        external_application_url="https://u2.example.com",
        resume_label="u2-cv",
        cover_letter_label="u2-cl",
        submission_note="u2 submitted",
        user_id="u2",
        user_email="u2@example.com",
    )

    u1 = get_application_details(db_path=db, job_url=url, user_id="u1")
    u2 = get_application_details(db_path=db, job_url=url, user_id="u2")
    assert u1["notes"] == "u1-note"
    assert u1["interview_at"] == ""
    assert u1["follow_up_note"] == "u1-fup"
    assert u1["application_channel"] == "referral"
    assert u1["contact_name"] == "U1 Recruiter"
    assert u1["resume_label"] == "u1-cv"
    assert u1["cover_letter_label"] == "u1-cl"
    assert u2["notes"] == "u2-note"
    assert u2["interview_at"] == "2026-04-10"
    assert u2["follow_up_note"] == "u2-fup"
    assert u2["application_channel"] == "company_site"
    assert u2["contact_name"] == "U2 Recruiter"
    assert u2["resume_label"] == "u2-cv"
    assert u2["cover_letter_label"] == "u2-cl"

    many = get_many_application_details(db_path=db, job_urls=[url, "https://e/2"], user_id="u1")
    assert many[url]["notes"] == "u1-note"
    assert many["https://e/2"]["notes"] == ""


def test_interview_state_auto_sets_interview_at(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    url = "https://e/1"
    set_application_state(db_path=db, job_url=url, state="interview", user_id="u1", user_email="u1@example.com")
    details = get_application_details(db_path=db, job_url=url, user_id="u1")
    assert details["interview_at"] != ""
