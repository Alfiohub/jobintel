from __future__ import annotations

from pathlib import Path

from jobintel_next.product.application_tracking import build_closed_loop_metrics, set_application_state


def test_closed_loop_metrics_counts_and_rates(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    urls = [f"https://e/{i}" for i in range(1, 7)]
    set_application_state(db_path=db, job_url=urls[0], state="saved", user_id="u1", user_email="u1@example.com")
    set_application_state(db_path=db, job_url=urls[1], state="saved", user_id="u1", user_email="u1@example.com")
    set_application_state(db_path=db, job_url=urls[2], state="applied", user_id="u1", user_email="u1@example.com")
    set_application_state(db_path=db, job_url=urls[3], state="interview", user_id="u1", user_email="u1@example.com")
    set_application_state(db_path=db, job_url=urls[4], state="rejected", user_id="u1", user_email="u1@example.com")
    set_application_state(db_path=db, job_url=urls[5], state="applied", user_id="u2", user_email="u2@example.com")

    m = build_closed_loop_metrics(db_path=db, job_urls=urls[:5], user_id="u1")
    assert m["saved_count"] == 2
    assert m["applied_count"] == 1
    assert m["interview_count"] == 1
    assert m["rejected_count"] == 1
    assert m["open_pipeline_count"] == 4
    assert m["total_count"] == 5
    assert float(m["saved_to_applied_rate"]) == 0.2
    assert float(m["applied_to_interview_rate"]) == 1.0
    assert float(m["interview_to_rejected_rate"]) == 1.0


def test_closed_loop_metrics_empty_input_is_zero(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    m = build_closed_loop_metrics(db_path=db, job_urls=[], user_id="u1")
    assert m["open_pipeline_count"] == 0
    assert m["applied_count"] == 0
    assert m["interview_count"] == 0
    assert m["rejected_count"] == 0
    assert float(m["saved_to_applied_rate"]) == 0.0
    assert float(m["applied_to_interview_rate"]) == 0.0
    assert float(m["interview_to_rejected_rate"]) == 0.0
