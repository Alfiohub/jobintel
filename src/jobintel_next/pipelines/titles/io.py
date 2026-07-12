from __future__ import annotations

from typing import Any

from jobintel_next.domain.models import CleanedJob, ExtractedAttributes


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


def row_to_extracted(row: dict[str, Any]) -> ExtractedAttributes | None:
    url = str(row.get("url") or "").strip()
    if not url:
        return None
    skills = row.get("skills")
    tags = row.get("tags")
    return ExtractedAttributes(
        url=url,
        seniority=row.get("seniority"),
        employment_type=row.get("employment_type"),
        location_type=row.get("location_type"),
        city=row.get("city"),
        region=row.get("region"),
        country=row.get("country"),
        salary_min=row.get("salary_min"),
        salary_max=row.get("salary_max"),
        salary_currency=row.get("salary_currency"),
        salary_period=row.get("salary_period"),
        skills=skills if isinstance(skills, list) else [],
        tags=tags if isinstance(tags, dict) else {},
    )

