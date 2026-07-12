from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from jobintel_next.product.saved_searches import (
    archive_saved_search,
    check_new_matches,
    create_saved_search,
    delete_saved_search,
    disable_saved_search,
    enable_saved_search,
    get_saved_search_results,
    get_saved_search,
    list_saved_searches,
    restore_saved_search,
    run_saved_search,
    update_saved_search,
)
from jobintel_next.storage import build_sqlite_index


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows_v1() -> list[dict]:
    return [
        {
            "url": "https://e/1",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "has_salary": False,
            "has_skills": False,
            "title_is_other": False,
            "language_bucket": "en",
            "published_at": "2026-03-10T00:00:00+00:00",
        },
        {
            "url": "https://e/2",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": False,
            "language_bucket": "en",
            "skills": ["python"],
            "published_at": "2026-03-11T00:00:00+00:00",
        },
    ]


def _rows_v2() -> list[dict]:
    return [
        *_rows_v1(),
        {
            "url": "https://e/3",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "has_salary": False,
            "has_skills": True,
            "title_is_other": False,
            "language_bucket": "en",
            "skills": ["python"],
            "published_at": "2026-03-12T00:00:00+00:00",
        },
    ]


def test_create_list_enable_disable(tmp_path: Path) -> None:
    db = tmp_path / "saved.db"
    created = create_saved_search(
        db_path=db,
        name="AE search",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "account_executive"}),
    )
    assert created["is_enabled"] is True
    assert created["frequency"] == "daily"

    listed = list_saved_searches(db_path=db)
    assert len(listed) == 1
    sid = listed[0]["search_id"]

    disabled = disable_saved_search(db_path=db, search_id=sid)
    assert disabled["is_enabled"] is False

    enabled = enable_saved_search(db_path=db, search_id=sid)
    assert enabled["is_enabled"] is True


def test_saved_search_lifecycle_archive_restore_and_filters(tmp_path: Path) -> None:
    db = tmp_path / "saved.db"
    s_active = create_saved_search(
        db_path=db,
        name="active one",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "software_engineer"}),
    )
    s_disabled = create_saved_search(
        db_path=db,
        name="disabled one",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "account_executive"}),
        is_enabled=False,
    )
    assert s_active["lifecycle"] == "active"
    assert s_disabled["lifecycle"] == "disabled"

    archived = archive_saved_search(db_path=db, search_id=s_active["search_id"])
    assert archived["lifecycle"] == "archived"
    assert archived["is_enabled"] is False

    restored = restore_saved_search(db_path=db, search_id=s_active["search_id"])
    assert restored["lifecycle"] == "disabled"
    assert restored["is_enabled"] is False

    only_active = list_saved_searches(db_path=db, lifecycle="active")
    only_disabled = list_saved_searches(db_path=db, lifecycle="disabled")
    only_archived = list_saved_searches(db_path=db, lifecycle="archived")
    assert all(x["lifecycle"] == "active" for x in only_active)
    assert any(x["search_id"] == s_active["search_id"] for x in only_disabled)
    assert all(x["lifecycle"] == "disabled" for x in only_disabled)
    assert only_archived == []


def test_run_saved_search_filters_and_pack(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    _write(jobs_jsonl, _rows_v1())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    s_filters = create_saved_search(
        db_path=saved_db,
        name="SE filters",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "software_engineer"}),
    )
    run_filters = run_saved_search(
        db_path=saved_db,
        search_id=s_filters["search_id"],
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        limit=50,
    )
    assert run_filters["run_result"]["total_count"] == 1

    s_pack = create_saved_search(
        db_path=saved_db,
        name="AE pack",
        query_type="pack",
        pack_name="account_executive_jobs",
    )
    run_pack_rep = run_saved_search(
        db_path=saved_db,
        search_id=s_pack["search_id"],
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        limit=50,
    )
    assert run_pack_rep["run_result"]["total_count"] == 1


def test_check_new_matches_delta_detection(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    _write(jobs_jsonl, _rows_v1())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    s = create_saved_search(
        db_path=saved_db,
        name="SE python",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "software_engineer"}),
    )

    first = check_new_matches(
        db_path=saved_db,
        search_id=s["search_id"],
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        scan_limit=1000,
        return_limit=100,
    )
    assert first["current_count"] == 1
    assert first["new_count"] == 1

    second = check_new_matches(
        db_path=saved_db,
        search_id=s["search_id"],
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        scan_limit=1000,
        return_limit=100,
    )
    assert second["new_count"] == 0

    _write(jobs_jsonl, _rows_v2())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)
    third = check_new_matches(
        db_path=saved_db,
        search_id=s["search_id"],
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        scan_limit=1000,
        return_limit=100,
    )
    assert third["current_count"] == 2
    assert third["new_count"] == 1


def test_update_delete_and_seen_cleanup(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    _write(jobs_jsonl, _rows_v1())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    created = create_saved_search(
        db_path=saved_db,
        name="SE",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "software_engineer"}),
    )
    sid = created["search_id"]
    check_new_matches(
        db_path=saved_db,
        search_id=sid,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
    )

    updated = update_saved_search(
        db_path=saved_db,
        search_id=sid,
        name="AE Pack",
        query_type="pack",
        pack_name="account_executive_jobs",
        frequency="manual",
        is_enabled=False,
    )
    assert updated["name"] == "AE Pack"
    assert updated["query_type"] == "pack"
    assert updated["frequency"] == "manual"
    assert updated["filters_json"] is None
    assert updated["pack_name"] == "account_executive_jobs"
    assert updated["is_enabled"] is False
    fetched = get_saved_search(db_path=saved_db, search_id=sid)
    assert fetched["name"] == "AE Pack"

    deleted = delete_saved_search(db_path=saved_db, search_id=sid)
    assert deleted["deleted"] is True
    assert deleted["saved_search"]["search_id"] == sid
    listed = list_saved_searches(db_path=saved_db)
    assert listed == []
    with sqlite3.connect(saved_db) as conn:
        seen_count = conn.execute("SELECT COUNT(*) FROM saved_search_seen WHERE search_id = ?", (sid,)).fetchone()[0]
    assert seen_count == 0


def test_get_saved_search_results_current_and_new_without_mutation(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    jobs_jsonl = tmp_path / "jobs.jsonl"
    jobs_db = tmp_path / "jobs.db"
    _write(jobs_jsonl, _rows_v1())
    build_sqlite_index(input_path=jobs_jsonl, sqlite_path=jobs_db)

    created = create_saved_search(
        db_path=saved_db,
        name="SE",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "software_engineer"}),
    )
    sid = created["search_id"]

    current = get_saved_search_results(
        db_path=saved_db,
        search_id=sid,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        limit=50,
        new_only=False,
    )
    assert current["mode"] == "current"
    assert current["current_count"] == 1
    assert len(current["results"]) == 1

    new_before = get_saved_search_results(
        db_path=saved_db,
        search_id=sid,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        new_only=True,
        scan_limit=1000,
    )
    assert new_before["mode"] == "new_only"
    assert new_before["new_count"] == 1

    check_new_matches(
        db_path=saved_db,
        search_id=sid,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        scan_limit=1000,
        return_limit=100,
    )
    new_after = get_saved_search_results(
        db_path=saved_db,
        search_id=sid,
        indexed_input_path=jobs_jsonl,
        indexed_sqlite_path=jobs_db,
        new_only=True,
        scan_limit=1000,
    )
    assert new_after["new_count"] == 0


def test_saved_searches_service_isolated_by_user_id(tmp_path: Path) -> None:
    saved_db = tmp_path / "saved.db"
    s1 = create_saved_search(
        db_path=saved_db,
        name="u1",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "software_engineer"}),
        user_id="user-1",
        user_email="u1@example.com",
    )
    _ = create_saved_search(
        db_path=saved_db,
        name="u2",
        query_type="filters",
        filters_json=json.dumps({"normalized_title": "account_executive"}),
        user_id="user-2",
        user_email="u2@example.com",
    )

    list_u1 = list_saved_searches(db_path=saved_db, user_id="user-1")
    list_u2 = list_saved_searches(db_path=saved_db, user_id="user-2")
    assert len(list_u1) == 1
    assert len(list_u2) == 1
    assert list_u1[0]["name"] == "u1"
    assert list_u2[0]["name"] == "u2"

    # user-2 cannot fetch user-1 search
    try:
        _ = get_saved_search(db_path=saved_db, search_id=s1["search_id"], user_id="user-2")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "not found" in str(exc)
