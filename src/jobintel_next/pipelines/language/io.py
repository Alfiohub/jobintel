from __future__ import annotations

from typing import Any

from jobintel_next.domain.models import CanonicalRawJob


def row_to_canonical(row: dict[str, Any]) -> CanonicalRawJob | None:
    raw_payload = row.get("raw_payload") if isinstance(row.get("raw_payload"), dict) else {}

    source = str(row.get("source") or "").strip()
    source_org = str(row.get("source_org") or "").strip()
    url = str(row.get("url") or "").strip()
    title = str(row.get("title") or "").strip()
    company_name = str(row.get("company_name") or raw_payload.get("company_name") or source_org).strip()

    if not (source and source_org and url and title and company_name):
        return None

    description_raw = row.get("description_raw")
    if not isinstance(description_raw, str) or not description_raw.strip():
        content = raw_payload.get("content")
        description_raw = content if isinstance(content, str) else None

    departments_raw = row.get("departments_raw")
    if not isinstance(departments_raw, list):
        departments_raw = raw_payload.get("departments") if isinstance(raw_payload.get("departments"), list) else None

    offices_raw = row.get("offices_raw")
    if not isinstance(offices_raw, list):
        offices_raw = raw_payload.get("offices") if isinstance(raw_payload.get("offices"), list) else None

    return CanonicalRawJob(
        source=source,
        source_org=source_org,
        url=url,
        title=title,
        company_name=company_name,
        raw_payload=raw_payload,
        external_id=str(row.get("external_id") or "").strip() or None,
        location_raw=str(row.get("location_raw") or "").strip() or None,
        published_at=str(row.get("published_at") or row.get("posted_at") or "").strip() or None,
        updated_at=str(row.get("updated_at") or "").strip() or None,
        language_hint=str(row.get("language_hint") or row.get("language") or "").strip() or None,
        description_raw=description_raw,
        departments_raw=departments_raw,
        offices_raw=offices_raw,
    )

