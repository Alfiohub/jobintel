from __future__ import annotations

from typing import Any

from jobintel_next.domain.models import (
    CanonicalRawJob,
    CleanedJob,
    ExtractedAttributes,
    LanguageDecision,
    TitleClassification,
)
from jobintel_next.pipelines.language.io import row_to_canonical as _row_to_canonical
from jobintel_next.pipelines.titles.io import row_to_cleaned as _row_to_cleaned
from jobintel_next.pipelines.titles.io import row_to_extracted as _row_to_extracted


def row_to_canonical(row: dict[str, Any]) -> CanonicalRawJob | None:
    return _row_to_canonical(row)


def row_to_language_decision(row: dict[str, Any]) -> LanguageDecision | None:
    url = str(row.get("url") or "").strip()
    bucket = str(row.get("language_bucket") or "").strip()
    reason = str(row.get("language_reason") or "").strip()
    if not (url and bucket and reason):
        return None
    if bucket not in {"en", "non_en", "unknown"}:
        return None

    language_code = str(row.get("language_code") or "").strip() or None
    confidence_raw = row.get("language_confidence")
    confidence: float | None = None
    if isinstance(confidence_raw, (int, float)):
        confidence = float(confidence_raw)

    return LanguageDecision(
        url=url,
        bucket=bucket,  # type: ignore[arg-type]
        reason=reason,
        language_code=language_code,
        confidence=confidence,
    )


def row_to_cleaned(row: dict[str, Any]) -> CleanedJob | None:
    return _row_to_cleaned(row)


def row_to_extracted(row: dict[str, Any]) -> ExtractedAttributes | None:
    return _row_to_extracted(row)


def row_to_title_classification(row: dict[str, Any]) -> TitleClassification | None:
    url = str(row.get("url") or "").strip()
    normalized_title = str(row.get("normalized_title") or "").strip()
    role_family = str(row.get("role_family") or "").strip()
    classification_status = str(row.get("classification_status") or "").strip()
    match_method = str(row.get("match_method") or "").strip()
    confidence_raw = row.get("confidence")

    if not (url and normalized_title and role_family and classification_status and match_method):
        return None
    if classification_status not in {"matched", "fallback", "other", "non_role"}:
        return None
    if match_method not in {"rule_exact", "rule_pattern", "fallback", "manual_override"}:
        return None
    if not isinstance(confidence_raw, (int, float)):
        return None

    notes = row.get("notes") if isinstance(row.get("notes"), list) else []

    return TitleClassification(
        url=url,
        normalized_title=normalized_title,
        role_family=role_family,
        classification_status=classification_status,  # type: ignore[arg-type]
        match_method=match_method,  # type: ignore[arg-type]
        confidence=float(confidence_raw),
        matched_rule_id=str(row.get("matched_rule_id") or "").strip() or None,
        notes=[str(n) for n in notes],
    )
