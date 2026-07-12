from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from jobintel_next.domain.models import CanonicalRawJob


def map_greenhouse_job_to_canonical(*, board: str, payload: dict[str, Any]) -> CanonicalRawJob | None:
    """Single source of truth for Greenhouse -> CanonicalRawJob mapping."""
    title = str(payload.get("title") or "").strip()
    url = str(payload.get("absolute_url") or "").strip()
    if not title or not url:
        return None

    company_from_payload = str(payload.get("company_name") or "").strip()
    company_name = company_from_payload or board

    external_id = str(payload.get("id") or "").strip() or None

    location_raw: str | None = None
    raw_location = payload.get("location")
    if isinstance(raw_location, dict):
        location_raw = str(raw_location.get("name") or "").strip() or None
    elif isinstance(raw_location, str):
        location_raw = raw_location.strip() or None

    published_raw = str(payload.get("first_published") or "").strip()
    updated_raw = str(payload.get("updated_at") or "").strip()

    published_at = _to_utc_iso(published_raw) if published_raw else None
    updated_at = _to_utc_iso(updated_raw) if updated_raw else None

    language = payload.get("language")
    language_hint = str(language).strip() if isinstance(language, str) else None

    description_raw = payload.get("content")
    description_value = description_raw.strip() if isinstance(description_raw, str) and description_raw.strip() else None

    departments_raw = payload.get("departments") if isinstance(payload.get("departments"), list) else None
    offices_raw = payload.get("offices") if isinstance(payload.get("offices"), list) else None

    return CanonicalRawJob(
        source="greenhouse",
        source_org=board,
        url=url,
        title=title,
        company_name=company_name,
        raw_payload=dict(payload),
        external_id=external_id,
        location_raw=location_raw,
        published_at=published_at,
        updated_at=updated_at,
        language_hint=language_hint,
        description_raw=description_value,
        departments_raw=departments_raw,
        offices_raw=offices_raw,
    )


def _to_utc_iso(value: str) -> str | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return None
