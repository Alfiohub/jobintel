from __future__ import annotations

from pathlib import Path

from jobintel_next.product.application_tracking import (
    create_application_template,
    delete_application_template,
    list_application_templates,
    set_application_template_active,
)


def test_application_templates_crud_and_toggle(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    created = create_application_template(
        db_path=db,
        kind="resume",
        label="CV backend v2",
        description="backend focused",
        user_id="u1",
        user_email="u1@example.com",
    )
    assert created["kind"] == "resume"
    assert created["label"] == "CV backend v2"
    assert created["is_active"] is True

    listed = list_application_templates(db_path=db, user_id="u1", include_inactive=True)
    assert len(listed) == 1
    assert listed[0]["label"] == "CV backend v2"

    tid = str(created["template_id"])
    disabled = set_application_template_active(db_path=db, template_id=tid, is_active=False, user_id="u1")
    assert disabled["is_active"] is False

    only_active = list_application_templates(db_path=db, user_id="u1", include_inactive=False)
    assert only_active == []

    enabled = set_application_template_active(db_path=db, template_id=tid, is_active=True, user_id="u1")
    assert enabled["is_active"] is True
    only_active_after = list_application_templates(db_path=db, user_id="u1", include_inactive=False)
    assert len(only_active_after) == 1

    rep = delete_application_template(db_path=db, template_id=tid, user_id="u1")
    assert rep["deleted"] is True
    assert list_application_templates(db_path=db, user_id="u1", include_inactive=True) == []


def test_application_templates_isolation_per_user(tmp_path: Path) -> None:
    db = tmp_path / "app_state.db"
    t1 = create_application_template(
        db_path=db,
        kind="resume",
        label="u1 resume",
        user_id="u1",
        user_email="u1@example.com",
    )
    create_application_template(
        db_path=db,
        kind="cover_letter",
        label="u2 cover",
        user_id="u2",
        user_email="u2@example.com",
    )

    u1_list = list_application_templates(db_path=db, user_id="u1", include_inactive=True)
    u2_list = list_application_templates(db_path=db, user_id="u2", include_inactive=True)
    assert [x["label"] for x in u1_list] == ["u1 resume"]
    assert [x["label"] for x in u2_list] == ["u2 cover"]

    rep = delete_application_template(db_path=db, template_id=str(t1["template_id"]), user_id="u2")
    assert rep["deleted"] is False
    still_u1 = list_application_templates(db_path=db, user_id="u1", include_inactive=True)
    assert [x["label"] for x in still_u1] == ["u1 resume"]
