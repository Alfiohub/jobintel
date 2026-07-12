from __future__ import annotations

from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_json, write_json, write_jsonl
try:
    from experiments.title_context_layer.report_utils import lane_metadata
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from report_utils import lane_metadata


ALLOWED_TITLE_BUCKETS = {
    "partner_growth_manager",
    "partner_development_manager",
    "partner_director",
}

ALLOWED_DEPT_TERMS = [
    "sales",
    "alliances",
    "partner",
    "partnership",
]

BLOCKED_TITLE_TERMS = [
    "client",
    "provider",
    "charter",
]

BLOCKED_RESP_TERMS = [
    "provider",
    "patient",
    "clinical",
    "education",
    "district",
]


def _dept_text(row: dict[str, Any]) -> str:
    return " | ".join(str(item.get("name") or "") for item in (row.get("departments_raw") or []))


def _contains_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def refine_phase_e15_partner_lane(
    scoring_path: Path,
    out_json: Path,
    promotable_path: Path,
    review_path: Path,
) -> dict[str, Any]:
    payload = read_json(scoring_path)
    rows = payload["rows"]

    promotable: list[dict[str, Any]] = []
    review_only: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for row in rows:
        title = str(row.get("title_clean") or "")
        responsibilities = str(row.get("responsibilities_clean") or "")
        dept_text = _dept_text(row)
        title_bucket = str(row.get("title_bucket") or "")
        positive_score = int(row.get("positive_score") or 0)
        negative_score = int(row.get("negative_score") or 0)

        if title_bucket not in ALLOWED_TITLE_BUCKETS:
            excluded.append({**row, "partner_lane_decision": "exclude_non_partner_bucket"})
            continue
        if _contains_any(title, BLOCKED_TITLE_TERMS):
            excluded.append({**row, "partner_lane_decision": "exclude_blocked_title"})
            continue
        if _contains_any(responsibilities, BLOCKED_RESP_TERMS):
            excluded.append({**row, "partner_lane_decision": "exclude_blocked_context"})
            continue

        dept_ok = _contains_any(dept_text, ALLOWED_DEPT_TERMS)
        if positive_score >= 3 and negative_score <= 1 and dept_ok:
            promotable.append({**row, "partner_lane_decision": "promotable_partner_lane"})
        elif positive_score >= 3 and negative_score <= 1:
            review_only.append({**row, "partner_lane_decision": "review_missing_partner_dept"})
        else:
            excluded.append({**row, "partner_lane_decision": "exclude_low_signal"})

    result = {
        "lane_metadata": lane_metadata(
            lane_name="partner_lane_context_lane",
            lane_type="recoverable_with_context",
            target_label="account_manager",
            target_family="sales",
            promotable_rows=promotable,
            review_only_rows=review_only,
            excluded_rows=excluded,
        ),
        "source_promotable_count": payload["promotable_count"],
        "source_review_only_count": payload["review_only_count"],
        "partner_lane_promotable_count": len(promotable),
        "partner_lane_review_only_count": len(review_only),
        "partner_lane_excluded_count": len(excluded),
        "top_promotable_titles": _top_titles(promotable),
        "top_review_titles": _top_titles(review_only),
        "decision": (
            "ready_for_partner_shadow_batch_v2"
            if len(promotable) >= 15
            else "partner_lane_still_too_small"
        ),
    }

    write_json(out_json, result)
    write_jsonl(promotable_path, promotable)
    write_jsonl(review_path, review_only)
    return result


def _top_titles(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        title = str(row.get("title_clean") or "")
        counts[title] = counts.get(title, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12])


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    reports = root / "experiments/title_context_layer/reports"
    result = refine_phase_e15_partner_lane(
        scoring_path=reports / "phase_e15_account_manager_scoring_v1.json",
        out_json=reports / "phase_e15_partner_lane_refinement_v1.json",
        promotable_path=reports / "phase_e15_partner_lane_promotable_v1.jsonl",
        review_path=reports / "phase_e15_partner_lane_review_only_v1.jsonl",
    )
    print(result)
