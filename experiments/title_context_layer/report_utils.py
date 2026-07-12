from __future__ import annotations

from collections import Counter
from typing import Any


def top_counts(rows: list[dict[str, Any]], key: str, limit: int = 8) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        value = str(row.get(key) or "").strip()
        if value:
            counts[value] += 1
    return dict(counts.most_common(limit))


def concentration_metrics(
    rows: list[dict[str, Any]],
    *,
    title_key: str = "title_clean",
    company_key: str = "company_name",
) -> dict[str, Any]:
    title_counts = Counter(str(row.get(title_key) or "").strip() for row in rows if str(row.get(title_key) or "").strip())
    company_counts = Counter(str(row.get(company_key) or "").strip() for row in rows if str(row.get(company_key) or "").strip())
    total = len(rows)
    top_title = title_counts.most_common(1)[0] if title_counts else ("", 0)
    top_company = company_counts.most_common(1)[0] if company_counts else ("", 0)
    return {
        "rows": total,
        "unique_titles": len(title_counts),
        "unique_companies": len(company_counts),
        "top_title": {"value": top_title[0] or None, "count": top_title[1], "share": round(top_title[1] / total, 4) if total else 0.0},
        "top_company": {"value": top_company[0] or None, "count": top_company[1], "share": round(top_company[1] / total, 4) if total else 0.0},
        "top_titles": dict(title_counts.most_common(8)),
        "top_companies": dict(company_counts.most_common(8)),
    }


def risk_level_for_lane(
    *,
    promotable_count: int,
    review_only_count: int,
    excluded_count: int,
    concentration: dict[str, Any],
) -> str:
    total = promotable_count + review_only_count + excluded_count
    review_share = (review_only_count / total) if total else 0.0
    top_title_share = float(concentration.get("top_title", {}).get("share") or 0.0)
    top_company_share = float(concentration.get("top_company", {}).get("share") or 0.0)

    if promotable_count < 10 or top_title_share >= 0.55 or top_company_share >= 0.55:
        return "high"
    if review_share >= 0.45 or top_title_share >= 0.4 or top_company_share >= 0.4:
        return "medium"
    if review_share >= 0.2 or top_title_share >= 0.25 or top_company_share >= 0.25:
        return "medium-low"
    return "low"


def lane_metadata(
    *,
    lane_name: str,
    lane_type: str,
    target_label: str,
    target_family: str,
    promotable_rows: list[dict[str, Any]],
    review_only_rows: list[dict[str, Any]] | None = None,
    excluded_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    review_rows = review_only_rows or []
    excluded = excluded_rows or []
    concentration = concentration_metrics(promotable_rows)
    return {
        "lane_name": lane_name,
        "lane_type": lane_type,
        "target_label": target_label,
        "target_family": target_family,
        "promotable_count": len(promotable_rows),
        "review_only_count": len(review_rows),
        "excluded_count": len(excluded),
        "concentration": concentration,
        "risk_level": risk_level_for_lane(
            promotable_count=len(promotable_rows),
            review_only_count=len(review_rows),
            excluded_count=len(excluded),
            concentration=concentration,
        ),
    }
