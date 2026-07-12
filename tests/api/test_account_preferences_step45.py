from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jobintel_next.app.api import create_app
from jobintel_next.product.auth import create_local_user, get_user_settings


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
        }
    ]


def _login(client: TestClient, *, email: str, password: str) -> None:
    rep = client.post(
        "/login",
        data={"email": email, "password": password, "next": "/admin/account"},
        follow_redirects=False,
    )
    assert rep.status_code == 303


def test_account_page_render_and_update(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    _write(indexed, _rows())

    client = TestClient(create_app(input_path=indexed, saved_db_path=saved_db))
    _login(client, email="admin@example.com", password="admin123")

    r_get = client.get("/admin/account")
    assert r_get.status_code == 200
    assert "Account Settings" in r_get.text
    assert "Change Password" in r_get.text
    assert "Notification Preferences" in r_get.text
    assert "Target Search Profile" in r_get.text
    assert "digest email" in r_get.text.lower()
    assert "admin@example.com" in r_get.text

    r_post = client.post(
        "/admin/account",
        data={
            "email": "owner@example.com",
            "default_alert_email": "alerts@example.com",
            "include_dismissed_default": "on",
            "show_follow_up_attention": "on",
            "show_due_saved_search_attention": "on",
            "show_saved_search_quality_attention": "on",
            "show_digest_error_attention": "on",
            "digest_include_attention": "on",
            "target_titles": "backend engineer, data engineer",
            "target_role_families": "software_engineering,data_engineering",
            "preferred_location_types": "remote,hybrid",
            "salary_target_note": "target base 80k+",
            "keywords_note": "python, dbt",
        },
        follow_redirects=True,
    )
    assert r_post.status_code == 200
    assert "Account settings updated" in r_post.text
    assert "owner@example.com" in r_post.text

    settings = get_user_settings(db_path=saved_db, user_id="local-user")
    assert settings["email"] == "owner@example.com"
    assert settings["default_alert_email"] == "alerts@example.com"
    assert settings["include_dismissed_default"] is True
    assert settings["show_follow_up_attention"] is True
    assert settings["show_due_saved_search_attention"] is True
    assert settings["show_saved_search_quality_attention"] is True
    assert settings["show_digest_error_attention"] is True
    assert settings["digest_include_attention"] is True
    assert "backend engineer" in settings["target_titles"]
    assert "software_engineering" in settings["target_role_families"]
    assert "remote" in settings["preferred_location_types"]
    assert settings["salary_target_note"] == "target base 80k+"
    assert "python" in settings["keywords_note"]


def test_account_preferences_isolation_between_users(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    _write(indexed, _rows())

    app = create_app(input_path=indexed, saved_db_path=saved_db)
    create_local_user(db_path=saved_db, email="user2@example.com", password="user2pass", user_id="user-2")

    c1 = TestClient(app)
    c2 = TestClient(app)

    _login(c1, email="admin@example.com", password="admin123")
    _login(c2, email="user2@example.com", password="user2pass")

    r1 = c1.post(
        "/admin/account",
        data={
            "email": "owner@example.com",
            "default_alert_email": "owner-alerts@example.com",
        },
        follow_redirects=True,
    )
    assert r1.status_code == 200

    r2 = c2.get("/admin/account")
    assert r2.status_code == 200
    assert "user2@example.com" in r2.text
    assert "owner-alerts@example.com" not in r2.text

    s1 = get_user_settings(db_path=saved_db, user_id="local-user")
    s2 = get_user_settings(db_path=saved_db, user_id="user-2")
    assert s1["default_alert_email"] == "owner-alerts@example.com"
    assert s2["default_alert_email"] is None
