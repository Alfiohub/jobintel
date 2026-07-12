from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jobintel_next.app.api import create_app
from jobintel_next.product.auth import create_local_user


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


def test_admin_routes_require_session(tmp_path: Path) -> None:
    idx = tmp_path / "idx.jsonl"
    saved = tmp_path / "saved.db"
    _write(idx, _rows())

    client = TestClient(create_app(input_path=idx, saved_db_path=saved))
    r = client.get("/admin", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].startswith("/login")


def test_login_valid_and_logout(tmp_path: Path) -> None:
    idx = tmp_path / "idx.jsonl"
    saved = tmp_path / "saved.db"
    _write(idx, _rows())

    client = TestClient(create_app(input_path=idx, saved_db_path=saved))

    r_bad = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "wrong", "next": "/admin"},
        follow_redirects=False,
    )
    assert r_bad.status_code == 303
    assert r_bad.headers["location"].startswith("/login")

    r_ok = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123", "next": "/admin"},
        follow_redirects=False,
    )
    assert r_ok.status_code == 303
    assert r_ok.headers["location"] == "/admin"

    r_admin = client.get("/admin")
    assert r_admin.status_code == 200
    assert "Admin Overview" in r_admin.text

    r_logout = client.post("/logout", follow_redirects=False)
    assert r_logout.status_code == 303
    assert r_logout.headers["location"].startswith("/login")

    r_admin_after = client.get("/admin", follow_redirects=False)
    assert r_admin_after.status_code == 303
    assert r_admin_after.headers["location"].startswith("/login")


def test_session_user_data_isolation(tmp_path: Path) -> None:
    idx = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    _write(idx, _rows())

    app = create_app(input_path=idx, saved_db_path=saved_db)
    create_local_user(db_path=saved_db, email="user2@example.com", password="user2pass", user_id="user-2")

    c1 = TestClient(app)
    c2 = TestClient(app)

    l1 = c1.post("/login", data={"email": "admin@example.com", "password": "admin123", "next": "/admin"}, follow_redirects=False)
    l2 = c2.post("/login", data={"email": "user2@example.com", "password": "user2pass", "next": "/admin"}, follow_redirects=False)
    assert l1.status_code == 303
    assert l2.status_code == 303

    r1_create = c1.post(
        "/saved-searches",
        json={
            "name": "u1-search",
            "query_type": "filters",
            "filters_json": '{"normalized_title":"software_engineer"}',
        },
    )
    assert r1_create.status_code == 200

    r2_create = c2.post(
        "/saved-searches",
        json={
            "name": "u2-search",
            "query_type": "filters",
            "filters_json": '{"normalized_title":"software_engineer"}',
        },
    )
    assert r2_create.status_code == 200

    r1_list = c1.get("/saved-searches")
    r2_list = c2.get("/saved-searches")
    assert r1_list.status_code == 200
    assert r2_list.status_code == 200
    assert [x["name"] for x in r1_list.json()["saved_searches"]] == ["u1-search"]
    assert [x["name"] for x in r2_list.json()["saved_searches"]] == ["u2-search"]


def test_change_password_flow_and_login_with_new_password(tmp_path: Path) -> None:
    idx = tmp_path / "idx.jsonl"
    saved = tmp_path / "saved.db"
    _write(idx, _rows())
    client = TestClient(create_app(input_path=idx, saved_db_path=saved))

    login = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123", "next": "/admin/account"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    bad = client.post(
        "/admin/account/password",
        data={
            "current_password": "wrong",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        },
        follow_redirects=True,
    )
    assert bad.status_code == 200
    assert "current password is incorrect" in bad.text

    ok = client.post(
        "/admin/account/password",
        data={
            "current_password": "admin123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        },
        follow_redirects=True,
    )
    assert ok.status_code == 200
    assert "Password updated" in ok.text

    client.post("/logout", follow_redirects=False)
    old_login = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123", "next": "/admin"},
        follow_redirects=False,
    )
    assert old_login.status_code == 303
    assert old_login.headers["location"].startswith("/login")

    new_login = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "newpassword123", "next": "/admin"},
        follow_redirects=False,
    )
    assert new_login.status_code == 303
    assert new_login.headers["location"] == "/admin"
