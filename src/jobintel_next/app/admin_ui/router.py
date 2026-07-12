from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from jobintel_next.product.alerts import (
    SMTPConfig,
    get_alert_run_detail,
    get_alert_runs_summary,
    list_alert_runs,
    persist_email_delivery_to_run,
    send_email_alerts_from_run,
)
from jobintel_next.product.application_tracking import (
    APPLICATION_TEMPLATE_KINDS,
    build_closed_loop_metrics,
    clear_application_details,
    clear_application_state,
    count_application_states,
    create_application_template,
    delete_application_template,
    get_many_application_details,
    get_many_application_states,
    list_follow_up_items,
    list_application_templates,
    set_application_template_active,
    update_application_details,
    set_application_state,
)
from jobintel_next.product.job_state import (
    clear_job_state,
    count_user_job_state_entries,
    count_user_job_states,
    get_many_job_states,
    list_job_urls_by_state,
    set_job_state,
)
from jobintel_next.pipelines.retrieval import QueryParams
from jobintel_next.product.auth import authenticate_local_user, get_user_settings, update_user_settings
from jobintel_next.product.auth import change_local_password
from jobintel_next.product.attention import build_attention_items_for_user
from jobintel_next.product.ranking import rank_jobs
from jobintel_next.product.saved_searches import (
    archive_saved_search,
    build_saved_search_insight,
    build_saved_search_insights_map,
    get_saved_search_results,
    create_saved_search,
    delete_saved_search,
    disable_saved_search,
    enable_saved_search,
    get_saved_search,
    is_saved_search_due,
    list_saved_searches,
    restore_saved_search,
    run_enabled_saved_searches,
    run_saved_search,
    update_saved_search,
)
from jobintel_next.serving import count_jobs, list_jobs


router = APIRouter(tags=["admin-ui"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def _current_user(request: Request) -> tuple[str, str]:
    session = request.scope.get("session")
    if not isinstance(session, dict):
        raise HTTPException(status_code=401, detail="login required")
    user_id = str(session.get("user_id") or "").strip()
    email = str(session.get("user_email") or "").strip()
    if not user_id:
        raise HTTPException(status_code=401, detail="login required")
    if not email:
        email = f"{user_id}@local"
    return user_id, email


def _state(request: Request) -> tuple[str, str, str | None, str]:
    indexed_input = getattr(request.app.state, "indexed_input_path", None)
    saved_db = getattr(request.app.state, "saved_db_path", None)
    sqlite_path = getattr(request.app.state, "sqlite_path", None)
    runs_dir = getattr(request.app.state, "alert_runs_dir", None)
    if not isinstance(indexed_input, str) or not indexed_input:
        raise HTTPException(status_code=500, detail="dataset path not configured")
    if not isinstance(saved_db, str) or not saved_db:
        raise HTTPException(status_code=500, detail="saved db path not configured")
    if not isinstance(runs_dir, str) or not runs_dir:
        raise HTTPException(status_code=500, detail="alert runs dir not configured")
    if sqlite_path is not None and not isinstance(sqlite_path, str):
        raise HTTPException(status_code=500, detail="sqlite path not configured")
    return indexed_input, saved_db, sqlite_path, runs_dir


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


def _redirect_with_query(path: str, **params: str) -> RedirectResponse:
    cleaned = {k: v for k, v in params.items() if v}
    if not cleaned:
        return _redirect(path)
    parsed = urlsplit(path)
    existing = dict(parse_qsl(parsed.query, keep_blank_values=True))
    merged = {**existing, **cleaned}
    query = urlencode(merged)
    target = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))
    return _redirect(target)


def _saved_searches_redirect_target(request: Request) -> str:
    valid = {"all", "active", "disabled", "archived"}
    lifecycle = (request.query_params.get("lifecycle") or "").strip().lower()
    if lifecycle in valid and lifecycle != "all":
        return f"/admin/saved-searches?lifecycle={lifecycle}"
    referer = str(request.headers.get("referer") or "").strip()
    if referer:
        parsed = urlsplit(referer)
        if parsed.path == "/admin/saved-searches":
            query_map = dict(parse_qsl(parsed.query, keep_blank_values=True))
            ref_lifecycle = (query_map.get("lifecycle") or "").strip().lower()
            if ref_lifecycle in valid and ref_lifecycle != "all":
                return f"/admin/saved-searches?lifecycle={ref_lifecycle}"
    return "/admin/saved-searches"


def _job_state_db_path(request: Request) -> str:
    path = getattr(request.app.state, "job_state_db_path", None)
    if not isinstance(path, str) or not path:
        raise HTTPException(status_code=500, detail="job state db path not configured")
    return path


def _trueish(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int((value or "").strip())
    except ValueError:
        return default


def _split_csv(value: str | None) -> list[str]:
    return [x.strip() for x in str(value or "").split(",") if x and x.strip()]


def _normalize_token(value: str) -> str:
    return "_".join(value.strip().lower().split())


def _parse_filters_json(value: str | None) -> dict:
    raw = str(value or "").strip()
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def _is_active_saved_search(saved_search: dict) -> bool:
    return bool(saved_search.get("is_enabled")) and str(saved_search.get("lifecycle") or "active").strip().lower() == "active"


def _build_target_profile(settings: dict[str, object]) -> dict[str, list[str] | str]:
    target_titles = _split_csv(str(settings.get("target_titles") or ""))
    target_role_families = [_normalize_token(x) for x in _split_csv(str(settings.get("target_role_families") or ""))]
    preferred_location_types = [
        x
        for x in [_normalize_token(x) for x in _split_csv(str(settings.get("preferred_location_types") or ""))]
        if x in {"remote", "hybrid", "onsite"}
    ]
    return {
        "target_titles": target_titles,
        "target_titles_normalized": [_normalize_token(x) for x in target_titles],
        "target_role_families": target_role_families,
        "preferred_location_types": preferred_location_types,
        "keywords_note": str(settings.get("keywords_note") or "").strip(),
    }


def _default_target_filters(profile: dict[str, list[str] | str]) -> dict:
    filters: dict[str, object] = {"title_is_other": False}
    role_families = list(profile.get("target_role_families") or [])
    titles_normalized = list(profile.get("target_titles_normalized") or [])
    locations = list(profile.get("preferred_location_types") or [])
    if role_families:
        filters["role_family"] = str(role_families[0])
    elif titles_normalized:
        filters["normalized_title"] = str(titles_normalized[0])
    if locations:
        filters["location_type"] = str(locations[0])
    return filters


def _build_saved_search_suggestions(profile: dict[str, list[str] | str]) -> list[dict[str, str]]:
    role_families = list(profile.get("target_role_families") or [])
    titles = list(profile.get("target_titles") or [])
    titles_normalized = list(profile.get("target_titles_normalized") or [])
    locations = list(profile.get("preferred_location_types") or [])
    keywords_note = str(profile.get("keywords_note") or "")
    default_location = str(locations[0]) if locations else ""

    suggestions: list[dict[str, str]] = []
    seen_keys: set[str] = set()
    if not role_families and not titles_normalized and not locations and not keywords_note:
        return suggestions

    def _add(*, name: str, filters: dict, reason: str) -> None:
        key = json.dumps(filters, sort_keys=True)
        if key in seen_keys:
            return
        seen_keys.add(key)
        q = urlencode(
            {
                "use_target_profile": "true",
                "name": name,
                "query_type": "filters",
                "filters_json": json.dumps(filters, ensure_ascii=True),
                "frequency": "daily",
                "is_enabled": "true",
            }
        )
        suggestions.append(
            {
                "name": name,
                "filters_json": json.dumps(filters, ensure_ascii=True),
                "reason": reason,
                "href": f"/admin/saved-searches/new?{q}",
            }
        )

    _add(
        name="Target profile baseline",
        filters=_default_target_filters(profile),
        reason="Uses your target profile defaults (role/title + preferred location).",
    )

    for rf in role_families[:3]:
        filters = {"role_family": rf, "title_is_other": False}
        if default_location:
            filters["location_type"] = default_location
        _add(
            name=f"Target role: {rf}",
            filters=filters,
            reason="Role family from your target profile.",
        )

    for idx, title_norm in enumerate(titles_normalized[:3]):
        title_label = titles[idx] if idx < len(titles) else title_norm
        filters = {"normalized_title": title_norm, "title_is_other": False}
        if default_location:
            filters["location_type"] = default_location
        _add(
            name=f"Target title: {title_label}",
            filters=filters,
            reason="Title from your target profile.",
        )

    if keywords_note:
        tokens = [t.strip() for t in keywords_note.split(",") if t.strip()]
        if tokens:
            skills_filters = {"skills_contains": tokens[:3], "title_is_other": False}
            if default_location:
                skills_filters["location_type"] = default_location
            _add(
                name="Target keywords helper",
                filters=skills_filters,
                reason="Derived from your profile keywords note.",
            )
    return suggestions


def _saved_search_alignment(
    *,
    saved_search: dict,
    target_role_families: set[str],
    target_titles_normalized: set[str],
    preferred_location_types: set[str],
) -> dict[str, str]:
    if not target_role_families and not target_titles_normalized and not preferred_location_types:
        return {"status": "n/a", "label": "profile empty", "reason": "Set a target profile in Account."}

    if str(saved_search.get("query_type") or "") != "filters":
        return {"status": "partial", "label": "pack/manual review", "reason": "Pack search cannot be fully mapped to target fields."}

    filters = _parse_filters_json(saved_search.get("filters_json"))
    role_family = _normalize_token(str(filters.get("role_family") or ""))
    normalized_title = _normalize_token(str(filters.get("normalized_title") or ""))
    location_type = _normalize_token(str(filters.get("location_type") or ""))

    role_match = bool(role_family and role_family in target_role_families)
    title_match = bool(normalized_title and normalized_title in target_titles_normalized)
    loc_match = bool(location_type and location_type in preferred_location_types)

    if role_match or title_match:
        if loc_match or not preferred_location_types:
            return {"status": "aligned", "label": "aligned", "reason": "Matches target role/title and location preferences."}
        return {"status": "aligned", "label": "aligned", "reason": "Matches target role/title preferences."}
    if loc_match:
        return {"status": "partial", "label": "location only", "reason": "Matches preferred location, role/title mismatch."}
    return {"status": "missing", "label": "missing alignment", "reason": "Does not match current target role/title profile."}


def _gap_closure_href(*, name: str, filters: dict) -> str:
    q = urlencode(
        {
            "use_target_profile": "true",
            "name": name,
            "query_type": "filters",
            "filters_json": json.dumps(filters, ensure_ascii=True),
            "frequency": "daily",
            "is_enabled": "true",
        }
    )
    return f"/admin/saved-searches/new?{q}"


def _build_saved_search_coverage(
    *,
    profile: dict[str, list[str] | str],
    saved_searches: list[dict],
) -> dict[str, object]:
    target_roles = [str(x) for x in list(profile.get("target_role_families") or []) if str(x)]
    target_titles = [str(x) for x in list(profile.get("target_titles_normalized") or []) if str(x)]
    target_locations = [str(x) for x in list(profile.get("preferred_location_types") or []) if str(x)]
    default_location = target_locations[0] if target_locations else ""
    default_role = target_roles[0] if target_roles else ""

    enabled = [s for s in saved_searches if _is_active_saved_search(s)]
    enabled_pack_count = 0
    covered_roles: set[str] = set()
    covered_titles: set[str] = set()
    covered_locations: set[str] = set()
    unconstrained_location_count = 0
    for s in enabled:
        if str(s.get("query_type") or "") == "pack":
            enabled_pack_count += 1
            continue
        if str(s.get("query_type") or "") != "filters":
            continue
        filters = _parse_filters_json(s.get("filters_json"))
        role_family = _normalize_token(str(filters.get("role_family") or ""))
        normalized_title = _normalize_token(str(filters.get("normalized_title") or ""))
        location_type = _normalize_token(str(filters.get("location_type") or ""))
        if role_family:
            covered_roles.add(role_family)
        if normalized_title:
            covered_titles.add(normalized_title)
        if location_type:
            covered_locations.add(location_type)
        else:
            unconstrained_location_count += 1

    def _status_for_exact(target: str, covered_set: set[str]) -> tuple[str, str]:
        if target in covered_set:
            return ("covered", "Exact match via enabled filters search.")
        if enabled_pack_count > 0:
            return ("partial", "Pack searches enabled: potential indirect coverage.")
        return ("missing", "No enabled filters search explicitly covers this target.")

    role_items: list[dict[str, str]] = []
    for role in target_roles:
        status, reason = _status_for_exact(role, covered_roles)
        filters = {"role_family": role, "title_is_other": False}
        if default_location:
            filters["location_type"] = default_location
        role_items.append(
            {
                "kind": "role_family",
                "target": role,
                "status": status,
                "reason": reason,
                "href": _gap_closure_href(name=f"Target role: {role}", filters=filters),
            }
        )

    title_items: list[dict[str, str]] = []
    for title in target_titles:
        status, reason = _status_for_exact(title, covered_titles)
        filters = {"normalized_title": title, "title_is_other": False}
        if default_location:
            filters["location_type"] = default_location
        title_items.append(
            {
                "kind": "normalized_title",
                "target": title,
                "status": status,
                "reason": reason,
                "href": _gap_closure_href(name=f"Target title: {title}", filters=filters),
            }
        )

    location_items: list[dict[str, str]] = []
    for location in target_locations:
        if location in covered_locations:
            status = "covered"
            reason = "Exact location_type match via enabled filters search."
        elif unconstrained_location_count > 0 or enabled_pack_count > 0:
            status = "partial"
            reason = "Some enabled searches are broad (no location constraint or pack)."
        else:
            status = "missing"
            reason = "No enabled search includes this location preference."
        filters = {"location_type": location, "title_is_other": False}
        if default_role:
            filters["role_family"] = default_role
        location_items.append(
            {
                "kind": "location_type",
                "target": location,
                "status": status,
                "reason": reason,
                "href": _gap_closure_href(name=f"Target location: {location}", filters=filters),
            }
        )

    all_items = role_items + title_items + location_items
    covered_count = sum(1 for x in all_items if x["status"] == "covered")
    partial_count = sum(1 for x in all_items if x["status"] == "partial")
    missing_count = sum(1 for x in all_items if x["status"] == "missing")
    total_targets = len(all_items)
    coverage_pct = int(round((covered_count * 100.0 / total_targets), 0)) if total_targets else 0

    return {
        "empty_profile": total_targets == 0,
        "total_targets": total_targets,
        "covered_count": covered_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "coverage_pct": coverage_pct,
        "role_items": role_items,
        "title_items": title_items,
        "location_items": location_items,
    }


def _categorize_saved_search_strategy(*, saved_search: dict, alignment: dict[str, str], insight: dict) -> dict[str, str]:
    query_type = str(saved_search.get("query_type") or "")
    frequency = str(saved_search.get("frequency") or "")
    filters = _parse_filters_json(saved_search.get("filters_json"))
    has_role = bool(str(filters.get("role_family") or "").strip())
    has_title = bool(str(filters.get("normalized_title") or "").strip())
    has_location = bool(str(filters.get("location_type") or "").strip())
    has_skill_focus = isinstance(filters.get("skills_contains"), list) and len(filters.get("skills_contains") or []) > 0
    alignment_status = str(alignment.get("status") or "")

    if query_type == "pack" or frequency == "manual":
        return {
            "key": "manual_pack_review",
            "label": "manual/pack review",
            "reason": "Pack or manual-frequency search: periodic review oriented.",
        }
    if alignment_status == "aligned" and (has_role or has_title):
        return {
            "key": "target_aligned",
            "label": "target-aligned",
            "reason": "Explicitly aligned with target role/title profile.",
        }
    if has_location and not has_role and not has_title:
        return {
            "key": "location_focused",
            "label": "location-focused",
            "reason": "Location constrained without strong role/title targeting.",
        }
    if has_role or has_title or has_skill_focus:
        return {
            "key": "target_aligned",
            "label": "target-aligned",
            "reason": "Focused filters (role/title/skills) for higher precision.",
        }
    if float(insight.get("dismiss_rate", 0.0) or 0.0) >= 0.6:
        return {
            "key": "broad_discovery",
            "label": "broad discovery",
            "reason": "Broad exploration; currently high dismiss-rate.",
        }
    return {
        "key": "broad_discovery",
        "label": "broad discovery",
        "reason": "Broad scan to discover opportunities outside strict filters.",
    }


def _build_search_portfolio_summary(
    *,
    saved_searches: list[dict],
    strategy_map: dict[str, dict[str, str]],
    insights_map: dict[str, dict],
    target_profile: dict[str, list[str] | str],
) -> dict[str, object]:
    enabled = [s for s in saved_searches if _is_active_saved_search(s)]
    category_counts = {
        "broad_discovery": 0,
        "target_aligned": 0,
        "location_focused": 0,
        "manual_pack_review": 0,
    }
    low_yield_count = 0
    for s in enabled:
        sid = str(s.get("search_id") or "")
        strategy = strategy_map.get(sid, {})
        key = str(strategy.get("key") or "")
        if key in category_counts:
            category_counts[key] += 1
        ins = insights_map.get(sid, {})
        latest_new = int(ins.get("latest_new_count") or 0)
        dismiss_rate = float(ins.get("dismiss_rate", 0.0) or 0.0)
        quality_flags = [str(x) for x in (ins.get("quality_flags") or []) if str(x)]
        if latest_new == 0 and (dismiss_rate >= 0.6 or "no recent new matches" in quality_flags):
            low_yield_count += 1

    insights: list[dict[str, str]] = []
    enabled_count = len(enabled)
    broad_count = category_counts["broad_discovery"]
    target_count = category_counts["target_aligned"]
    has_target_profile = bool(list(target_profile.get("target_role_families") or []) or list(target_profile.get("target_titles_normalized") or []))

    if enabled_count == 0:
        insights.append(
            {
                "level": "medium",
                "text": "No enabled searches in portfolio. Enable or create searches to start discovery.",
                "href": "/admin/saved-searches/new?use_target_profile=true",
            }
        )
    else:
        if broad_count >= 3 and broad_count > (target_count * 2):
            insights.append(
                {
                    "level": "medium",
                    "text": "Too many broad searches compared to focused ones.",
                    "href": "/admin/saved-searches/new?use_target_profile=true",
                }
            )
        if has_target_profile and target_count == 0:
            insights.append(
                {
                    "level": "high",
                    "text": "Missing focused target-aligned searches for your profile.",
                    "href": "/admin/saved-searches/new?use_target_profile=true",
                }
            )
        if enabled_count >= 2 and low_yield_count >= max(2, enabled_count // 2):
            insights.append(
                {
                    "level": "medium",
                    "text": "Portfolio dominated by low-yield searches (recently no new / high dismiss-rate).",
                    "href": "/admin/saved-searches",
                }
            )
        if target_count >= 1 and broad_count >= 1 and low_yield_count < max(1, enabled_count // 2):
            insights.append(
                {
                    "level": "low",
                    "text": "Good balance between broad discovery and targeted searches.",
                    "href": "/admin/saved-searches",
                }
            )
    return {
        "enabled_count": enabled_count,
        "category_counts": category_counts,
        "low_yield_count": low_yield_count,
        "insights": insights,
    }


def _build_search_hygiene_summary(
    *,
    saved_searches: list[dict],
    insights_map: dict[str, dict],
) -> dict[str, object]:
    enabled = [s for s in saved_searches if _is_active_saved_search(s)]
    by_id = {str(s.get("search_id") or ""): s for s in saved_searches}
    items: list[dict[str, object]] = []
    seen_item_keys: set[str] = set()

    def _push(
        *,
        category: str,
        severity: str,
        search_id: str,
        reason: str,
        related_ids: list[str] | None = None,
        candidate_disable: bool = False,
    ) -> None:
        key = f"{category}:{search_id}:{'|'.join(sorted(related_ids or []))}:{reason}"
        if key in seen_item_keys:
            return
        seen_item_keys.add(key)
        s = by_id.get(search_id, {})
        items.append(
            {
                "category": category,
                "severity": severity,
                "search_id": search_id,
                "search_name": str(s.get("name") or search_id),
                "reason": reason,
                "related_ids": related_ids or [],
                "is_enabled": bool(s.get("is_enabled")),
                "candidate_disable": candidate_disable,
            }
        )

    # 1) Evident duplicates.
    signature_groups: dict[str, list[str]] = {}
    for s in enabled:
        sid = str(s.get("search_id") or "")
        query_type = str(s.get("query_type") or "")
        if query_type == "pack":
            signature = f"pack:{str(s.get('pack_name') or '').strip().lower()}"
        else:
            signature = f"filters:{json.dumps(_parse_filters_json(s.get('filters_json')), sort_keys=True)}"
        signature_groups.setdefault(signature, []).append(sid)
    for ids in signature_groups.values():
        if len(ids) < 2:
            continue
        for sid in ids:
            related = [x for x in ids if x != sid]
            _push(
                category="duplicate",
                severity="high",
                search_id=sid,
                reason="Same query signature as another enabled saved search.",
                related_ids=related,
                candidate_disable=True,
            )

    # 2) Simple overlaps for enabled filters searches.
    enabled_filters = [s for s in enabled if str(s.get("query_type") or "") == "filters"]
    for i, left in enumerate(enabled_filters):
        left_id = str(left.get("search_id") or "")
        lf = _parse_filters_json(left.get("filters_json"))
        left_role = _normalize_token(str(lf.get("role_family") or ""))
        left_title = _normalize_token(str(lf.get("normalized_title") or ""))
        left_loc = _normalize_token(str(lf.get("location_type") or ""))
        if not left_role:
            continue
        for right in enabled_filters[i + 1 :]:
            right_id = str(right.get("search_id") or "")
            rf = _parse_filters_json(right.get("filters_json"))
            right_role = _normalize_token(str(rf.get("role_family") or ""))
            right_title = _normalize_token(str(rf.get("normalized_title") or ""))
            right_loc = _normalize_token(str(rf.get("location_type") or ""))
            if left_role != right_role:
                continue
            same_or_compatible_loc = (not left_loc or not right_loc or left_loc == right_loc)
            if not same_or_compatible_loc:
                continue
            title_overlap = (not left_title or not right_title or left_title == right_title)
            if not title_overlap:
                continue
            _push(
                category="overlap",
                severity="medium",
                search_id=left_id,
                reason=f"Overlaps with {str(right.get('name') or right_id)} on role/location scope.",
                related_ids=[right_id],
                candidate_disable=False,
            )
            _push(
                category="overlap",
                severity="medium",
                search_id=right_id,
                reason=f"Overlaps with {str(left.get('name') or left_id)} on role/location scope.",
                related_ids=[left_id],
                candidate_disable=False,
            )

    # 3) Low-yield/noisy/stale.
    for s in enabled:
        sid = str(s.get("search_id") or "")
        ins = insights_map.get(sid, {})
        latest_new = ins.get("latest_new_count")
        latest_new_i = int(latest_new or 0) if latest_new is not None else None
        dismiss_rate = float(ins.get("dismiss_rate", 0.0) or 0.0)
        has_last_run = bool(str(s.get("last_run_at") or "").strip())
        quality_flags = [str(x) for x in (ins.get("quality_flags") or []) if str(x)]

        if has_last_run and latest_new_i is not None and latest_new_i == 0:
            _push(
                category="stale",
                severity="medium",
                search_id=sid,
                reason="No recent new matches on latest run.",
                candidate_disable=False,
            )
        if latest_new_i is not None and latest_new_i <= 1 and dismiss_rate >= 0.6:
            _push(
                category="noisy",
                severity="high",
                search_id=sid,
                reason="High dismiss-rate with low recent new matches.",
                candidate_disable=True,
            )
        if "high dismiss rate" in quality_flags and latest_new_i in {0, None}:
            _push(
                category="low_yield",
                severity="medium",
                search_id=sid,
                reason="Persistently low-yield search (high dismiss-rate / no new matches).",
                candidate_disable=True,
            )

    category_counts = {
        "duplicate": 0,
        "overlap": 0,
        "noisy": 0,
        "stale": 0,
        "low_yield": 0,
    }
    for it in items:
        c = str(it.get("category") or "")
        if c in category_counts:
            category_counts[c] += 1

    candidate_disable_count = sum(1 for it in items if bool(it.get("candidate_disable")))
    return {
        "items": items,
        "category_counts": category_counts,
        "candidate_disable_count": candidate_disable_count,
    }


def _parse_iso_ts(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _follow_up_status(value: str | None, *, now: datetime | None = None) -> str:
    dt = _parse_iso_ts(value)
    if dt is None:
        return ""
    ref = now or datetime.now(timezone.utc)
    if dt <= ref:
        return "overdue"
    if dt <= (ref + timedelta(days=2)):
        return "due"
    return "scheduled"


def _rank_reason(row: dict) -> str:
    factors = row.get("rank_factors")
    if not isinstance(factors, dict):
        return ""
    reasons: list[str] = []
    state_points = float(factors.get("job_state") or 0.0)
    if state_points > 0:
        reasons.append(f"state:{row.get('job_state', 'new')}")
    if float(factors.get("freshness_published") or 0.0) >= 7.0:
        reasons.append("fresh")
    if float(factors.get("has_salary") or 0.0) > 0:
        reasons.append("salary signal")
    if float(factors.get("has_skills") or 0.0) > 0:
        reasons.append("skills signal")
    if float(factors.get("title_fit") or 0.0) > 0:
        reasons.append("title fit")
    if float(factors.get("role_fit") or 0.0) > 0:
        reasons.append("role fit")
    if float(factors.get("title_is_other") or 0.0) < 0:
        reasons.append("penalty:other")
    return ", ".join(reasons[:4])


def _pct_label(value: float) -> str:
    return f"{int(round(max(0.0, min(1.0, value)) * 100.0))}%"


def _latest_search_outcomes(
    *,
    runs_dir: str,
    user_id: str,
    search_ids: set[str],
    recent_limit: int = 20,
) -> dict[str, dict[str, str | int | None]]:
    outcomes: dict[str, dict[str, str | int | None]] = {}
    if not search_ids:
        return outcomes
    runs = list_alert_runs(runs_dir=runs_dir, user_id=user_id)[:recent_limit]
    for run in runs:
        run_id = str(run.get("run_id") or "")
        if not run_id:
            continue
        try:
            detail = get_alert_run_detail(runs_dir=runs_dir, run_id=run_id, user_id=user_id)
        except ValueError:
            continue
        for item in detail.get("results", []):
            if not isinstance(item, dict):
                continue
            sid = str(item.get("search_id") or "")
            if not sid or sid not in search_ids or sid in outcomes:
                continue
            outcomes[sid] = {
                "run_id": detail.get("run_id"),
                "run_timestamp": detail.get("run_timestamp"),
                "status": item.get("status"),
                "new_matches_count": int(item.get("new_matches_count") or 0),
                "total_current_matches": item.get("total_current_matches"),
            }
    return outcomes


@router.get("/login")
def login_page(request: Request):
    session = request.scope.get("session")
    if isinstance(session, dict) and str(session.get("user_id") or "").strip():
        target = (request.query_params.get("next") or "/admin").strip() or "/admin"
        return _redirect(target)
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "next_url": request.query_params.get("next", "/admin"),
            "bootstrap_email": getattr(request.app.state, "bootstrap_user_email", "admin@example.com"),
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.post("/login")
async def login_submit(request: Request):
    _, saved_db, _, _ = _state(request)
    form = await request.form()
    email = str(form.get("email") or "").strip()
    password = str(form.get("password") or "").strip()
    next_url = str(form.get("next") or "/admin").strip() or "/admin"
    user = authenticate_local_user(db_path=saved_db, email=email, password=password)
    if user is None:
        return _redirect_with_query("/login", error="Login failed: invalid email or password", next=next_url)
    session = request.scope.get("session")
    if not isinstance(session, dict):
        raise HTTPException(status_code=500, detail="session not configured")
    session.clear()
    session["user_id"] = str(user["user_id"])
    session["user_email"] = str(user["email"])
    return _redirect(next_url)


@router.post("/logout")
def logout_submit(request: Request):
    session = request.scope.get("session")
    if isinstance(session, dict):
        session.clear()
    resp = _redirect_with_query("/login", message="Logged out")
    cookie_name = str(getattr(request.app.state, "session_cookie_name", "jobintel_session"))
    resp.delete_cookie(cookie_name, path="/")
    resp.delete_cookie("session", path="/")  # backward compatibility with earlier cookie name
    return resp


@router.get("/admin")
def admin_home(request: Request):
    indexed_input, saved_db, sqlite_path, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    settings = get_user_settings(db_path=saved_db, user_id=user_id)
    target_titles = _split_csv(str(settings.get("target_titles") or ""))
    target_role_families = _split_csv(str(settings.get("target_role_families") or ""))
    target_locations = _split_csv(str(settings.get("preferred_location_types") or ""))
    saved = list_saved_searches(db_path=saved_db, user_id=user_id)
    due_count = sum(1 for s in saved if is_saved_search_due(s))
    enabled_count = sum(1 for s in saved if _is_active_saved_search(s))
    summary = get_alert_runs_summary(runs_dir=runs_dir, user_id=user_id)
    recent_runs = list_alert_runs(runs_dir=runs_dir, user_id=user_id)[:10]
    inbox_review_count = count_user_job_state_entries(db_path=_job_state_db_path(request), user_id=user_id)
    latest_run_status = "not_run"
    if recent_runs:
        processed_error = int(recent_runs[0].get("processed_error") or 0)
        latest_run_status = "error" if processed_error > 0 else "ok"
    diagnostics = {
        "current_user_id": user_id,
        "current_user_email": str(settings.get("email") or ""),
        "default_alert_email": str(settings.get("default_alert_email") or ""),
        "default_alert_email_configured": bool(str(settings.get("default_alert_email") or "").strip()),
        "saved_searches_enabled_count": enabled_count,
        "latest_run_status": latest_run_status,
        "sqlite_backend_enabled": bool(getattr(request.app.state, "sqlite_path", None)),
        "alert_runs_dir": runs_dir,
    }
    onboarding_items = [
        {
            "label": "Create your first saved search",
            "done": len(saved) > 0,
            "href": "/admin/saved-searches/new",
            "cta": "Create saved search",
        },
        {
            "label": "Set a default alert email in Account",
            "done": bool(str(settings.get("default_alert_email") or "").strip()),
            "href": "/admin/account",
            "cta": "Set alert email",
        },
        {
            "label": "Run alerts to generate your first run",
            "done": int(summary.get("runs_count") or 0) > 0,
            "href": "/admin/alerts",
            "cta": "Run alerts",
        },
        {
            "label": "Review your inbox and mark at least one job",
            "done": inbox_review_count > 0,
            "href": "/admin/inbox?state=new",
            "cta": "Open inbox",
        },
    ]
    onboarding_done = sum(1 for x in onboarding_items if x["done"])
    latest_digest = None
    if recent_runs:
        latest_run_id = str(recent_runs[0].get("run_id") or "")
        if latest_run_id:
            try:
                latest = get_alert_run_detail(runs_dir=runs_dir, run_id=latest_run_id, user_id=user_id)
                latest_digest = latest.get("digest_delivery")
            except ValueError:
                latest_digest = None
    attention_items = build_attention_items_for_user(
        saved_db_path=saved_db,
        job_state_db_path=_job_state_db_path(request),
        runs_dir=runs_dir,
        indexed_input_path=indexed_input,
        indexed_sqlite_path=sqlite_path,
        user_id=user_id,
        max_items=8,
    )
    latest_new_by_search = {}
    latest_outcomes = _latest_search_outcomes(
        runs_dir=runs_dir,
        user_id=user_id,
        search_ids={str(s.get("search_id") or "") for s in saved},
    )
    for sid, v in latest_outcomes.items():
        if isinstance(v, dict):
            latest_new_by_search[sid] = int(v.get("new_matches_count") or 0)
    insights_map = build_saved_search_insights_map(
        db_path=saved_db,
        job_state_db_path=_job_state_db_path(request),
        search_ids=[str(s.get("search_id") or "") for s in saved if str(s.get("search_id") or "")],
        indexed_input_path=indexed_input,
        indexed_sqlite_path=sqlite_path,
        user_id=user_id,
        latest_new_by_search=latest_new_by_search,
        scan_limit=200,
    )
    saved_searches_needing_attention: list[dict] = []
    for s in saved:
        sid = str(s.get("search_id") or "")
        insight = insights_map.get(sid, {})
        flags = [str(x) for x in (insight.get("quality_flags") or []) if str(x).strip()]
        if is_saved_search_due(s):
            flags = ["due now", *flags]
        if flags:
            saved_searches_needing_attention.append(
                {
                    "search_id": sid,
                    "name": str(s.get("name") or sid),
                    "flags": flags[:3],
                    "latest_new_count": int(insight.get("latest_new_count") or 0),
                }
            )
    saved_searches_needing_attention = saved_searches_needing_attention[:5]

    total_jobs = int(count_jobs(input_path=indexed_input, sqlite_path=sqlite_path, query=QueryParams())["count"] or 0)
    job_state_counts = count_user_job_states(db_path=_job_state_db_path(request), user_id=user_id)
    funnel_new = max(
        0,
        total_jobs
        - int(job_state_counts.get("seen") or 0)
        - int(job_state_counts.get("saved") or 0)
        - int(job_state_counts.get("dismissed") or 0),
    )
    saved_urls = list_job_urls_by_state(db_path=_job_state_db_path(request), state="saved", user_id=user_id)
    app_states_saved = get_many_application_states(
        db_path=_job_state_db_path(request),
        job_urls=saved_urls,
        user_id=user_id,
    )
    app_details_saved = get_many_application_details(
        db_path=_job_state_db_path(request),
        job_urls=saved_urls,
        user_id=user_id,
    )
    pipeline_counts = count_application_states(
        db_path=_job_state_db_path(request),
        job_urls=saved_urls,
        user_id=user_id,
    )
    closed_loop = build_closed_loop_metrics(
        db_path=_job_state_db_path(request),
        job_urls=saved_urls,
        user_id=user_id,
    )
    closed_loop_insights: list[str] = [f"You have {int(closed_loop['open_pipeline_count'])} open opportunities."]
    if int(closed_loop["interview_count"]) > 0:
        closed_loop_insights.append(f"{int(closed_loop['interview_count'])} interviews currently active.")
    if int(closed_loop["total_count"]) >= 5 and float(closed_loop["saved_to_applied_rate"]) < 0.2:
        closed_loop_insights.append("High shortlist volume, low applied conversion.")
    closed_loop_labels = {
        "saved_to_applied": _pct_label(float(closed_loop["saved_to_applied_rate"])),
        "applied_to_interview": _pct_label(float(closed_loop["applied_to_interview_rate"])),
        "interview_to_rejected": _pct_label(float(closed_loop["interview_to_rejected_rate"])),
    }
    saved_without_notes_count = 0
    interview_missing_date_count = 0
    follow_up_due_count = 0
    for u in saved_urls:
        details = app_details_saved.get(u, {})
        notes = str(details.get("notes") or "").strip()
        state = app_states_saved.get(u, "saved")
        if state == "saved" and not notes:
            saved_without_notes_count += 1
        if state == "interview" and not str(details.get("interview_at") or "").strip():
            interview_missing_date_count += 1
        if _follow_up_status(str(details.get("follow_up_at") or "")) in {"due", "overdue"}:
            follow_up_due_count += 1
    funnel_counts = {
        "new": funnel_new,
        "saved": int(job_state_counts.get("saved") or 0),
        "applied": int(pipeline_counts.get("applied") or 0),
        "interview": int(pipeline_counts.get("interview") or 0),
        "rejected": int(pipeline_counts.get("rejected") or 0),
    }

    top_shortlist_items: list[dict] = []
    pipeline_needing_attention: list[dict] = []
    needs_follow_up: list[dict] = []
    target_profile_insights: list[str] = []
    shortlist_location_mix = {"remote": 0, "hybrid": 0, "onsite": 0, "other": 0}
    if saved_urls:
        saved_set = set(saved_urls)
        rep_saved = list_jobs(
            input_path=indexed_input,
            sqlite_path=sqlite_path,
            query=QueryParams(sort_by="published_at_desc", limit=None),
            limit=5000,
            offset=0,
        )
        rows_saved = [dict(r) for r in rep_saved.get("results", []) if isinstance(r, dict)]
        saved_rows = [r for r in rows_saved if str(r.get("url") or "") in saved_set]
        ranked_saved = rank_jobs(rows=saved_rows, states_by_url=get_many_job_states(
            db_path=_job_state_db_path(request),
            job_urls=[str(r.get("url") or "") for r in saved_rows],
            user_id=user_id,
        ))
        for row in ranked_saved:
            row_url = str(row.get("url") or "")
            row["application_state"] = app_states_saved.get(row_url, "saved")
            details = app_details_saved.get(row_url, {})
            row["application_notes"] = str(details.get("notes") or "")
            row["applied_at"] = str(details.get("applied_at") or "")
            row["interview_at"] = str(details.get("interview_at") or "")
            row["follow_up_at"] = str(details.get("follow_up_at") or "")
            row["follow_up_note"] = str(details.get("follow_up_note") or "")
            row["application_channel"] = str(details.get("application_channel") or "")
            row["contact_name"] = str(details.get("contact_name") or "")
            row["contact_email"] = str(details.get("contact_email") or "")
            row["compensation_note"] = str(details.get("compensation_note") or "")
            row["external_application_url"] = str(details.get("external_application_url") or "")
            row["follow_up_status"] = _follow_up_status(row["follow_up_at"])
            row["rank_reason"] = _rank_reason(row)
            loc = str(row.get("location_type") or "").strip().lower()
            if loc in shortlist_location_mix:
                shortlist_location_mix[loc] += 1
            else:
                shortlist_location_mix["other"] += 1
        top_shortlist_items = ranked_saved[:5]
        for row in ranked_saved:
            state = str(row.get("application_state") or "saved")
            notes = str(row.get("application_notes") or "").strip()
            interview_at = str(row.get("interview_at") or "").strip()
            reason = ""
            if state == "saved" and not notes:
                reason = "saved without notes"
            elif state == "interview" and not interview_at:
                reason = "interview without date"
            if reason:
                pipeline_needing_attention.append(
                    {
                        "url": str(row.get("url") or ""),
                        "title_raw": str(row.get("title_raw") or "-"),
                        "reason": reason,
                    }
                )
            if len(pipeline_needing_attention) >= 5:
                break
        due_rows = [r for r in ranked_saved if str(r.get("follow_up_status") or "") in {"due", "overdue"}]
        due_rows = sorted(
            due_rows,
            key=lambda r: (
                0 if str(r.get("follow_up_status")) == "overdue" else 1,
                _parse_iso_ts(str(r.get("follow_up_at") or "")) or datetime.max.replace(tzinfo=timezone.utc),
            ),
        )
        for row in due_rows[:5]:
            needs_follow_up.append(
                {
                    "url": str(row.get("url") or ""),
                    "title_raw": str(row.get("title_raw") or "-"),
                    "follow_up_at": str(row.get("follow_up_at") or ""),
                    "follow_up_note": str(row.get("follow_up_note") or ""),
                    "follow_up_status": str(row.get("follow_up_status") or ""),
                }
            )
        if target_role_families and ranked_saved:
            matched = sum(1 for r in ranked_saved if str(r.get("role_family") or "").strip() in set(target_role_families))
            target_profile_insights.append(
                f"Role-family alignment: {matched}/{len(ranked_saved)} shortlist items match your target families."
            )
        if target_locations and ranked_saved:
            preferred_hits = 0
            for r in ranked_saved:
                loc = str(r.get("location_type") or "").strip().lower()
                if loc in target_locations:
                    preferred_hits += 1
            target_profile_insights.append(
                f"Location alignment: {preferred_hits}/{len(ranked_saved)} shortlist items match preferred locations."
            )
    top_ranked_new_jobs: list[dict] = []
    try:
        rep_top = list_jobs(
            input_path=getattr(request.app.state, "indexed_input_path", ""),
            sqlite_path=getattr(request.app.state, "sqlite_path", None),
            query=QueryParams(sort_by="published_at_desc", limit=None),
            limit=200,
            offset=0,
        )
        rows_top = [dict(r) for r in rep_top.get("results", []) if isinstance(r, dict)]
        states_top = get_many_job_states(
            db_path=_job_state_db_path(request),
            job_urls=[str(r.get("url") or "") for r in rows_top],
            user_id=user_id,
        )
        ranked_top = rank_jobs(rows=rows_top, states_by_url=states_top)
        for row in ranked_top:
            if str(row.get("job_state") or "new") != "new":
                continue
            row["rank_reason"] = _rank_reason(row)
            top_ranked_new_jobs.append(row)
            if len(top_ranked_new_jobs) >= 5:
                break
    except Exception:
        top_ranked_new_jobs = []
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "saved_searches_count": len(saved),
            "saved_searches_enabled_count": enabled_count,
            "saved_searches_due_count": due_count,
            "summary": summary,
            "recent_runs": recent_runs,
            "target_titles": target_titles,
            "target_role_families": target_role_families,
            "target_locations": target_locations,
            "salary_target_note": str(settings.get("salary_target_note") or ""),
            "keywords_note": str(settings.get("keywords_note") or ""),
            "target_profile_insights": target_profile_insights,
            "shortlist_location_mix": shortlist_location_mix,
            "latest_digest": latest_digest,
            "attention_items": attention_items,
            "diagnostics": diagnostics,
            "funnel_counts": funnel_counts,
            "closed_loop": closed_loop,
            "closed_loop_labels": closed_loop_labels,
            "closed_loop_insights": closed_loop_insights,
            "saved_without_notes_count": saved_without_notes_count,
            "interview_missing_date_count": interview_missing_date_count,
            "follow_up_due_count": follow_up_due_count,
            "saved_searches_needing_attention": saved_searches_needing_attention,
            "top_shortlist_items": top_shortlist_items,
            "pipeline_needing_attention": pipeline_needing_attention,
            "needs_follow_up": needs_follow_up,
            "top_ranked_new_jobs": top_ranked_new_jobs,
            "onboarding_items": onboarding_items,
            "onboarding_done": onboarding_done,
            "onboarding_total": len(onboarding_items),
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin/notifications")
def admin_notifications(request: Request):
    indexed_input, saved_db, sqlite_path, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    items = build_attention_items_for_user(
        saved_db_path=saved_db,
        job_state_db_path=_job_state_db_path(request),
        runs_dir=runs_dir,
        indexed_input_path=indexed_input,
        indexed_sqlite_path=sqlite_path,
        user_id=user_id,
        max_items=50,
    )
    return templates.TemplateResponse(
        request,
        "notifications.html",
        {
            "items": items,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin/today")
def admin_today(request: Request):
    indexed_input, saved_db, sqlite_path, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    settings = get_user_settings(db_path=saved_db, user_id=user_id)
    job_state_db = _job_state_db_path(request)

    rep = list_jobs(
        input_path=indexed_input,
        sqlite_path=sqlite_path,
        query=QueryParams(sort_by="published_at_desc", limit=None),
        limit=5000,
        offset=0,
    )
    rows = [dict(r) for r in rep.get("results", []) if isinstance(r, dict)]
    states = get_many_job_states(
        db_path=job_state_db,
        job_urls=[str(r.get("url") or "") for r in rows],
        user_id=user_id,
    )
    ranked = rank_jobs(rows=rows, states_by_url=states)
    by_url = {str(r.get("url") or ""): r for r in ranked}

    high_rank_new_jobs: list[dict] = []
    for row in ranked:
        if str(row.get("job_state") or "new") != "new":
            continue
        row["rank_reason"] = _rank_reason(row)
        high_rank_new_jobs.append(row)
        if len(high_rank_new_jobs) >= 8:
            break

    saved_urls = list_job_urls_by_state(db_path=job_state_db, state="saved", user_id=user_id)
    app_states = get_many_application_states(db_path=job_state_db, job_urls=saved_urls, user_id=user_id)
    app_details = get_many_application_details(db_path=job_state_db, job_urls=saved_urls, user_id=user_id)

    shortlist_attention: list[dict[str, str]] = []
    for url in saved_urls:
        details = app_details.get(url, {})
        app_state = str(app_states.get(url) or "saved")
        reason = ""
        priority = "low"
        if app_state == "saved" and not str(details.get("notes") or "").strip():
            reason = "saved without notes"
            priority = "medium"
        elif app_state == "interview" and not str(details.get("interview_at") or "").strip():
            reason = "interview without date"
            priority = "high"
        if not reason:
            continue
        title = str((by_url.get(url) or {}).get("title_raw") or url)
        shortlist_attention.append(
            {
                "url": url,
                "title_raw": title,
                "reason": reason,
                "priority": priority,
            }
        )
        if len(shortlist_attention) >= 8:
            break

    follow_up_due: list[dict[str, str]] = []
    for item in list_follow_up_items(db_path=job_state_db, user_id=user_id, limit=100):
        status = str(item.get("follow_up_status") or "")
        if status not in {"due", "overdue"}:
            continue
        url = str(item.get("job_url") or "")
        title = str((by_url.get(url) or {}).get("title_raw") or url)
        follow_up_due.append(
            {
                "url": url,
                "title_raw": title,
                "follow_up_at": str(item.get("follow_up_at") or ""),
                "follow_up_note": str(item.get("follow_up_note") or ""),
                "follow_up_status": status,
            }
        )
        if len(follow_up_due) >= 8:
            break

    attention_items = build_attention_items_for_user(
        saved_db_path=saved_db,
        job_state_db_path=job_state_db,
        runs_dir=runs_dir,
        indexed_input_path=indexed_input,
        indexed_sqlite_path=sqlite_path,
        user_id=user_id,
        max_items=30,
    )
    high_attention = [x for x in attention_items if str(x.get("priority") or "") == "high"][:8]

    return templates.TemplateResponse(
        request,
        "today.html",
        {
            "target_titles": _split_csv(str(settings.get("target_titles") or "")),
            "target_role_families": _split_csv(str(settings.get("target_role_families") or "")),
            "target_locations": _split_csv(str(settings.get("preferred_location_types") or "")),
            "high_rank_new_jobs": high_rank_new_jobs,
            "follow_up_due": follow_up_due,
            "shortlist_attention": shortlist_attention,
            "high_attention": high_attention,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin/review")
def admin_review(request: Request):
    indexed_input, saved_db, sqlite_path, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    job_state_db = _job_state_db_path(request)
    now = datetime.now(timezone.utc)

    rep = list_jobs(
        input_path=indexed_input,
        sqlite_path=sqlite_path,
        query=QueryParams(sort_by="published_at_desc", limit=None),
        limit=5000,
        offset=0,
    )
    rows = [dict(r) for r in rep.get("results", []) if isinstance(r, dict)]
    by_url = {str(r.get("url") or ""): r for r in rows}

    saved_urls = list_job_urls_by_state(db_path=job_state_db, state="saved", user_id=user_id)
    app_states = get_many_application_states(db_path=job_state_db, job_urls=saved_urls, user_id=user_id)
    app_details = get_many_application_details(db_path=job_state_db, job_urls=saved_urls, user_id=user_id)

    stale_saved_jobs: list[dict[str, str]] = []
    stale_applied_jobs: list[dict[str, str]] = []
    interview_missing_items: list[dict[str, str]] = []
    for url in saved_urls:
        row = by_url.get(url, {})
        title = str(row.get("title_raw") or url)
        details = app_details.get(url, {})
        state = str(app_states.get(url) or "saved")
        notes = str(details.get("notes") or "").strip()
        follow_up_at = str(details.get("follow_up_at") or "").strip()
        application_channel = str(details.get("application_channel") or "").strip()
        contact_name = str(details.get("contact_name") or "").strip()
        contact_email = str(details.get("contact_email") or "").strip()
        resume_label = str(details.get("resume_label") or "").strip()
        submission_note = str(details.get("submission_note") or "").strip()
        applied_at = str(details.get("applied_at") or "").strip()
        interview_at = str(details.get("interview_at") or "").strip()
        published_dt = _parse_iso_ts(str(row.get("published_at") or ""))

        if state == "saved":
            reason = ""
            if published_dt and (now - published_dt) >= timedelta(days=14):
                reason = "saved for 14+ days without pipeline progress"
            elif not notes and not follow_up_at:
                reason = "saved without notes and follow-up"
            if reason:
                stale_saved_jobs.append(
                    {
                        "url": url,
                        "title_raw": title,
                        "reason": reason,
                        "priority": "medium",
                        "href": "/admin/shortlist?pipeline_state=saved",
                    }
                )

        if state == "applied":
            reason = ""
            applied_dt = _parse_iso_ts(applied_at)
            if not applied_at:
                reason = "applied without applied date"
            elif not application_channel:
                reason = "applied without channel"
            elif not resume_label:
                reason = "applied without resume label"
            elif not submission_note:
                reason = "applied without submission note"
            elif not follow_up_at and applied_dt and (now - applied_dt) >= timedelta(days=7):
                reason = "applied 7+ days ago without follow-up"
            elif not notes and not follow_up_at:
                reason = "applied without notes/follow-up"
            if reason:
                stale_applied_jobs.append(
                    {
                        "url": url,
                        "title_raw": title,
                        "reason": reason,
                        "priority": "high" if "7+ days" in reason else "medium",
                        "href": "/admin/shortlist?pipeline_state=applied",
                    }
                )

        if state == "interview":
            missing: list[str] = []
            if not interview_at:
                missing.append("interview date")
            if not notes:
                missing.append("interview notes")
            if not contact_name and not contact_email:
                missing.append("contact")
            if missing:
                interview_missing_items.append(
                    {
                        "url": url,
                        "title_raw": title,
                        "reason": f"missing {' and '.join(missing)}",
                        "priority": "high",
                        "href": "/admin/shortlist?pipeline_state=interview",
                    }
                )

    stale_saved_jobs = stale_saved_jobs[:10]
    stale_applied_jobs = stale_applied_jobs[:10]
    interview_missing_items = interview_missing_items[:10]

    saved = list_saved_searches(db_path=saved_db, user_id=user_id)
    latest_outcomes = _latest_search_outcomes(
        runs_dir=runs_dir,
        user_id=user_id,
        search_ids={str(s.get("search_id") or "") for s in saved},
    )
    latest_new_by_search = {
        sid: int(v.get("new_matches_count") or 0) for sid, v in latest_outcomes.items() if isinstance(v, dict)
    }
    insights_map = build_saved_search_insights_map(
        db_path=saved_db,
        job_state_db_path=job_state_db,
        search_ids=[str(s.get("search_id") or "") for s in saved if str(s.get("search_id") or "")],
        indexed_input_path=indexed_input,
        indexed_sqlite_path=sqlite_path,
        user_id=user_id,
        latest_new_by_search=latest_new_by_search,
        scan_limit=200,
    )
    searches_no_recent_new: list[dict[str, str]] = []
    searches_high_dismiss: list[dict[str, str]] = []
    for s in saved:
        sid = str(s.get("search_id") or "")
        if not sid:
            continue
        name = str(s.get("name") or sid)
        insight = insights_map.get(sid, {})
        flags = {str(x) for x in (insight.get("quality_flags") or [])}
        if "no recent new matches" in flags:
            searches_no_recent_new.append(
                {
                    "search_id": sid,
                    "name": name,
                    "reason": "no recent new matches",
                    "priority": "medium",
                    "href": f"/admin/saved-searches/{sid}",
                }
            )
        if "high dismiss rate" in flags:
            searches_high_dismiss.append(
                {
                    "search_id": sid,
                    "name": name,
                    "reason": "high dismiss rate",
                    "priority": "low",
                    "href": f"/admin/saved-searches/{sid}",
                }
            )

    return templates.TemplateResponse(
        request,
        "review.html",
        {
            "stale_saved_jobs": stale_saved_jobs,
            "stale_applied_jobs": stale_applied_jobs,
            "interview_missing_items": interview_missing_items,
            "searches_no_recent_new": searches_no_recent_new[:10],
            "searches_high_dismiss": searches_high_dismiss[:10],
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin/inbox")
def admin_inbox(request: Request):
    indexed_input, saved_db, sqlite_path, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    settings = get_user_settings(db_path=saved_db, user_id=user_id)
    state_filter = (request.query_params.get("state") or "new").strip().lower()
    if state_filter not in {"all", "new", "seen", "saved", "dismissed"}:
        state_filter = "new"
    include_param = request.query_params.get("include_dismissed")
    include_dismissed = _trueish(include_param) if include_param is not None else bool(
        settings.get("include_dismissed_default", True)
    )
    only_remote = _trueish(request.query_params.get("only_remote"))
    only_salary = _trueish(request.query_params.get("only_salary"))
    exclude_other = _trueish(request.query_params.get("exclude_other"))
    only_follow_up_due = _trueish(request.query_params.get("only_follow_up_due"))
    only_follow_up_set = _trueish(request.query_params.get("only_follow_up_set"))
    high_rank_only = _trueish(request.query_params.get("high_rank_only"))
    sort_by = (request.query_params.get("sort_by") or "").strip().lower()
    if sort_by not in {"rank", "newest"}:
        sort_by = "newest" if state_filter == "saved" else "rank"
    limit = max(1, min(500, _safe_int(request.query_params.get("limit"), 100)))
    offset = max(0, _safe_int(request.query_params.get("offset"), 0))
    normalized_title = (request.query_params.get("normalized_title") or "").strip() or None
    role_family = (request.query_params.get("role_family") or "").strip() or None

    rep = list_jobs(
        input_path=indexed_input,
        sqlite_path=sqlite_path,
        query=QueryParams(
            normalized_title=normalized_title,
            role_family=role_family,
            sort_by="published_at_desc",
            limit=None,
        ),
        limit=1_000_000,
        offset=0,
    )
    rows = rep.get("results", [])
    states = get_many_job_states(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in rows if isinstance(r, dict)],
        user_id=user_id,
    )
    clean_rows = [dict(r) for r in rows if isinstance(r, dict)]
    enriched = rank_jobs(
        rows=clean_rows,
        states_by_url=states,
        expected_normalized_title=normalized_title,
        expected_role_family=role_family,
    )

    def matches(item: dict) -> bool:
        current = str(item.get("job_state") or "new")
        if not include_dismissed and current == "dismissed":
            return False
        if state_filter != "all" and current != state_filter:
            return False
        if only_remote and str(item.get("location_type") or "").strip().lower() != "remote":
            return False
        if only_salary and not bool(item.get("has_salary")):
            return False
        if exclude_other and bool(item.get("title_is_other")):
            return False
        if high_rank_only and float(item.get("rank_score") or 0.0) < 35.0:
            return False
        return True

    filtered = [x for x in enriched if matches(x)]
    for item in filtered:
        item["rank_reason"] = _rank_reason(item)
    if sort_by == "newest":
        filtered = sorted(
            filtered,
            key=lambda x: (_parse_iso_ts(str(x.get("published_at") or "")) or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )
    total_count = len(filtered)
    paged = filtered[offset : offset + limit]
    has_saved_searches = len(list_saved_searches(db_path=saved_db, user_id=user_id)) > 0
    has_alert_runs = int(get_alert_runs_summary(runs_dir=runs_dir, user_id=user_id).get("runs_count") or 0) > 0
    counts = {"new": 0, "seen": 0, "saved": 0, "dismissed": 0}
    for x in enriched:
        state = str(x.get("job_state") or "new")
        if state in counts:
            counts[state] += 1

    next_url = str(request.url.path)
    if request.url.query:
        next_url = f"{next_url}?{request.url.query}"

    return templates.TemplateResponse(
        request,
        "inbox.html",
        {
            "rows": paged,
            "state_filter": state_filter,
            "include_dismissed": include_dismissed,
            "only_remote": only_remote,
            "only_salary": only_salary,
            "exclude_other": exclude_other,
            "high_rank_only": high_rank_only,
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset,
            "total_count": total_count,
            "state_counts": counts,
            "normalized_title": normalized_title or "",
            "role_family": role_family or "",
            "next_url": next_url,
            "has_saved_searches": has_saved_searches,
            "has_alert_runs": has_alert_runs,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin/shortlist")
def admin_shortlist(request: Request):
    indexed_input, saved_db, sqlite_path, _ = _state(request)
    user_id, _ = _current_user(request)
    settings = get_user_settings(db_path=saved_db, user_id=user_id)

    sort_by = (request.query_params.get("sort_by") or "rank").strip().lower()
    if sort_by not in {"rank", "newest", "salary"}:
        sort_by = "rank"
    only_remote = _trueish(request.query_params.get("only_remote"))
    only_salary = _trueish(request.query_params.get("only_salary"))
    exclude_other = _trueish(request.query_params.get("exclude_other"))
    only_follow_up_due = _trueish(request.query_params.get("only_follow_up_due"))
    only_follow_up_set = _trueish(request.query_params.get("only_follow_up_set"))
    role_family = (request.query_params.get("role_family") or "").strip() or None
    limit = max(1, min(500, _safe_int(request.query_params.get("limit"), 100)))
    offset = max(0, _safe_int(request.query_params.get("offset"), 0))

    rep = list_jobs(
        input_path=indexed_input,
        sqlite_path=sqlite_path,
        query=QueryParams(
            role_family=role_family,
            sort_by="published_at_desc",
            limit=None,
        ),
        limit=1_000_000,
        offset=0,
    )
    rows = [dict(r) for r in rep.get("results", []) if isinstance(r, dict)]
    states = get_many_job_states(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in rows],
        user_id=user_id,
    )
    ranked = rank_jobs(rows=rows, states_by_url=states, expected_role_family=role_family)
    app_states = get_many_application_states(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in ranked],
        user_id=user_id,
    )
    app_details = get_many_application_details(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in ranked],
        user_id=user_id,
    )
    template_rows = list_application_templates(
        db_path=_job_state_db_path(request),
        user_id=user_id,
        include_inactive=False,
    )
    resume_templates = [str(t.get("label") or "") for t in template_rows if str(t.get("kind") or "") == "resume"]
    cover_letter_templates = [
        str(t.get("label") or "") for t in template_rows if str(t.get("kind") or "") == "cover_letter"
    ]
    pipeline_state = (request.query_params.get("pipeline_state") or "").strip().lower()
    if pipeline_state and pipeline_state not in {"saved", "applied", "interview", "rejected"}:
        pipeline_state = ""

    filtered: list[dict] = []
    for item in ranked:
        if str(item.get("job_state") or "new") != "saved":
            continue
        item_url = str(item.get("url") or "")
        item["application_state"] = app_states.get(item_url, "saved")
        details = app_details.get(item_url, {})
        item["application_notes"] = str(details.get("notes") or "")
        item["applied_at"] = str(details.get("applied_at") or "")
        item["interview_at"] = str(details.get("interview_at") or "")
        item["follow_up_at"] = str(details.get("follow_up_at") or "")
        item["follow_up_note"] = str(details.get("follow_up_note") or "")
        item["application_channel"] = str(details.get("application_channel") or "")
        item["contact_name"] = str(details.get("contact_name") or "")
        item["contact_email"] = str(details.get("contact_email") or "")
        item["compensation_note"] = str(details.get("compensation_note") or "")
        item["external_application_url"] = str(details.get("external_application_url") or "")
        item["resume_label"] = str(details.get("resume_label") or "")
        item["cover_letter_label"] = str(details.get("cover_letter_label") or "")
        item["submission_note"] = str(details.get("submission_note") or "")
        item["follow_up_status"] = _follow_up_status(item["follow_up_at"])
        if pipeline_state and item["application_state"] != pipeline_state:
            continue
        if only_follow_up_set and not item["follow_up_at"]:
            continue
        if only_follow_up_due and item["follow_up_status"] not in {"due", "overdue"}:
            continue
        if only_remote and str(item.get("location_type") or "").strip().lower() != "remote":
            continue
        if only_salary and not bool(item.get("has_salary")):
            continue
        if exclude_other and bool(item.get("title_is_other")):
            continue
        item["rank_reason"] = _rank_reason(item)
        filtered.append(item)

    if sort_by == "newest":
        filtered = sorted(
            filtered,
            key=lambda x: (_parse_iso_ts(str(x.get("published_at") or "")) or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )
    elif sort_by == "salary":
        filtered = sorted(
            filtered,
            key=lambda x: (
                float(x.get("salary_max") or x.get("salary_min") or 0.0),
                float(x.get("rank_score") or 0.0),
            ),
            reverse=True,
        )

    total_count = len(filtered)
    paged = filtered[offset : offset + limit]
    pipeline_counts = count_application_states(
        db_path=_job_state_db_path(request),
        job_urls=[str(x.get("url") or "") for x in filtered],
        user_id=user_id,
    )
    closed_loop = build_closed_loop_metrics(
        db_path=_job_state_db_path(request),
        job_urls=[str(x.get("url") or "") for x in filtered],
        user_id=user_id,
    )
    closed_loop_labels = {
        "saved_to_applied": _pct_label(float(closed_loop["saved_to_applied_rate"])),
        "applied_to_interview": _pct_label(float(closed_loop["applied_to_interview_rate"])),
        "interview_to_rejected": _pct_label(float(closed_loop["interview_to_rejected_rate"])),
    }
    closed_loop_insights: list[str] = [f"You have {int(closed_loop['open_pipeline_count'])} open opportunities."]
    if int(closed_loop["interview_count"]) > 0:
        closed_loop_insights.append(f"{int(closed_loop['interview_count'])} interviews currently active.")
    if int(closed_loop["total_count"]) >= 5 and float(closed_loop["saved_to_applied_rate"]) < 0.2:
        closed_loop_insights.append("High shortlist volume, low applied conversion.")
    next_url = str(request.url.path)
    if request.url.query:
        next_url = f"{next_url}?{request.url.query}"

    return templates.TemplateResponse(
        request,
        "shortlist.html",
        {
            "rows": paged,
            "sort_by": sort_by,
            "only_remote": only_remote,
            "only_salary": only_salary,
            "exclude_other": exclude_other,
            "only_follow_up_due": only_follow_up_due,
            "only_follow_up_set": only_follow_up_set,
            "pipeline_state": pipeline_state,
            "role_family": role_family or "",
            "limit": limit,
            "offset": offset,
            "total_count": total_count,
            "pipeline_counts": pipeline_counts,
            "closed_loop": closed_loop,
            "closed_loop_labels": closed_loop_labels,
            "closed_loop_insights": closed_loop_insights,
            "target_titles": _split_csv(str(settings.get("target_titles") or "")),
            "target_role_families": _split_csv(str(settings.get("target_role_families") or "")),
            "target_locations": _split_csv(str(settings.get("preferred_location_types") or "")),
            "salary_target_note": str(settings.get("salary_target_note") or ""),
            "resume_templates": resume_templates,
            "cover_letter_templates": cover_letter_templates,
            "next_url": next_url,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin/templates")
def admin_templates(request: Request):
    user_id, _ = _current_user(request)
    template_rows = list_application_templates(
        db_path=_job_state_db_path(request),
        user_id=user_id,
        include_inactive=True,
    )
    return templates.TemplateResponse(
        request,
        "templates.html",
        {
            "template_kinds": sorted(APPLICATION_TEMPLATE_KINDS),
            "templates": template_rows,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.post("/admin/templates/new")
async def admin_create_template(request: Request):
    form = await request.form()
    user_id, user_email = _current_user(request)
    kind = str(form.get("kind") or "").strip()
    label = str(form.get("label") or "").strip()
    description = str(form.get("description") or "").strip()
    is_active = _trueish(str(form.get("is_active") or "on"))
    try:
        create_application_template(
            db_path=_job_state_db_path(request),
            kind=kind,
            label=label,
            description=description,
            is_active=is_active,
            user_id=user_id,
            user_email=user_email,
        )
        return _redirect_with_query("/admin/templates", message="Template created")
    except ValueError as exc:
        return _redirect_with_query("/admin/templates", error=str(exc))


@router.post("/admin/templates/{template_id}/enable")
def admin_enable_template(request: Request, template_id: str):
    user_id, _ = _current_user(request)
    try:
        set_application_template_active(
            db_path=_job_state_db_path(request),
            template_id=template_id,
            is_active=True,
            user_id=user_id,
        )
        return _redirect_with_query("/admin/templates", message="Template enabled")
    except ValueError as exc:
        return _redirect_with_query("/admin/templates", error=str(exc))


@router.post("/admin/templates/{template_id}/disable")
def admin_disable_template(request: Request, template_id: str):
    user_id, _ = _current_user(request)
    try:
        set_application_template_active(
            db_path=_job_state_db_path(request),
            template_id=template_id,
            is_active=False,
            user_id=user_id,
        )
        return _redirect_with_query("/admin/templates", message="Template disabled")
    except ValueError as exc:
        return _redirect_with_query("/admin/templates", error=str(exc))


@router.post("/admin/templates/{template_id}/delete")
def admin_delete_template(request: Request, template_id: str):
    user_id, _ = _current_user(request)
    try:
        delete_application_template(
            db_path=_job_state_db_path(request),
            template_id=template_id,
            user_id=user_id,
        )
        return _redirect_with_query("/admin/templates", message="Template deleted")
    except ValueError as exc:
        return _redirect_with_query("/admin/templates", error=str(exc))


@router.get("/admin/exports/shortlist.csv")
def admin_export_shortlist_csv(request: Request):
    indexed_input, _, sqlite_path, _ = _state(request)
    user_id, _ = _current_user(request)

    sort_by = (request.query_params.get("sort_by") or "rank").strip().lower()
    if sort_by not in {"rank", "newest", "salary"}:
        sort_by = "rank"
    only_remote = _trueish(request.query_params.get("only_remote"))
    only_salary = _trueish(request.query_params.get("only_salary"))
    exclude_other = _trueish(request.query_params.get("exclude_other"))
    only_follow_up_due = _trueish(request.query_params.get("only_follow_up_due"))
    only_follow_up_set = _trueish(request.query_params.get("only_follow_up_set"))
    role_family = (request.query_params.get("role_family") or "").strip() or None
    pipeline_state = (request.query_params.get("pipeline_state") or "").strip().lower()
    if pipeline_state and pipeline_state not in {"saved", "applied", "interview", "rejected"}:
        pipeline_state = ""

    rep = list_jobs(
        input_path=indexed_input,
        sqlite_path=sqlite_path,
        query=QueryParams(
            role_family=role_family,
            sort_by="published_at_desc",
            limit=None,
        ),
        limit=1_000_000,
        offset=0,
    )
    rows = [dict(r) for r in rep.get("results", []) if isinstance(r, dict)]
    states = get_many_job_states(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in rows],
        user_id=user_id,
    )
    ranked = rank_jobs(rows=rows, states_by_url=states, expected_role_family=role_family)
    app_states = get_many_application_states(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in ranked],
        user_id=user_id,
    )
    app_details = get_many_application_details(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in ranked],
        user_id=user_id,
    )

    filtered: list[dict] = []
    for item in ranked:
        if str(item.get("job_state") or "new") != "saved":
            continue
        item_url = str(item.get("url") or "")
        item["application_state"] = app_states.get(item_url, "saved")
        details = app_details.get(item_url, {})
        item["application_notes"] = str(details.get("notes") or "")
        item["applied_at"] = str(details.get("applied_at") or "")
        item["interview_at"] = str(details.get("interview_at") or "")
        item["follow_up_at"] = str(details.get("follow_up_at") or "")
        item["application_channel"] = str(details.get("application_channel") or "")
        item["contact_name"] = str(details.get("contact_name") or "")
        item["contact_email"] = str(details.get("contact_email") or "")
        item["compensation_note"] = str(details.get("compensation_note") or "")
        item["external_application_url"] = str(details.get("external_application_url") or "")
        item["resume_label"] = str(details.get("resume_label") or "")
        item["cover_letter_label"] = str(details.get("cover_letter_label") or "")
        item["submission_note"] = str(details.get("submission_note") or "")
        item["follow_up_status"] = _follow_up_status(str(details.get("follow_up_at") or ""))
        if pipeline_state and item["application_state"] != pipeline_state:
            continue
        if only_follow_up_set and not item["follow_up_at"]:
            continue
        if only_follow_up_due and item["follow_up_status"] not in {"due", "overdue"}:
            continue
        if only_remote and str(item.get("location_type") or "").strip().lower() != "remote":
            continue
        if only_salary and not bool(item.get("has_salary")):
            continue
        if exclude_other and bool(item.get("title_is_other")):
            continue
        filtered.append(item)

    if sort_by == "newest":
        filtered = sorted(
            filtered,
            key=lambda x: (_parse_iso_ts(str(x.get("published_at") or "")) or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )
    elif sort_by == "salary":
        filtered = sorted(
            filtered,
            key=lambda x: (
                float(x.get("salary_max") or x.get("salary_min") or 0.0),
                float(x.get("rank_score") or 0.0),
            ),
            reverse=True,
        )

    out = io.StringIO()
    writer = csv.DictWriter(
        out,
        fieldnames=[
            "title",
            "company",
            "url",
            "job_state",
            "application_state",
            "notes",
            "applied_at",
            "interview_at",
            "follow_up_at",
            "application_channel",
            "contact_name",
            "contact_email",
            "compensation_note",
            "external_application_url",
            "resume_label",
            "cover_letter_label",
            "submission_note",
            "rank_score",
            "published_at",
            "role_family",
            "normalized_title",
            "location_type",
            "has_salary",
        ],
    )
    writer.writeheader()
    for row in filtered:
        writer.writerow(
            {
                "title": str(row.get("title_raw") or ""),
                "company": str(row.get("company_name") or row.get("source_org") or ""),
                "url": str(row.get("url") or ""),
                "job_state": str(row.get("job_state") or "new"),
                "application_state": str(row.get("application_state") or "saved"),
                "notes": str(row.get("application_notes") or ""),
                "applied_at": str(row.get("applied_at") or ""),
                "interview_at": str(row.get("interview_at") or ""),
                "follow_up_at": str(row.get("follow_up_at") or ""),
                "application_channel": str(row.get("application_channel") or ""),
                "contact_name": str(row.get("contact_name") or ""),
                "contact_email": str(row.get("contact_email") or ""),
                "compensation_note": str(row.get("compensation_note") or ""),
                "external_application_url": str(row.get("external_application_url") or ""),
                "resume_label": str(row.get("resume_label") or ""),
                "cover_letter_label": str(row.get("cover_letter_label") or ""),
                "submission_note": str(row.get("submission_note") or ""),
                "rank_score": str(row.get("rank_score") or ""),
                "published_at": str(row.get("published_at") or ""),
                "role_family": str(row.get("role_family") or ""),
                "normalized_title": str(row.get("normalized_title") or ""),
                "location_type": str(row.get("location_type") or ""),
                "has_salary": "true" if bool(row.get("has_salary")) else "false",
            }
        )
    content = out.getvalue()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    headers = {"Content-Disposition": f'attachment; filename="shortlist_export_{ts}.csv"'}
    return Response(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/admin/saved-searches")
def admin_saved_searches(request: Request):
    indexed_input, saved_db, sqlite_path, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    lifecycle = (request.query_params.get("lifecycle") or "all").strip().lower() or "all"
    if lifecycle not in {"all", "active", "disabled", "archived"}:
        lifecycle = "all"
    saved = list_saved_searches(db_path=saved_db, user_id=user_id, lifecycle=lifecycle)
    saved_all = list_saved_searches(db_path=saved_db, user_id=user_id, lifecycle="all")
    saved_active = [s for s in saved_all if _is_active_saved_search(s)]
    due_map = {str(s.get("search_id")): is_saved_search_due(s) for s in saved}
    latest_outcomes = _latest_search_outcomes(
        runs_dir=runs_dir,
        user_id=user_id,
        search_ids={str(s.get("search_id") or "") for s in saved_all},
    )
    latest_new_by_search = {
        sid: int(v.get("new_matches_count") or 0) for sid, v in latest_outcomes.items() if isinstance(v, dict)
    }
    insights_map = build_saved_search_insights_map(
        db_path=saved_db,
        job_state_db_path=_job_state_db_path(request),
        search_ids=[str(s.get("search_id") or "") for s in saved if str(s.get("search_id") or "")],
        indexed_input_path=indexed_input,
        indexed_sqlite_path=sqlite_path,
        user_id=user_id,
        latest_new_by_search=latest_new_by_search,
        scan_limit=200,
    )
    settings = get_user_settings(db_path=saved_db, user_id=user_id)
    target_profile = _build_target_profile(settings)
    target_roles = {str(x) for x in list(target_profile.get("target_role_families") or []) if str(x)}
    target_titles = {str(x) for x in list(target_profile.get("target_titles_normalized") or []) if str(x)}
    target_locations = {str(x) for x in list(target_profile.get("preferred_location_types") or []) if str(x)}
    alignment_map = {
        str(s.get("search_id") or ""): _saved_search_alignment(
            saved_search=s,
            target_role_families=target_roles,
            target_titles_normalized=target_titles,
            preferred_location_types=target_locations,
        )
        for s in saved
    }
    strategy_map = {}
    for s in saved:
        sid = str(s.get("search_id") or "")
        strategy_map[sid] = _categorize_saved_search_strategy(
            saved_search=s,
            alignment=alignment_map.get(sid, {}),
            insight=insights_map.get(sid, {}),
        )
    coverage = _build_saved_search_coverage(profile=target_profile, saved_searches=saved_active)
    portfolio = _build_search_portfolio_summary(
        saved_searches=saved_active,
        strategy_map=strategy_map,
        insights_map=insights_map,
        target_profile=target_profile,
    )
    hygiene = _build_search_hygiene_summary(saved_searches=saved_active, insights_map=insights_map)
    return templates.TemplateResponse(
        request,
        "saved_searches.html",
        {
            "saved_searches": saved,
            "due_map": due_map,
            "latest_outcomes": latest_outcomes,
            "insights_map": insights_map,
            "alignment_map": alignment_map,
            "strategy_map": strategy_map,
            "coverage": coverage,
            "portfolio": portfolio,
            "hygiene": hygiene,
            "lifecycle_filter": lifecycle,
            "has_saved_searches": len(saved) > 0,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin/saved-searches/new")
def admin_saved_search_new(request: Request):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    settings = get_user_settings(db_path=saved_db, user_id=user_id)
    target_profile = _build_target_profile(settings)
    use_target_profile = _trueish(request.query_params.get("use_target_profile"))
    name = request.query_params.get("name", "")
    query_type = request.query_params.get("query_type", "filters")
    filters_json = request.query_params.get("filters_json", "")
    if use_target_profile and not str(filters_json).strip():
        filters_json = json.dumps(_default_target_filters(target_profile), ensure_ascii=True)
        if not str(name).strip():
            name = "Target profile search"
        query_type = "filters"
    suggestions = _build_saved_search_suggestions(target_profile)
    return templates.TemplateResponse(
        request,
        "saved_search_new.html",
        {
            "error": request.query_params.get("error"),
            "name": name,
            "query_type": query_type,
            "filters_json": filters_json,
            "pack_name": request.query_params.get("pack_name", ""),
            "frequency": request.query_params.get("frequency", "daily"),
            "is_enabled": request.query_params.get("is_enabled", "true"),
            "use_target_profile": use_target_profile,
            "target_profile": target_profile,
            "suggestions": suggestions,
        },
    )


@router.post("/admin/saved-searches/new")
async def admin_saved_search_create(request: Request):
    _, saved_db, _, _ = _state(request)
    user_id, user_email = _current_user(request)
    form = await request.form()
    name = str(form.get("name") or "").strip()
    query_type = str(form.get("query_type") or "filters").strip()
    filters_json = str(form.get("filters_json") or "").strip() or None
    pack_name = str(form.get("pack_name") or "").strip() or None
    frequency = str(form.get("frequency") or "daily").strip().lower() or "daily"
    is_enabled = str(form.get("is_enabled") or "").strip().lower() in {"1", "true", "yes", "on"}
    try:
        create_saved_search(
            db_path=saved_db,
            name=name,
            query_type=query_type,
            filters_json=filters_json,
            pack_name=pack_name,
            frequency=frequency,
            is_enabled=is_enabled,
            user_id=user_id,
            user_email=user_email,
        )
    except ValueError as exc:
        return _redirect_with_query(
            "/admin/saved-searches/new",
            error=str(exc),
            name=name,
            query_type=query_type,
            filters_json=filters_json or "",
            pack_name=pack_name or "",
            frequency=frequency,
            is_enabled="true" if is_enabled else "false",
        )
    return _redirect_with_query("/admin/saved-searches", message="Saved search created")


@router.post("/admin/saved-searches/{search_id}/enable")
def admin_saved_search_enable(request: Request, search_id: str):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    target = _saved_searches_redirect_target(request)
    try:
        enable_saved_search(db_path=saved_db, search_id=search_id, user_id=user_id)
        return _redirect_with_query(target, message="Saved search enabled")
    except ValueError as exc:
        return _redirect_with_query(target, error=str(exc))


@router.post("/admin/saved-searches/{search_id}/disable")
def admin_saved_search_disable(request: Request, search_id: str):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    target = _saved_searches_redirect_target(request)
    try:
        disable_saved_search(db_path=saved_db, search_id=search_id, user_id=user_id)
        return _redirect_with_query(target, message="Saved search disabled")
    except ValueError as exc:
        return _redirect_with_query(target, error=str(exc))


@router.post("/admin/saved-searches/{search_id}/archive")
def admin_saved_search_archive(request: Request, search_id: str):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    target = _saved_searches_redirect_target(request)
    try:
        archive_saved_search(db_path=saved_db, search_id=search_id, user_id=user_id)
        return _redirect_with_query(
            target,
            message="Saved search archived (excluded from run-due and strategy views)",
        )
    except ValueError as exc:
        return _redirect_with_query(target, error=str(exc))


@router.post("/admin/saved-searches/{search_id}/restore")
def admin_saved_search_restore(request: Request, search_id: str):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    target = _saved_searches_redirect_target(request)
    try:
        restore_saved_search(db_path=saved_db, search_id=search_id, user_id=user_id)
        return _redirect_with_query(
            target,
            message="Saved search restored as disabled (enable it when ready)",
        )
    except ValueError as exc:
        return _redirect_with_query(target, error=str(exc))


@router.post("/admin/saved-searches/{search_id}/run")
def admin_saved_search_run(request: Request, search_id: str):
    indexed_input, saved_db, sqlite_path, _ = _state(request)
    user_id, _ = _current_user(request)
    target = _saved_searches_redirect_target(request)
    try:
        rep = run_saved_search(
            db_path=saved_db,
            search_id=search_id,
            indexed_input_path=indexed_input,
            indexed_sqlite_path=sqlite_path,
            limit=100,
            offset=0,
            user_id=user_id,
        )
        total = int(rep["run_result"].get("total_count") or 0)
        return _redirect_with_query(target, message=f"Run completed: {total} matches")
    except ValueError as exc:
        return _redirect_with_query(target, error=str(exc))


@router.get("/admin/saved-searches/{search_id}")
def admin_saved_search_detail(request: Request, search_id: str):
    indexed_input, saved_db, sqlite_path, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    mode = (request.query_params.get("mode") or "current").strip().lower()
    if mode not in {"current", "new"}:
        mode = "current"
    sort_by = (request.query_params.get("sort_by") or "rank").strip().lower()
    if sort_by not in {"rank", "newest"}:
        sort_by = "rank"
    only_remote = _trueish(request.query_params.get("only_remote"))
    only_salary = _trueish(request.query_params.get("only_salary"))
    exclude_other = _trueish(request.query_params.get("exclude_other"))
    high_rank_only = _trueish(request.query_params.get("high_rank_only"))
    limit = max(1, min(500, _safe_int(request.query_params.get("limit"), 100)))
    offset = max(0, _safe_int(request.query_params.get("offset"), 0))
    scan_limit = max(1, min(100000, _safe_int(request.query_params.get("scan_limit"), 5000)))

    try:
        rep = get_saved_search_results(
            db_path=saved_db,
            search_id=search_id,
            indexed_input_path=indexed_input,
            indexed_sqlite_path=sqlite_path,
            limit=limit,
            offset=offset,
            new_only=(mode == "new"),
            scan_limit=scan_limit,
            user_id=user_id,
        )
    except ValueError as exc:
        return _redirect_with_query("/admin/saved-searches", error=str(exc))

    saved_search = rep["saved_search"]
    is_due = is_saved_search_due(saved_search)
    latest_outcomes = _latest_search_outcomes(
        runs_dir=runs_dir,
        user_id=user_id,
        search_ids={str(saved_search.get("search_id") or "")},
    )
    latest_outcome = latest_outcomes.get(str(saved_search.get("search_id") or ""))
    latest_new_count = None
    if isinstance(latest_outcome, dict):
        latest_new_count = int(latest_outcome.get("new_matches_count") or 0)
    insight = build_saved_search_insight(
        db_path=saved_db,
        job_state_db_path=_job_state_db_path(request),
        search_id=search_id,
        indexed_input_path=indexed_input,
        indexed_sqlite_path=sqlite_path,
        user_id=user_id,
        latest_new_count=latest_new_count,
        scan_limit=500,
    )

    rows = rep.get("results", [])
    states = get_many_job_states(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in rows if isinstance(r, dict)],
        user_id=user_id,
    )
    expected_normalized_title: str | None = None
    expected_role_family: str | None = None
    if isinstance(saved_search.get("filters_json"), str) and str(saved_search.get("filters_json")).strip():
        try:
            f = json.loads(str(saved_search.get("filters_json")))
            if isinstance(f, dict):
                nt = str(f.get("normalized_title") or "").strip()
                rf = str(f.get("role_family") or "").strip()
                expected_normalized_title = nt or None
                expected_role_family = rf or None
        except Exception:
            expected_normalized_title = None
            expected_role_family = None

    enriched = rank_jobs(
        rows=[dict(r) for r in rows if isinstance(r, dict)],
        states_by_url=states,
        expected_normalized_title=expected_normalized_title,
        expected_role_family=expected_role_family,
    )
    filtered: list[dict] = []
    for item in enriched:
        if only_remote and str(item.get("location_type") or "").strip().lower() != "remote":
            continue
        if only_salary and not bool(item.get("has_salary")):
            continue
        if exclude_other and bool(item.get("title_is_other")):
            continue
        if high_rank_only and float(item.get("rank_score") or 0.0) < 35.0:
            continue
        item["rank_reason"] = _rank_reason(item)
        filtered.append(item)
    if sort_by == "newest":
        filtered = sorted(
            filtered,
            key=lambda x: (_parse_iso_ts(str(x.get("published_at") or "")) or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )
    enriched = filtered

    next_url = str(request.url.path)
    if request.url.query:
        next_url = f"{next_url}?{request.url.query}"

    return templates.TemplateResponse(
        request,
        "saved_search_detail.html",
        {
            "saved_search": saved_search,
            "insight": insight,
            "is_due": is_due,
            "latest_outcome": latest_outcome,
            "mode": mode,
            "current_count": rep.get("current_count", 0),
            "new_count": rep.get("new_count"),
            "limit": limit,
            "offset": offset,
            "scan_limit": scan_limit,
            "sort_by": sort_by,
            "only_remote": only_remote,
            "only_salary": only_salary,
            "exclude_other": exclude_other,
            "high_rank_only": high_rank_only,
            "rows": enriched,
            "returned_count": len(enriched),
            "next_url": next_url,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin/saved-searches/{search_id}/edit")
def admin_saved_search_edit(request: Request, search_id: str):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    try:
        saved = get_saved_search(db_path=saved_db, search_id=search_id, user_id=user_id)
    except ValueError as exc:
        return _redirect_with_query("/admin/saved-searches", error=str(exc))
    return templates.TemplateResponse(
        request,
        "saved_search_edit.html",
        {
            "saved_search": saved,
            "error": request.query_params.get("error"),
            "message": request.query_params.get("message"),
        },
    )


@router.post("/admin/saved-searches/{search_id}/edit")
async def admin_saved_search_edit_save(request: Request, search_id: str):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    form = await request.form()
    name = str(form.get("name") or "").strip()
    query_type = str(form.get("query_type") or "filters").strip()
    filters_json = str(form.get("filters_json") or "").strip() or None
    pack_name = str(form.get("pack_name") or "").strip() or None
    frequency = str(form.get("frequency") or "daily").strip().lower() or "daily"
    is_enabled = str(form.get("is_enabled") or "").strip().lower() in {"1", "true", "yes", "on"}
    try:
        update_saved_search(
            db_path=saved_db,
            search_id=search_id,
            name=name,
            query_type=query_type,
            filters_json=filters_json,
            pack_name=pack_name,
            frequency=frequency,
            is_enabled=is_enabled,
            user_id=user_id,
        )
    except ValueError as exc:
        return _redirect_with_query(f"/admin/saved-searches/{search_id}/edit", error=str(exc))
    return _redirect_with_query("/admin/saved-searches", message="Saved search updated")


@router.post("/admin/saved-searches/{search_id}/delete")
def admin_saved_search_delete(request: Request, search_id: str):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    target = _saved_searches_redirect_target(request)
    try:
        delete_saved_search(db_path=saved_db, search_id=search_id, user_id=user_id)
        return _redirect_with_query(target, message="Saved search deleted")
    except ValueError as exc:
        return _redirect_with_query(target, error=str(exc))


@router.get("/admin/alerts")
def admin_alerts(request: Request):
    _, saved_db, _, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    summary = get_alert_runs_summary(runs_dir=runs_dir, user_id=user_id)
    runs = list_alert_runs(runs_dir=runs_dir, user_id=user_id)[:30]
    settings = get_user_settings(db_path=saved_db, user_id=user_id)
    saved = list_saved_searches(db_path=saved_db, user_id=user_id)
    return templates.TemplateResponse(
        request,
        "alerts.html",
        {
            "summary": summary,
            "runs": runs,
            "has_saved_searches": len(saved) > 0,
            "default_alert_email": settings.get("default_alert_email") or "",
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.post("/admin/alerts/run-all")
async def admin_alerts_run_all(request: Request):
    indexed_input, saved_db, sqlite_path, runs_dir = _state(request)
    user_id, user_email = _current_user(request)
    form = await request.form()
    send_email = str(form.get("send_email") or "").strip().lower() in {"1", "true", "yes", "on"}
    email_to = str(form.get("email_to") or "").strip() or None
    rep = run_enabled_saved_searches(
        saved_db_path=saved_db,
        indexed_input_path=indexed_input,
        indexed_sqlite_path=sqlite_path,
        outdir=runs_dir,
        scan_limit=5000,
        return_limit=200,
        sample_size=5,
        user_id=user_id,
        user_email=user_email,
    )
    run_id = str(rep["run_id"])
    query: dict[str, str] = {"message": f"Run completed: {rep['total_new_matches']} new matches"}
    if send_email:
        if not email_to:
            settings = get_user_settings(db_path=saved_db, user_id=user_id)
            email_to = str(settings.get("default_alert_email") or "").strip() or None
        if not email_to:
            query = {
                "message": (
                    f"Run completed: {rep['total_new_matches']} new matches. "
                    "Digest email skipped: set default alert email in Account or enter email_to."
                )
            }
        else:
            try:
                smtp = SMTPConfig.from_env()
                email_rep = send_email_alerts_from_run(
                    run_json_path=rep["json_report_path"],
                    to_email=email_to,
                    smtp_config=smtp,
                )
                persist_email_delivery_to_run(run_json_path=rep["json_report_path"], email_delivery=email_rep)
                query = {
                    "message": (
                        "Run completed. "
                        f"Email attempted={email_rep.get('attempted_count', 0)}, "
                        f"sent={email_rep.get('sent_count', 0)}, "
                        f"skipped={email_rep.get('skipped_count', 0)}, "
                        f"errors={email_rep.get('error_count', 0)}"
                    )
                }
            except ValueError as exc:
                query = {"error": str(exc)}
    return _redirect_with_query(f"/admin/alerts/{run_id}", **query)


@router.get("/admin/account")
def admin_account(request: Request):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    settings = get_user_settings(db_path=saved_db, user_id=user_id)
    return templates.TemplateResponse(
        request,
        "account.html",
        {
            "settings": settings,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.post("/admin/account")
async def admin_account_update(request: Request):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    form = await request.form()
    email = str(form.get("email") or "").strip()
    default_alert_email = str(form.get("default_alert_email") or "").strip() or None
    include_dismissed_default = str(form.get("include_dismissed_default") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    show_saved_search_quality_attention = str(form.get("show_saved_search_quality_attention") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    show_due_saved_search_attention = str(form.get("show_due_saved_search_attention") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    show_follow_up_attention = str(form.get("show_follow_up_attention") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    show_digest_error_attention = str(form.get("show_digest_error_attention") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    digest_include_attention = str(form.get("digest_include_attention") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    target_titles = str(form.get("target_titles") or "")
    target_role_families = str(form.get("target_role_families") or "")
    preferred_location_types = str(form.get("preferred_location_types") or "")
    salary_target_note = str(form.get("salary_target_note") or "")
    keywords_note = str(form.get("keywords_note") or "")
    try:
        settings = update_user_settings(
            db_path=saved_db,
            user_id=user_id,
            email=email,
            default_alert_email=default_alert_email,
            include_dismissed_default=include_dismissed_default,
            show_saved_search_quality_attention=show_saved_search_quality_attention,
            show_due_saved_search_attention=show_due_saved_search_attention,
            show_follow_up_attention=show_follow_up_attention,
            show_digest_error_attention=show_digest_error_attention,
            digest_include_attention=digest_include_attention,
            target_titles=target_titles,
            target_role_families=target_role_families,
            preferred_location_types=preferred_location_types,
            salary_target_note=salary_target_note,
            keywords_note=keywords_note,
        )
    except ValueError as exc:
        return _redirect_with_query("/admin/account", error=str(exc))
    session = request.scope.get("session")
    if isinstance(session, dict):
        session["user_email"] = str(settings["email"])
    return _redirect_with_query("/admin/account", message="Account settings updated")


@router.post("/admin/account/password")
async def admin_account_change_password(request: Request):
    _, saved_db, _, _ = _state(request)
    user_id, _ = _current_user(request)
    form = await request.form()
    current_password = str(form.get("current_password") or "").strip()
    new_password = str(form.get("new_password") or "").strip()
    confirm_password = str(form.get("confirm_password") or "").strip()
    if new_password != confirm_password:
        return _redirect_with_query("/admin/account", error="new password and confirmation do not match")
    try:
        change_local_password(
            db_path=saved_db,
            user_id=user_id,
            current_password=current_password,
            new_password=new_password,
        )
    except ValueError as exc:
        return _redirect_with_query("/admin/account", error=str(exc))
    return _redirect_with_query("/admin/account", message="Password updated")


@router.post("/admin/jobs/state")
async def admin_set_job_state(request: Request):
    form = await request.form()
    user_id, user_email = _current_user(request)
    job_url = str(form.get("job_url") or "").strip()
    state = str(form.get("state") or "").strip()
    next_url = str(form.get("next") or "/admin").strip() or "/admin"
    if not job_url:
        return _redirect_with_query(next_url, error="job_url is required")
    try:
        set_job_state(
            db_path=_job_state_db_path(request),
            job_url=job_url,
            state=state,
            user_id=user_id,
            user_email=user_email,
        )
        return _redirect_with_query(next_url, message=f"Job state updated: {state}")
    except ValueError as exc:
        return _redirect_with_query(next_url, error=str(exc))


@router.post("/admin/jobs/state/clear")
async def admin_clear_job_state(request: Request):
    form = await request.form()
    user_id, _ = _current_user(request)
    job_url = str(form.get("job_url") or "").strip()
    next_url = str(form.get("next") or "/admin").strip() or "/admin"
    if not job_url:
        return _redirect_with_query(next_url, error="job_url is required")
    try:
        clear_job_state(db_path=_job_state_db_path(request), job_url=job_url, user_id=user_id)
        return _redirect_with_query(next_url, message="Job state reset to new")
    except ValueError as exc:
        return _redirect_with_query(next_url, error=str(exc))


@router.post("/admin/shortlist/pipeline")
async def admin_set_pipeline_state(request: Request):
    form = await request.form()
    user_id, user_email = _current_user(request)
    job_url = str(form.get("job_url") or "").strip()
    state = str(form.get("state") or "").strip()
    next_url = str(form.get("next") or "/admin/shortlist").strip() or "/admin/shortlist"
    if not job_url:
        return _redirect_with_query(next_url, error="job_url is required")
    try:
        set_application_state(
            db_path=_job_state_db_path(request),
            job_url=job_url,
            state=state,
            user_id=user_id,
            user_email=user_email,
        )
        return _redirect_with_query(next_url, message=f"Pipeline updated: {state}")
    except ValueError as exc:
        return _redirect_with_query(next_url, error=str(exc))


@router.post("/admin/shortlist/pipeline/clear")
async def admin_clear_pipeline_state(request: Request):
    form = await request.form()
    user_id, _ = _current_user(request)
    job_url = str(form.get("job_url") or "").strip()
    next_url = str(form.get("next") or "/admin/shortlist").strip() or "/admin/shortlist"
    if not job_url:
        return _redirect_with_query(next_url, error="job_url is required")
    try:
        clear_application_state(
            db_path=_job_state_db_path(request),
            job_url=job_url,
            user_id=user_id,
        )
        return _redirect_with_query(next_url, message="Pipeline reset to saved")
    except ValueError as exc:
        return _redirect_with_query(next_url, error=str(exc))


@router.post("/admin/shortlist/details")
async def admin_update_pipeline_details(request: Request):
    form = await request.form()
    user_id, user_email = _current_user(request)
    job_url = str(form.get("job_url") or "").strip()
    notes = str(form.get("notes") or "")
    applied_at = str(form.get("applied_at") or "").strip()
    interview_at = str(form.get("interview_at") or "").strip()
    follow_up_at = str(form.get("follow_up_at") or "").strip()
    follow_up_note = str(form.get("follow_up_note") or "")
    application_channel = str(form.get("application_channel") or "")
    contact_name = str(form.get("contact_name") or "")
    contact_email = str(form.get("contact_email") or "")
    compensation_note = str(form.get("compensation_note") or "")
    external_application_url = str(form.get("external_application_url") or "")
    resume_template_label = str(form.get("resume_template_label") or "").strip()
    cover_letter_template_label = str(form.get("cover_letter_template_label") or "").strip()
    resume_label = str(form.get("resume_label") or "")
    cover_letter_label = str(form.get("cover_letter_label") or "")
    submission_note = str(form.get("submission_note") or "")
    if not str(resume_label).strip():
        resume_label = resume_template_label
    if not str(cover_letter_label).strip():
        cover_letter_label = cover_letter_template_label
    next_url = str(form.get("next") or "/admin/shortlist").strip() or "/admin/shortlist"
    if not job_url:
        return _redirect_with_query(next_url, error="job_url is required")
    try:
        update_application_details(
            db_path=_job_state_db_path(request),
            job_url=job_url,
            notes=notes,
            applied_at=applied_at,
            interview_at=interview_at,
            follow_up_at=follow_up_at,
            follow_up_note=follow_up_note,
            application_channel=application_channel,
            contact_name=contact_name,
            contact_email=contact_email,
            compensation_note=compensation_note,
            external_application_url=external_application_url,
            resume_label=resume_label,
            cover_letter_label=cover_letter_label,
            submission_note=submission_note,
            user_id=user_id,
            user_email=user_email,
        )
        return _redirect_with_query(next_url, message="Application details updated")
    except ValueError as exc:
        return _redirect_with_query(next_url, error=str(exc))


@router.post("/admin/shortlist/details/clear")
async def admin_clear_pipeline_details(request: Request):
    form = await request.form()
    user_id, _ = _current_user(request)
    job_url = str(form.get("job_url") or "").strip()
    next_url = str(form.get("next") or "/admin/shortlist").strip() or "/admin/shortlist"
    if not job_url:
        return _redirect_with_query(next_url, error="job_url is required")
    try:
        clear_application_details(
            db_path=_job_state_db_path(request),
            job_url=job_url,
            user_id=user_id,
        )
        return _redirect_with_query(next_url, message="Application details cleared")
    except ValueError as exc:
        return _redirect_with_query(next_url, error=str(exc))


@router.get("/admin/alerts/{run_id}")
def admin_alert_detail(request: Request, run_id: str):
    _, _, _, runs_dir = _state(request)
    user_id, _ = _current_user(request)
    try:
        detail = get_alert_run_detail(runs_dir=runs_dir, run_id=run_id, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    samples: list[dict] = []
    for item in detail.get("results", []):
        if not isinstance(item, dict):
            continue
        for row in item.get("sample_new_matches", []):
            if isinstance(row, dict):
                samples.append(row)
    states_by_url = get_many_job_states(
        db_path=_job_state_db_path(request),
        job_urls=[str(r.get("url") or "") for r in samples],
        user_id=user_id,
    )
    return templates.TemplateResponse(
        request,
        "alert_detail.html",
        {
            "run": detail,
            "states_by_url": states_by_url,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )
