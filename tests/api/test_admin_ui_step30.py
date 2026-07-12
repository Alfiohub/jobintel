from __future__ import annotations

import json
from pathlib import Path
import re

from fastapi.testclient import TestClient

from jobintel_next.app.api import create_app
from jobintel_next.product.auth import create_local_user
from jobintel_next.product.saved_searches import create_saved_search


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
            "location_type": "remote",
            "has_salary": True,
            "has_skills": True,
            "title_is_other": False,
            "skills": ["python"],
        },
        {
            "url": "https://e/2",
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "published_at": "2026-03-11T00:00:00+00:00",
            "location_type": "onsite",
            "has_salary": False,
            "title_is_other": True,
        },
    ]


def _client(tmp_path: Path) -> tuple[TestClient, Path, Path, Path]:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    job_state_db = tmp_path / "job_state.db"
    runs_dir = tmp_path / "alerts" / "runs"
    _write(indexed, _rows())
    client = TestClient(
        create_app(
            input_path=indexed,
            saved_db_path=saved_db,
            alert_runs_dir=runs_dir,
            job_state_db_path=job_state_db,
        )
    )
    login = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123", "next": "/admin"},
        follow_redirects=False,
    )
    assert login.status_code == 303
    return client, indexed, saved_db, runs_dir


def test_admin_overview_page_renders(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin")
    assert r.status_code == 200
    assert "Admin Overview" in r.text
    assert "Job Search Funnel" in r.text
    assert "Closed-loop Outcomes" in r.text
    assert "Open opportunities" in r.text
    assert "Saved → Applied" in r.text
    assert "Applied → Interview" in r.text
    assert "New jobs" in r.text
    assert "Saved jobs" in r.text
    assert "Applied" in r.text
    assert "Interview" in r.text
    assert "Rejected" in r.text
    assert "Top Shortlist Items" in r.text
    assert "Saved Searches Needing Attention" in r.text
    assert "Pipeline Needing Attention" in r.text
    assert "Needs Follow-up" in r.text
    assert "Needs Attention" in r.text
    assert "Target Search Profile" in r.text
    assert "Open Today view" in r.text
    assert "/admin/notifications" in r.text
    assert "No shortlist items yet." in r.text
    assert "Due now" in r.text
    assert "Enabled searches" in r.text
    assert "Daily workflow" in r.text
    assert "Weekly maintenance" in r.text


def test_admin_dashboard_funnel_counts_and_attention_update(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    client.post(
        "/admin/shortlist/pipeline",
        data={"job_url": "https://e/1", "state": "interview", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    client.post(
        "/admin/shortlist/details",
        data={
            "job_url": "https://e/1",
            "notes": "",
            "applied_at": "",
            "interview_at": "",
            "follow_up_at": "2020-01-01",
            "follow_up_note": "send follow-up mail",
            "next": "/admin/shortlist",
        },
        follow_redirects=True,
    )

    r = client.get("/admin")
    assert r.status_code == 200
    assert "Needs Follow-up" in r.text
    assert "send follow-up mail" in r.text
    assert "interview without date" in r.text
    assert "saved without notes=0" in r.text
    assert "interview without date=1" in r.text


def test_admin_notifications_page_renders(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin/notifications")
    assert r.status_code == 200
    assert "Notifications / Needs Attention" in r.text
    assert "Signals view." in r.text
    assert "/admin/today" in r.text
    assert "/admin/review" in r.text
    assert "/admin/saved-searches" in r.text


def test_admin_today_page_renders_and_blocks_present(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin/today")
    assert r.status_code == 200
    assert "Today View" in r.text
    assert "Target profile:" in r.text
    assert "High Ranked New Jobs" in r.text
    assert "Follow-up Due / Overdue" in r.text
    assert "Shortlist Items Needing Attention" in r.text
    assert "High Priority Attention" in r.text
    assert "Today = immediate action." in r.text
    assert "/admin/inbox?state=new&sort_by=rank" in r.text
    assert "/admin/shortlist" in r.text
    assert "/admin/notifications" in r.text
    assert "/admin/review" in r.text


def test_admin_today_page_handles_empty_followups_and_shortlist(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin/today")
    assert r.status_code == 200
    assert "No follow-up items due." in r.text
    assert "No shortlist blockers right now." in r.text


def test_admin_review_page_renders_and_empty_states(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin/review")
    assert r.status_code == 200
    assert "Daily / Weekly Review" in r.text
    assert "Weekly maintenance focus." in r.text
    assert "Saved Jobs Stale" in r.text
    assert "Applied Jobs Without Recent Update" in r.text
    assert "Interview Items Missing Notes/Date" in r.text
    assert "Saved Searches with No Recent New Matches" in r.text
    assert "High Dismiss-Rate Searches Needing Cleanup" in r.text
    assert "No stale saved jobs right now." in r.text
    assert "No applied jobs currently blocked." in r.text
    assert "No interview items missing context." in r.text
    assert "/admin/shortlist" in r.text
    assert "/admin/saved-searches" in r.text
    assert "/admin/saved-searches?lifecycle=active" in r.text
    assert "/admin/saved-searches?lifecycle=archived" in r.text


def test_admin_review_page_shows_interview_gap_item(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    client.post(
        "/admin/shortlist/pipeline",
        data={"job_url": "https://e/1", "state": "interview", "next": "/admin/shortlist"},
        follow_redirects=True,
    )

    r = client.get("/admin/review")
    assert r.status_code == 200
    assert "missing interview notes" in r.text
    assert "/admin/shortlist?pipeline_state=interview" in r.text


def test_admin_templates_page_crud_and_shortlist_template_selection(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r0 = client.get("/admin/templates")
    assert r0.status_code == 200
    assert "Reusable Application Templates" in r0.text
    assert "Create template" in r0.text

    r_new = client.post(
        "/admin/templates/new",
        data={"kind": "resume", "label": "CV backend v2", "description": "backend cv", "is_active": "true"},
        follow_redirects=True,
    )
    assert r_new.status_code == 200
    assert "Template created" in r_new.text
    assert "CV backend v2" in r_new.text

    # Disable from templates page
    m = re.search(r"/admin/templates/([0-9a-f-]+)/disable", r_new.text)
    assert m is not None
    template_id = str(m.group(1))
    r_dis = client.post(f"/admin/templates/{template_id}/disable", follow_redirects=True)
    assert r_dis.status_code == 200
    assert "Template disabled" in r_dis.text

    # Re-enable and use it in shortlist details via select fallback.
    r_en = client.post(f"/admin/templates/{template_id}/enable", follow_redirects=True)
    assert r_en.status_code == 200
    assert "Template enabled" in r_en.text

    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    r_short = client.get("/admin/shortlist")
    assert r_short.status_code == 200
    assert "resume_template_label" in r_short.text
    assert "CV backend v2" in r_short.text

    r_upd = client.post(
        "/admin/shortlist/details",
        data={
            "job_url": "https://e/1",
            "notes": "",
            "applied_at": "",
            "interview_at": "",
            "follow_up_at": "",
            "follow_up_note": "",
            "application_channel": "",
            "contact_name": "",
            "contact_email": "",
            "external_application_url": "",
            "compensation_note": "",
            "resume_template_label": "CV backend v2",
            "resume_label": "",
            "cover_letter_template_label": "",
            "cover_letter_label": "",
            "submission_note": "",
            "next": "/admin/shortlist",
        },
        follow_redirects=True,
    )
    assert r_upd.status_code == 200
    assert "resume: CV backend v2" in r_upd.text

    r_del = client.post(f"/admin/templates/{template_id}/delete", follow_redirects=True)
    assert r_del.status_code == 200
    assert "Template deleted" in r_del.text


def test_admin_inbox_page_renders(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin/inbox")
    assert r.status_code == 200
    assert "Job Inbox" in r.text
    assert "Rank" in r.text
    assert "Filtered" in r.text
    assert "badge-state-new" in r.text
    assert "Apply filters" in r.text


def test_admin_saved_searches_list_renders(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    sid = saved["search_id"]
    r = client.get("/admin/saved-searches")
    assert r.status_code == 200
    assert "Saved Searches" in r.text
    assert "software eng" in r.text
    assert "daily" in r.text
    assert "due now" in r.text
    assert "Open" in r.text
    assert f"/admin/saved-searches/{sid}" in r.text
    assert "Saved Marks" in r.text
    assert "Dismissed Marks" in r.text
    assert "Saved %" in r.text
    assert "Dismiss %" in r.text
    assert "Quality" in r.text
    assert "Search Portfolio / Strategy" in r.text
    assert "Strategy" in r.text
    assert "Search Hygiene" in r.text
    assert "Lifecycle" in r.text
    assert "active" in r.text
    assert "Search operations model:" in r.text
    assert "/admin/today" in r.text
    assert "/admin/review" in r.text
    assert "/admin/notifications" in r.text


def test_admin_create_saved_search_via_form(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.post(
        "/admin/saved-searches/new",
        data={
            "name": "python jobs",
            "query_type": "filters",
            "filters_json": '{"skills_contains":["python"]}',
            "frequency": "twice_daily",
            "is_enabled": "on",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert "Saved search created" in r.text
    assert "python jobs" in r.text
    assert "twice_daily" in r.text


def test_admin_saved_search_new_shows_target_suggestions_and_prefill(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/account",
        data={
            "email": "admin@example.com",
            "default_alert_email": "",
            "include_dismissed_default": "on",
            "target_titles": "backend engineer",
            "target_role_families": "software_engineering",
            "preferred_location_types": "remote",
            "salary_target_note": "",
            "keywords_note": "python, fastapi",
        },
        follow_redirects=True,
    )

    r = client.get("/admin/saved-searches/new")
    assert r.status_code == 200
    assert "Target-aligned helpers" in r.text
    assert "Quick suggestions" in r.text
    assert "Target profile baseline" in r.text
    assert "Use target profile" in r.text

    r_prefill = client.get("/admin/saved-searches/new?use_target_profile=true")
    assert r_prefill.status_code == 200
    assert "role_family" in r_prefill.text
    assert "software_engineering" in r_prefill.text
    assert "location_type" in r_prefill.text
    assert "remote" in r_prefill.text
    assert "title_is_other" in r_prefill.text


def test_admin_saved_search_new_handles_empty_profile(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin/saved-searches/new")
    assert r.status_code == 200
    assert "Target-aligned helpers" in r.text
    assert "No target profile suggestions yet." in r.text


def test_admin_saved_searches_list_shows_target_alignment_and_coverage_gap(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    client.post(
        "/admin/account",
        data={
            "email": "admin@example.com",
            "default_alert_email": "",
            "include_dismissed_default": "on",
            "target_titles": "",
            "target_role_families": "data_engineering",
            "preferred_location_types": "remote",
            "salary_target_note": "",
            "keywords_note": "",
        },
        follow_redirects=True,
    )
    create_saved_search(
        db_path=saved_db,
        name="se search",
        query_type="filters",
        filters_json='{"role_family":"software_engineering","location_type":"onsite"}',
    )
    r = client.get("/admin/saved-searches")
    assert r.status_code == 200
    assert "Target Coverage" in r.text
    assert "Coverage gaps needing action" in r.text
    assert "data_engineering" in r.text
    assert "role_family" in r.text
    assert "Create search for missing target" in r.text
    assert "Target+role%3A+data_engineering" in r.text
    assert "Target Alignment" in r.text
    assert "missing alignment" in r.text


def test_admin_saved_searches_coverage_empty_profile_state(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin/saved-searches")
    assert r.status_code == 200
    assert "Target Coverage" in r.text
    assert "Search Portfolio / Strategy" in r.text
    assert "Target profile is empty." in r.text
    assert "Set target profile" in r.text


def test_admin_saved_searches_portfolio_categories_and_insights(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    client.post(
        "/admin/account",
        data={
            "email": "admin@example.com",
            "default_alert_email": "",
            "include_dismissed_default": "on",
            "target_titles": "software engineer",
            "target_role_families": "software_engineering",
            "preferred_location_types": "remote",
            "salary_target_note": "",
            "keywords_note": "",
        },
        follow_redirects=True,
    )
    create_saved_search(
        db_path=saved_db,
        name="broad",
        query_type="filters",
        filters_json='{"title_is_other":false}',
        is_enabled=True,
    )
    create_saved_search(
        db_path=saved_db,
        name="target",
        query_type="filters",
        filters_json='{"role_family":"software_engineering","location_type":"remote","title_is_other":false}',
        is_enabled=True,
    )
    create_saved_search(
        db_path=saved_db,
        name="location",
        query_type="filters",
        filters_json='{"location_type":"remote","title_is_other":false}',
        is_enabled=True,
    )
    create_saved_search(
        db_path=saved_db,
        name="pack review",
        query_type="pack",
        pack_name="high_confidence_tech_jobs",
        is_enabled=True,
    )

    r = client.get("/admin/saved-searches")
    assert r.status_code == 200
    assert "Search Portfolio / Strategy" in r.text
    assert "Portfolio insights" in r.text
    assert "broad discovery" in r.text
    assert "target-aligned" in r.text
    assert "location-focused" in r.text
    assert "manual/pack review" in r.text


def test_admin_saved_searches_hygiene_detects_duplicates_overlap_and_allows_disable(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    s_dup_a = create_saved_search(
        db_path=saved_db,
        name="dup a",
        query_type="filters",
        filters_json='{"role_family":"software_engineering","location_type":"remote","title_is_other":false}',
        is_enabled=True,
    )
    s_dup_b = create_saved_search(
        db_path=saved_db,
        name="dup b",
        query_type="filters",
        filters_json='{"role_family":"software_engineering","location_type":"remote","title_is_other":false}',
        is_enabled=True,
    )
    s_overlap = create_saved_search(
        db_path=saved_db,
        name="overlap role",
        query_type="filters",
        filters_json='{"role_family":"software_engineering","title_is_other":false}',
        is_enabled=True,
    )

    # Build history + dismiss signal for low-yield/noisy detection.
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "dismissed", "next": "/admin/inbox"},
        follow_redirects=True,
    )
    client.post("/admin/alerts/run-all", follow_redirects=True)
    client.post("/admin/alerts/run-all", follow_redirects=True)

    r = client.get("/admin/saved-searches")
    assert r.status_code == 200
    assert "Search Hygiene" in r.text
    assert "duplicate" in r.text
    assert "overlap" in r.text
    assert "stale" in r.text or "noisy" in r.text or "low_yield" in r.text
    assert "Candidate disable/review" in r.text
    assert f"/admin/saved-searches/{s_dup_a['search_id']}/disable" in r.text
    assert f"/admin/saved-searches/{s_dup_b['search_id']}/disable" in r.text
    assert f"/admin/saved-searches/{s_overlap['search_id']}" in r.text

    r_dis = client.post(f"/admin/saved-searches/{s_dup_b['search_id']}/disable", follow_redirects=True)
    assert r_dis.status_code == 200
    assert "Saved search disabled" in r_dis.text


def test_admin_enable_disable_actions(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="toggle me",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        is_enabled=True,
    )
    sid = saved["search_id"]
    r1 = client.post(f"/admin/saved-searches/{sid}/disable", follow_redirects=True)
    assert r1.status_code == 200
    assert "Saved search disabled" in r1.text
    r2 = client.post(f"/admin/saved-searches/{sid}/enable", follow_redirects=True)
    assert r2.status_code == 200
    assert "Saved search enabled" in r2.text


def test_admin_saved_search_archive_restore_and_lifecycle_filters(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="lifecycle me",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        is_enabled=True,
    )
    sid = saved["search_id"]

    r_arch = client.post(f"/admin/saved-searches/{sid}/archive", follow_redirects=True)
    assert r_arch.status_code == 200
    assert "Saved search archived" in r_arch.text
    assert "archived" in r_arch.text

    r_archived = client.get("/admin/saved-searches?lifecycle=archived")
    assert r_archived.status_code == 200
    assert "lifecycle me" in r_archived.text
    assert f"/admin/saved-searches/{sid}/restore" in r_archived.text

    r_restore = client.post(f"/admin/saved-searches/{sid}/restore", follow_redirects=True)
    assert r_restore.status_code == 200
    assert "Saved search restored as disabled (enable it when ready)" in r_restore.text

    r_disabled = client.get("/admin/saved-searches?lifecycle=disabled")
    assert r_disabled.status_code == 200
    assert "lifecycle me" in r_disabled.text
    assert "disabled" in r_disabled.text


def test_admin_saved_search_actions_keep_lifecycle_filter_context(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="keep filter",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        is_enabled=True,
    )
    sid = saved["search_id"]

    r_disable = client.post(
        f"/admin/saved-searches/{sid}/disable",
        headers={"referer": "http://testserver/admin/saved-searches?lifecycle=active"},
        follow_redirects=False,
    )
    assert r_disable.status_code == 303
    assert r_disable.headers["location"].startswith("/admin/saved-searches?lifecycle=active")

    # Simulate archive + restore flow from archived view.
    client.post(f"/admin/saved-searches/{sid}/archive", follow_redirects=True)
    r_restore = client.post(
        f"/admin/saved-searches/{sid}/restore",
        headers={"referer": "http://testserver/admin/saved-searches?lifecycle=archived"},
        follow_redirects=False,
    )
    assert r_restore.status_code == 303
    assert r_restore.headers["location"].startswith("/admin/saved-searches?lifecycle=archived")


def test_admin_edit_page_render_and_save(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="edit me",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    sid = saved["search_id"]

    r_get = client.get(f"/admin/saved-searches/{sid}/edit")
    assert r_get.status_code == 200
    assert "Edit Saved Search" in r_get.text
    assert "edit me" in r_get.text

    r_post = client.post(
        f"/admin/saved-searches/{sid}/edit",
        data={
            "name": "edited name",
            "query_type": "pack",
            "filters_json": "",
            "pack_name": "account_executive_jobs",
            "frequency": "manual",
            "is_enabled": "on",
        },
        follow_redirects=True,
    )
    assert r_post.status_code == 200
    assert "Saved search updated" in r_post.text
    assert "edited name" in r_post.text
    assert "manual" in r_post.text


def test_admin_saved_search_detail_page_and_state_actions(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="detail me",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    sid = saved["search_id"]

    r_get = client.get(f"/admin/saved-searches/{sid}")
    assert r_get.status_code == 200
    assert "Saved Search: detail me" in r_get.text
    assert "Current count" in r_get.text
    assert "Rank" in r_get.text
    assert "Quality snapshot" in r_get.text
    assert "Saved marked" in r_get.text
    assert "Dismissed marked" in r_get.text
    assert "Due status" in r_get.text
    assert "New matches only" in r_get.text
    assert "freq: daily" in r_get.text
    assert "badge-state-new" in r_get.text
    assert "https://e/1" in r_get.text

    r_save = client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": f"/admin/saved-searches/{sid}"},
        follow_redirects=True,
    )
    assert r_save.status_code == 200
    assert "Job state updated: saved" in r_save.text
    assert ">saved<" in r_save.text

    r_reset = client.post(
        "/admin/jobs/state/clear",
        data={"job_url": "https://e/1", "next": f"/admin/saved-searches/{sid}"},
        follow_redirects=True,
    )
    assert r_reset.status_code == 200
    assert "Job state reset to new" in r_reset.text
    assert ">new<" in r_reset.text


def test_admin_saved_search_detail_shows_last_run_and_due_status(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="detail run status",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    sid = saved["search_id"]
    rr = client.post(f"/admin/saved-searches/{sid}/run", follow_redirects=True)
    assert rr.status_code == 200

    r = client.get(f"/admin/saved-searches/{sid}")
    assert r.status_code == 200
    assert "Due status" in r.text
    assert "not due" in r.text
    assert "Last run" in r.text


def test_admin_saved_search_detail_new_mode(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="new mode",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    sid = saved["search_id"]
    r = client.get(f"/admin/saved-searches/{sid}?mode=new&scan_limit=100")
    assert r.status_code == 200
    assert "new matches only" in r.text


def test_admin_delete_action(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    saved = create_saved_search(
        db_path=saved_db,
        name="delete me",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    sid = saved["search_id"]
    r = client.post(f"/admin/saved-searches/{sid}/delete", follow_redirects=True)
    assert r.status_code == 200
    assert "Saved search deleted" in r.text
    assert "delete me" not in r.text


def test_admin_run_all_action(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    r = client.post("/admin/alerts/run-all", follow_redirects=False)
    assert r.status_code == 303
    location = r.headers["location"]
    assert location.startswith("/admin/alerts/")
    rd = client.get(location)
    assert rd.status_code == 200
    assert "Alert Run" in rd.text


def test_admin_run_all_send_email_without_recipient_shows_actionable_message(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    r = client.post("/admin/alerts/run-all", data={"send_email": "on", "email_to": ""}, follow_redirects=True)
    assert r.status_code == 200
    assert "Run completed:" in r.text
    assert "Digest email skipped" in r.text
    assert "set default alert email in Account" in r.text


def test_admin_alert_detail_page(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    rr = client.post("/alerts/run-all")
    run_id = rr.json()["run_id"]

    r = client.get(f"/admin/alerts/{run_id}")
    assert r.status_code == 200
    assert f"Alert Run {run_id}" in r.text
    assert "software eng" in r.text
    assert "Open inbox" in r.text
    assert "badge-state-new" in r.text


def test_admin_alert_detail_renders_digest_delivery_metadata(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    rr = client.post("/alerts/run-all")
    payload = rr.json()
    run_id = payload["run_id"]
    run_json = Path(payload["json_report_path"])
    obj = json.loads(run_json.read_text(encoding="utf-8"))
    obj["digest_delivery"] = {
        "to_email": "digest@example.com",
        "attempted_count": 1,
        "sent_count": 1,
        "skipped_count": 0,
        "error_count": 0,
        "email_sent": True,
        "email_error": False,
    }
    run_json.write_text(json.dumps(obj), encoding="utf-8")

    r = client.get(f"/admin/alerts/{run_id}")
    assert r.status_code == 200
    assert "Digest delivery" in r.text
    assert "digest@example.com" in r.text


def test_admin_job_state_actions_from_alert_detail(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    rr = client.post("/alerts/run-all")
    run_id = rr.json()["run_id"]

    r0 = client.get(f"/admin/alerts/{run_id}")
    assert r0.status_code == 200
    assert "Current State" in r0.text
    assert "Sample new matches" in r0.text
    assert "badge-state-new" in r0.text

    r1 = client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": f"/admin/alerts/{run_id}"},
        follow_redirects=True,
    )
    assert r1.status_code == 200
    assert "Job state updated: saved" in r1.text
    assert ">saved<" in r1.text

    r2 = client.post(
        "/admin/jobs/state/clear",
        data={"job_url": "https://e/1", "next": f"/admin/alerts/{run_id}"},
        follow_redirects=True,
    )
    assert r2.status_code == 200
    assert "Job state reset to new" in r2.text
    assert ">new<" in r2.text


def test_admin_inbox_state_actions(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)

    r0 = client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/inbox?state=saved"},
        follow_redirects=True,
    )
    assert r0.status_code == 200
    assert "Job state updated: saved" in r0.text
    assert "https://e/1" in r0.text

    r1 = client.post(
        "/admin/jobs/state/clear",
        data={"job_url": "https://e/1", "next": "/admin/inbox?state=new"},
        follow_redirects=True,
    )
    assert r1.status_code == 200
    assert "Job state reset to new" in r1.text
    assert "https://e/1" in r1.text


def test_admin_first_run_empty_states_and_cta(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)

    r_home = client.get("/admin")
    assert r_home.status_code == 200
    assert "Getting Started" in r_home.text
    assert "Checklist progress:" in r_home.text
    assert "0/4" in r_home.text
    assert "Create your first saved search" in r_home.text
    assert "Set a default alert email in Account" in r_home.text
    assert "Run alerts to generate your first run" in r_home.text
    assert "Review your inbox and mark at least one job" in r_home.text

    r_saved = client.get("/admin/saved-searches")
    assert r_saved.status_code == 200
    assert "No saved searches yet." in r_saved.text
    assert "Create your first saved search" in r_saved.text

    r_alerts = client.get("/admin/alerts")
    assert r_alerts.status_code == 200
    assert "No alert runs yet." in r_alerts.text
    assert "Set a default alert email" in r_alerts.text

    r_inbox = client.get("/admin/inbox?state=saved")
    assert r_inbox.status_code == 200
    assert "Inbox is empty." in r_inbox.text
    assert "You do not have saved searches yet." in r_inbox.text


def test_admin_onboarding_checklist_updates_after_minimal_flow(tmp_path: Path) -> None:
    client, _, saved_db, _ = _client(tmp_path)
    create_saved_search(
        db_path=saved_db,
        name="first search",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )
    client.post(
        "/admin/account",
        data={
            "email": "admin@example.com",
            "default_alert_email": "alerts@example.com",
            "include_dismissed_default": "on",
        },
        follow_redirects=True,
    )
    client.post("/admin/alerts/run-all", follow_redirects=True)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "seen", "next": "/admin/inbox"},
        follow_redirects=True,
    )

    r_home = client.get("/admin")
    assert r_home.status_code == 200
    assert "Checklist progress:" in r_home.text
    assert "4/4" in r_home.text

    r_saved = client.get("/admin/saved-searches")
    assert r_saved.status_code == 200
    assert "No saved searches yet." not in r_saved.text


def test_admin_inbox_sort_and_quick_filters(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)

    r_rank = client.get("/admin/inbox?sort_by=rank&state=all")
    assert r_rank.status_code == 200
    assert "Why ranked" in r_rank.text
    assert "skills signal" in r_rank.text or "salary signal" in r_rank.text

    r_filtered = client.get(
        "/admin/inbox?state=all&sort_by=rank&only_remote=true&only_salary=true&exclude_other=true"
    )
    assert r_filtered.status_code == 200
    assert "https://e/1" in r_filtered.text
    assert "https://e/2" not in r_filtered.text


def test_admin_saved_view_newest_ordering_is_useful_for_triage(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/inbox?state=saved"},
        follow_redirects=True,
    )
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/2", "state": "saved", "next": "/admin/inbox?state=saved"},
        follow_redirects=True,
    )

    r = client.get("/admin/inbox?state=saved&sort_by=newest")
    assert r.status_code == 200
    assert "https://e/1" in r.text and "https://e/2" in r.text
    # e/2 is newer than e/1 in fixture dates.
    assert r.text.index("https://e/2") < r.text.index("https://e/1")


def test_admin_overview_shows_top_ranked_new_jobs_section(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    r = client.get("/admin")
    assert r.status_code == 200
    assert "Top Ranked New Jobs" in r.text
    assert "/admin/shortlist" in r.text


def test_admin_shortlist_render_and_only_saved_jobs(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/2", "state": "dismissed", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    r = client.get("/admin/shortlist")
    assert r.status_code == 200
    assert "Saved Jobs Shortlist" in r.text
    assert "Target profile:" in r.text
    assert "https://e/1" in r.text
    assert "https://e/2" not in r.text
    assert "Pipeline state" in r.text
    assert "Outcome Summary" in r.text
    assert "Interview → Rejected" in r.text
    assert "Applied" in r.text
    assert "Interview" in r.text
    assert "Rejected" in r.text
    assert "Reset Pipeline" in r.text
    assert "Notes / Timeline" in r.text
    assert "Save details" in r.text
    assert "Clear details" in r.text
    assert "Only follow-up set" in r.text
    assert "Only follow-up due" in r.text
    assert "Sort" in r.text
    assert "role_family" in r.text
    assert "Export CSV" in r.text
    assert "/admin/exports/shortlist.csv" in r.text


def test_admin_shortlist_export_csv_is_per_user_and_contains_expected_fields(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    job_state_db = tmp_path / "job_state.db"
    runs_dir = tmp_path / "alerts" / "runs"
    _write(indexed, _rows())
    app = create_app(
        input_path=indexed,
        saved_db_path=saved_db,
        alert_runs_dir=runs_dir,
        job_state_db_path=job_state_db,
    )
    create_local_user(db_path=saved_db, email="user2@example.com", password="user2pass", user_id="user-2")

    c1 = TestClient(app)
    c2 = TestClient(app)
    l1 = c1.post("/login", data={"email": "admin@example.com", "password": "admin123", "next": "/admin"}, follow_redirects=False)
    l2 = c2.post("/login", data={"email": "user2@example.com", "password": "user2pass", "next": "/admin"}, follow_redirects=False)
    assert l1.status_code == 303
    assert l2.status_code == 303

    c1.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    c1.post(
        "/admin/shortlist/details",
        data={
            "job_url": "https://e/1",
            "notes": "strong fit",
            "applied_at": "2026-04-01",
            "interview_at": "",
            "follow_up_at": "2026-04-04",
            "follow_up_note": "follow up soon",
            "application_channel": "linkedin",
            "contact_name": "Alice Recruiter",
            "contact_email": "alice@example.com",
            "compensation_note": "target 70k",
            "external_application_url": "https://apply.example.com/1",
            "resume_label": "CV backend v2",
            "cover_letter_label": "CL generic data role",
            "submission_note": "submitted via company site with custom answers",
            "next": "/admin/shortlist",
        },
        follow_redirects=True,
    )

    c2.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/2", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )

    r1 = c1.get("/admin/exports/shortlist.csv")
    assert r1.status_code == 200
    assert "text/csv" in r1.headers.get("content-type", "")
    assert "attachment;" in r1.headers.get("content-disposition", "")
    assert "application_channel" in r1.text
    assert "resume_label" in r1.text
    assert "cover_letter_label" in r1.text
    assert "submission_note" in r1.text
    assert "contact_name" in r1.text
    assert "external_application_url" in r1.text
    assert "https://e/1" in r1.text
    assert "https://e/2" not in r1.text
    assert "Alice Recruiter" in r1.text
    assert "linkedin" in r1.text
    assert "CV backend v2" in r1.text
    assert "CL generic data role" in r1.text
    assert "custom answers" in r1.text

    r2 = c2.get("/admin/exports/shortlist.csv")
    assert r2.status_code == 200
    assert "https://e/2" in r2.text
    assert "https://e/1" not in r2.text


def test_admin_shortlist_filters_and_newest_sort(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/2", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )

    r1 = client.get("/admin/shortlist?only_remote=true&only_salary=true&exclude_other=true")
    assert r1.status_code == 200
    assert "https://e/1" in r1.text
    assert "https://e/2" not in r1.text

    r2 = client.get("/admin/shortlist?sort_by=newest")
    assert r2.status_code == 200
    assert "https://e/1" in r2.text and "https://e/2" in r2.text
    assert r2.text.index("https://e/2") < r2.text.index("https://e/1")


def test_admin_shortlist_actions_work(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )

    r_seen = client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "seen", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    assert r_seen.status_code == 200
    assert "Job state updated: seen" in r_seen.text
    assert "https://e/1" not in r_seen.text

    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    r_dismiss = client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "dismissed", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    assert r_dismiss.status_code == 200
    assert "Job state updated: dismissed" in r_dismiss.text
    assert "https://e/1" not in r_dismiss.text


def test_admin_shortlist_pipeline_filter_and_actions(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/2", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    client.post(
        "/admin/shortlist/pipeline",
        data={"job_url": "https://e/1", "state": "applied", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    client.post(
        "/admin/shortlist/pipeline",
        data={"job_url": "https://e/2", "state": "rejected", "next": "/admin/shortlist"},
        follow_redirects=True,
    )

    r_applied = client.get("/admin/shortlist?pipeline_state=applied")
    assert r_applied.status_code == 200
    assert "https://e/1" in r_applied.text
    assert "https://e/2" not in r_applied.text

    r_reset = client.post(
        "/admin/shortlist/pipeline/clear",
        data={"job_url": "https://e/1", "next": "/admin/shortlist?pipeline_state=saved"},
        follow_redirects=True,
    )
    assert r_reset.status_code == 200
    assert "Pipeline reset to saved" in r_reset.text
    assert "https://e/1" in r_reset.text


def test_admin_shortlist_details_update_and_clear(tmp_path: Path) -> None:
    client, _, _, _ = _client(tmp_path)
    client.post(
        "/admin/jobs/state",
        data={"job_url": "https://e/1", "state": "saved", "next": "/admin/shortlist"},
        follow_redirects=True,
    )

    r_upd = client.post(
        "/admin/shortlist/details",
        data={
            "job_url": "https://e/1",
            "notes": "Reached out to recruiter",
            "applied_at": "2026-04-01",
            "interview_at": "2026-04-05",
            "follow_up_at": "2020-01-01",
            "follow_up_note": "follow tomorrow",
            "application_channel": "linkedin",
            "contact_name": "Alice Recruiter",
            "contact_email": "alice@example.com",
            "external_application_url": "https://apply.example.com/123",
            "compensation_note": "target 70k",
            "resume_label": "CV backend v2",
            "cover_letter_label": "CL generic data role",
            "submission_note": "submitted through company site",
            "next": "/admin/shortlist",
        },
        follow_redirects=True,
    )
    assert r_upd.status_code == 200
    assert "Application details updated" in r_upd.text
    assert "Reached out to recruiter" in r_upd.text
    assert "applied: 2026-04-01" in r_upd.text
    assert "interview: 2026-04-05" in r_upd.text
    assert "follow-up: 2020-01-01" in r_upd.text
    assert "follow tomorrow" in r_upd.text
    assert "channel: linkedin" in r_upd.text
    assert "Alice Recruiter" in r_upd.text
    assert "alice@example.com" in r_upd.text
    assert "external application link" in r_upd.text
    assert "target 70k" in r_upd.text
    assert "resume: CV backend v2" in r_upd.text
    assert "cover letter: CL generic data role" in r_upd.text
    assert "submitted through company site" in r_upd.text
    assert "overdue" in r_upd.text

    r_due = client.get("/admin/shortlist?only_follow_up_due=true")
    assert r_due.status_code == 200
    assert "https://e/1" in r_due.text

    r_set = client.get("/admin/shortlist?only_follow_up_set=true")
    assert r_set.status_code == 200
    assert "https://e/1" in r_set.text

    r_clear = client.post(
        "/admin/shortlist/details/clear",
        data={"job_url": "https://e/1", "next": "/admin/shortlist"},
        follow_redirects=True,
    )
    assert r_clear.status_code == 200
    assert "Application details cleared" in r_clear.text
    assert "Reached out to recruiter" not in r_clear.text
    assert "Alice Recruiter" not in r_clear.text
    assert "resume: CV backend v2" not in r_clear.text
