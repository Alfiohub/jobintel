from __future__ import annotations

from typing import Any

from jobintel_next.product.job_state import get_many_job_states

from .service import get_saved_search_results


def build_saved_search_insight(
    *,
    db_path: str,
    job_state_db_path: str,
    search_id: str,
    indexed_input_path: str,
    indexed_sqlite_path: str | None,
    user_id: str,
    latest_new_count: int | None = None,
    scan_limit: int = 500,
) -> dict[str, Any]:
    rep = get_saved_search_results(
        db_path=db_path,
        search_id=search_id,
        indexed_input_path=indexed_input_path,
        indexed_sqlite_path=indexed_sqlite_path,
        limit=scan_limit,
        offset=0,
        new_only=False,
        user_id=user_id,
    )
    rows = [dict(r) for r in rep.get("results", []) if isinstance(r, dict)]
    urls = [str(r.get("url") or "") for r in rows if str(r.get("url") or "")]
    states = get_many_job_states(
        db_path=job_state_db_path,
        job_urls=urls,
        user_id=user_id,
    )

    saved_marks = 0
    dismissed_marks = 0
    for u in urls:
        st = states.get(u, "new")
        if st == "saved":
            saved_marks += 1
        elif st == "dismissed":
            dismissed_marks += 1

    scanned_count = len(urls)
    current_count = int(rep.get("current_count") or scanned_count)
    latest_new = int(latest_new_count or 0) if latest_new_count is not None else None

    base = scanned_count if scanned_count > 0 else 0
    saved_rate = (saved_marks / base) if base else 0.0
    dismiss_rate = (dismissed_marks / base) if base else 0.0

    quality_flags: list[str] = []
    if scanned_count >= 5 and dismiss_rate >= 0.6:
        quality_flags.append("high dismiss rate")
    if latest_new is not None and latest_new == 0 and str(rep.get("saved_search", {}).get("last_run_at") or ""):
        quality_flags.append("no recent new matches")
    if scanned_count == 0:
        quality_flags.append("no current matches")

    return {
        "search_id": search_id,
        "current_count": current_count,
        "latest_new_count": latest_new,
        "saved_marked_count": saved_marks,
        "dismissed_marked_count": dismissed_marks,
        "saved_rate": round(saved_rate, 3),
        "dismiss_rate": round(dismiss_rate, 3),
        "last_run_at": rep.get("saved_search", {}).get("last_run_at"),
        "scanned_count": scanned_count,
        "scan_limit": scan_limit,
        "is_partial_sample": current_count > scanned_count,
        "quality_flags": quality_flags,
    }


def build_saved_search_insights_map(
    *,
    db_path: str,
    job_state_db_path: str,
    search_ids: list[str],
    indexed_input_path: str,
    indexed_sqlite_path: str | None,
    user_id: str,
    latest_new_by_search: dict[str, int],
    scan_limit: int = 200,
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for sid in search_ids:
        try:
            out[sid] = build_saved_search_insight(
                db_path=db_path,
                job_state_db_path=job_state_db_path,
                search_id=sid,
                indexed_input_path=indexed_input_path,
                indexed_sqlite_path=indexed_sqlite_path,
                user_id=user_id,
                latest_new_count=latest_new_by_search.get(sid),
                scan_limit=scan_limit,
            )
        except Exception:
            out[sid] = {
                "search_id": sid,
                "current_count": 0,
                "latest_new_count": latest_new_by_search.get(sid),
                "saved_marked_count": 0,
                "dismissed_marked_count": 0,
                "saved_rate": 0.0,
                "dismiss_rate": 0.0,
                "last_run_at": None,
                "scanned_count": 0,
                "scan_limit": scan_limit,
                "is_partial_sample": False,
                "quality_flags": ["insight unavailable"],
            }
    return out
