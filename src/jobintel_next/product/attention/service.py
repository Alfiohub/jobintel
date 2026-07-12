from __future__ import annotations

from typing import Any

from jobintel_next.product.alerts import get_alert_run_detail, list_alert_runs
from jobintel_next.product.application_tracking import list_follow_up_items
from jobintel_next.product.auth import get_user_settings
from jobintel_next.product.saved_searches import (
    build_saved_search_insights_map,
    is_saved_search_due,
    list_saved_searches,
)


def build_attention_items_for_user(
    *,
    saved_db_path: str,
    job_state_db_path: str,
    runs_dir: str,
    indexed_input_path: str,
    indexed_sqlite_path: str | None,
    user_id: str,
    max_items: int = 12,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    prefs = {
        "show_follow_up_attention": True,
        "show_due_saved_search_attention": True,
        "show_saved_search_quality_attention": True,
        "show_digest_error_attention": True,
    }
    try:
        settings = get_user_settings(db_path=saved_db_path, user_id=user_id)
        prefs.update(
            {
                "show_follow_up_attention": bool(settings.get("show_follow_up_attention", True)),
                "show_due_saved_search_attention": bool(settings.get("show_due_saved_search_attention", True)),
                "show_saved_search_quality_attention": bool(settings.get("show_saved_search_quality_attention", True)),
                "show_digest_error_attention": bool(settings.get("show_digest_error_attention", True)),
            }
        )
    except Exception:
        pass

    # 1) Follow-up due/overdue (highest ROI)
    if prefs["show_follow_up_attention"]:
        follow_ups = list_follow_up_items(db_path=job_state_db_path, user_id=user_id, limit=50)
        for f in follow_ups:
            status = str(f.get("follow_up_status") or "")
            if status not in {"due", "overdue"}:
                continue
            job_url = str(f.get("job_url") or "")
            label = "Follow-up overdue" if status == "overdue" else "Follow-up due soon"
            priority = "high" if status == "overdue" else "medium"
            items.append(
                {
                    "type": "follow_up",
                    "title": f"{label}: {job_url}",
                    "priority": priority,
                    "href": "/admin/shortlist?only_follow_up_due=true",
                    "meta": {
                        "job_url": job_url,
                        "follow_up_at": str(f.get("follow_up_at") or ""),
                        "follow_up_note": str(f.get("follow_up_note") or ""),
                    },
                }
            )

    # 2) Saved searches due now
    saved = list_saved_searches(db_path=saved_db_path, user_id=user_id)
    if prefs["show_due_saved_search_attention"]:
        for s in saved:
            if not is_saved_search_due(s):
                continue
            sid = str(s.get("search_id") or "")
            name = str(s.get("name") or sid)
            items.append(
                {
                    "type": "saved_search_due",
                    "title": f"Saved search due now: {name}",
                    "priority": "medium",
                    "href": f"/admin/saved-searches/{sid}",
                    "meta": {"search_id": sid},
                }
            )

    # 3) Saved searches quality flags
    try:
        search_ids = [str(s.get("search_id") or "") for s in saved if str(s.get("search_id") or "")]
        insights = build_saved_search_insights_map(
            db_path=saved_db_path,
            job_state_db_path=job_state_db_path,
            search_ids=search_ids,
            indexed_input_path=indexed_input_path,
            indexed_sqlite_path=indexed_sqlite_path,
            user_id=user_id,
            latest_new_by_search={},
            scan_limit=150,
        )
        by_id = {str(s.get("search_id") or ""): s for s in saved}
        for sid, insight in insights.items():
            flags = [str(x) for x in (insight.get("quality_flags") or []) if str(x).strip()]
            if not flags:
                continue
            if not prefs["show_saved_search_quality_attention"]:
                continue
            name = str(by_id.get(sid, {}).get("name") or sid)
            priority = "high" if "high dismiss rate" in flags else "low"
            items.append(
                {
                    "type": "saved_search_quality",
                    "title": f"Search needs tuning: {name} ({', '.join(flags[:2])})",
                    "priority": priority,
                    "href": f"/admin/saved-searches/{sid}",
                    "meta": {"search_id": sid, "flags": flags[:3]},
                }
            )
    except Exception:
        pass

    # 4) Latest digest error
    runs = list_alert_runs(runs_dir=runs_dir, user_id=user_id)
    if runs and prefs["show_digest_error_attention"]:
        rid = str(runs[0].get("run_id") or "")
        if rid:
            try:
                detail = get_alert_run_detail(runs_dir=runs_dir, run_id=rid, user_id=user_id)
                digest = detail.get("digest_delivery")
                if isinstance(digest, dict) and bool(digest.get("email_error")):
                    items.append(
                        {
                            "type": "digest_error",
                            "title": f"Latest digest delivery failed (run {rid})",
                            "priority": "high",
                            "href": f"/admin/alerts/{rid}",
                            "meta": {"run_id": rid},
                        }
                    )
            except Exception:
                pass

    priority_order = {"high": 0, "medium": 1, "low": 2}
    items = sorted(items, key=lambda x: (priority_order.get(str(x.get("priority") or "low"), 3), str(x.get("title") or "")))
    return items[: max(1, int(max_items))]
