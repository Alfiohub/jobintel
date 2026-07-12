from __future__ import annotations

from pathlib import Path

import pytest

from jobintel_next.product.job_state import (
    clear_job_state,
    count_user_job_states,
    get_job_state,
    get_many_job_states,
    list_job_urls_by_state,
    set_job_state,
)


def test_job_state_set_get_clear_roundtrip(tmp_path: Path) -> None:
    db = tmp_path / "job_state.db"
    url = "https://jobs/1"

    initial = get_job_state(db_path=db, job_url=url)
    assert initial["state"] == "new"

    saved = set_job_state(db_path=db, job_url=url, state="saved")
    assert saved["state"] == "saved"
    assert saved["updated_at"]

    current = get_job_state(db_path=db, job_url=url)
    assert current["state"] == "saved"

    cleared = clear_job_state(db_path=db, job_url=url)
    assert cleared["deleted"] is True

    after_clear = get_job_state(db_path=db, job_url=url)
    assert after_clear["state"] == "new"


def test_get_many_job_states_defaults_to_new(tmp_path: Path) -> None:
    db = tmp_path / "job_state.db"
    u1 = "https://jobs/a"
    u2 = "https://jobs/b"
    u3 = "https://jobs/c"

    set_job_state(db_path=db, job_url=u1, state="seen")
    set_job_state(db_path=db, job_url=u2, state="dismissed")

    states = get_many_job_states(db_path=db, job_urls=[u1, u2, u3])
    assert states[u1] == "seen"
    assert states[u2] == "dismissed"
    assert states[u3] == "new"


def test_invalid_state_raises(tmp_path: Path) -> None:
    db = tmp_path / "job_state.db"
    with pytest.raises(ValueError, match="invalid job state"):
        set_job_state(db_path=db, job_url="https://jobs/1", state="archived")


def test_job_state_isolated_by_user_id(tmp_path: Path) -> None:
    db = tmp_path / "job_state.db"
    url = "https://jobs/1"
    set_job_state(db_path=db, job_url=url, state="saved", user_id="user-1", user_email="u1@example.com")

    u1 = get_job_state(db_path=db, job_url=url, user_id="user-1")
    u2 = get_job_state(db_path=db, job_url=url, user_id="user-2")
    assert u1["state"] == "saved"
    assert u2["state"] == "new"


def test_count_user_job_states(tmp_path: Path) -> None:
    db = tmp_path / "job_state.db"
    set_job_state(db_path=db, job_url="https://jobs/1", state="saved", user_id="user-1", user_email="u1@example.com")
    set_job_state(db_path=db, job_url="https://jobs/2", state="dismissed", user_id="user-1", user_email="u1@example.com")
    set_job_state(db_path=db, job_url="https://jobs/3", state="seen", user_id="user-1", user_email="u1@example.com")
    set_job_state(db_path=db, job_url="https://jobs/4", state="saved", user_id="user-2", user_email="u2@example.com")

    c1 = count_user_job_states(db_path=db, user_id="user-1")
    c2 = count_user_job_states(db_path=db, user_id="user-2")
    assert c1["saved"] == 1
    assert c1["dismissed"] == 1
    assert c1["seen"] == 1
    assert c2["saved"] == 1
    assert c2["dismissed"] == 0


def test_list_job_urls_by_state_isolated_by_user(tmp_path: Path) -> None:
    db = tmp_path / "job_state.db"
    set_job_state(db_path=db, job_url="https://jobs/1", state="saved", user_id="u1", user_email="u1@example.com")
    set_job_state(db_path=db, job_url="https://jobs/2", state="saved", user_id="u1", user_email="u1@example.com")
    set_job_state(db_path=db, job_url="https://jobs/3", state="dismissed", user_id="u1", user_email="u1@example.com")
    set_job_state(db_path=db, job_url="https://jobs/4", state="saved", user_id="u2", user_email="u2@example.com")

    u1_saved = list_job_urls_by_state(db_path=db, state="saved", user_id="u1")
    u2_saved = list_job_urls_by_state(db_path=db, state="saved", user_id="u2")
    assert "https://jobs/1" in u1_saved and "https://jobs/2" in u1_saved
    assert "https://jobs/4" not in u1_saved
    assert u2_saved == ["https://jobs/4"]
