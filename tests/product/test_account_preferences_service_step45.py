from __future__ import annotations

from pathlib import Path

from jobintel_next.product.auth import authenticate_local_user, change_local_password, create_local_user, get_user_settings, update_user_settings


def test_update_user_settings_persistence_and_isolation(tmp_path: Path) -> None:
    db = tmp_path / "saved.db"

    u1 = create_local_user(db_path=db, email="u1@example.com", password="password1", user_id="u1")
    u2 = create_local_user(db_path=db, email="u2@example.com", password="password2", user_id="u2")

    assert u1["user_id"] == "u1"
    assert u2["user_id"] == "u2"

    updated = update_user_settings(
        db_path=db,
        user_id="u1",
        email="u1-new@example.com",
        default_alert_email="alerts-u1@example.com",
        include_dismissed_default=False,
        show_saved_search_quality_attention=False,
        show_due_saved_search_attention=False,
        show_follow_up_attention=True,
        show_digest_error_attention=True,
        digest_include_attention=False,
        target_titles="backend engineer, data engineer",
        target_role_families="software_engineering,data_engineering",
        preferred_location_types="remote,hybrid",
        salary_target_note="target base 80k+",
        keywords_note="python,dbt,fastapi",
    )
    assert updated["email"] == "u1-new@example.com"
    assert updated["default_alert_email"] == "alerts-u1@example.com"
    assert updated["include_dismissed_default"] is False
    assert updated["show_saved_search_quality_attention"] is False
    assert updated["show_due_saved_search_attention"] is False
    assert updated["show_follow_up_attention"] is True
    assert updated["show_digest_error_attention"] is True
    assert updated["digest_include_attention"] is False
    assert "backend engineer" in updated["target_titles"]
    assert "software_engineering" in updated["target_role_families"]
    assert "remote" in updated["preferred_location_types"]
    assert updated["salary_target_note"] == "target base 80k+"
    assert "python" in updated["keywords_note"]

    u1_read = get_user_settings(db_path=db, user_id="u1")
    u2_read = get_user_settings(db_path=db, user_id="u2")
    assert u1_read["email"] == "u1-new@example.com"
    assert u1_read["default_alert_email"] == "alerts-u1@example.com"
    assert u1_read["include_dismissed_default"] is False
    assert u1_read["show_saved_search_quality_attention"] is False
    assert u1_read["show_due_saved_search_attention"] is False
    assert u1_read["digest_include_attention"] is False
    assert "backend engineer" in u1_read["target_titles"]
    assert "software_engineering" in u1_read["target_role_families"]
    assert "remote" in u1_read["preferred_location_types"]
    assert u1_read["salary_target_note"] == "target base 80k+"
    assert "python" in u1_read["keywords_note"]

    assert u2_read["email"] == "u2@example.com"
    assert u2_read["default_alert_email"] is None
    assert u2_read["include_dismissed_default"] is True
    assert u2_read["show_saved_search_quality_attention"] is True
    assert u2_read["show_due_saved_search_attention"] is True
    assert u2_read["show_follow_up_attention"] is True
    assert u2_read["show_digest_error_attention"] is True
    assert u2_read["digest_include_attention"] is True
    assert u2_read["target_titles"] == ""
    assert u2_read["target_role_families"] == ""
    assert u2_read["preferred_location_types"] == ""
    assert u2_read["salary_target_note"] == ""
    assert u2_read["keywords_note"] == ""


def test_change_local_password_success_and_wrong_current(tmp_path: Path) -> None:
    db = tmp_path / "saved.db"
    create_local_user(db_path=db, email="user@example.com", password="initial123", user_id="u1")

    bad = None
    try:
        change_local_password(db_path=db, user_id="u1", current_password="wrong", new_password="newpass123")
    except ValueError as exc:
        bad = str(exc)
    assert bad == "current password is incorrect"

    ok = change_local_password(db_path=db, user_id="u1", current_password="initial123", new_password="newpass123")
    assert ok["password_changed"] is True

    assert authenticate_local_user(db_path=db, email="user@example.com", password="initial123") is None
    assert authenticate_local_user(db_path=db, email="user@example.com", password="newpass123") is not None
