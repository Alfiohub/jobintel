from __future__ import annotations

from typing import Any

from jobintel_next.domain.models import CleanedJob


def row_to_cleaned(row: dict[str, Any]) -> CleanedJob | None:
    url = str(row.get("url") or "").strip()
    title_clean = str(row.get("title_clean") or "").strip()
    description_clean = str(row.get("description_clean") or "").strip()
    if not (url and title_clean):
        return None
    return CleanedJob(
        url=url,
        title_clean=title_clean,
        description_clean=description_clean,
        location_clean=str(row.get("location_clean") or "").strip(),
        requirements_clean=str(row.get("requirements_clean") or "").strip(),
        responsibilities_clean=str(row.get("responsibilities_clean") or "").strip(),
        content_hash=str(row.get("content_hash") or "").strip() or None,
    )

