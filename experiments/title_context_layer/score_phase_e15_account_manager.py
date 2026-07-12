from __future__ import annotations

from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_jsonl, repo_root, write_json, write_jsonl
try:
    from experiments.title_context_layer.report_utils import lane_metadata
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from report_utils import lane_metadata


TITLE_POSITIVE_PATTERNS = {
    "partner_growth_manager": ["partner growth manager"],
    "partner_development_manager": ["partner development manager"],
    "client_strategy": ["client strategist", "manager client strategy", "manager, client strategy"],
    "client_partnership_specialist": ["client partnership specialist"],
    "partner_director": ["partner director"],
    "charter_partnerships_manager": ["charter partnerships manager"],
}

POSITIVE_TERMS = [
    "pipeline",
    "bookings",
    "revenue",
    "growth",
    "grow a named portfolio",
    "portfolio of existing",
    "merchant acquisition",
    "go-to-market",
    "upsell",
    "new business",
    "account expansion",
    "trusted partner",
    "strategic advisor",
    "brand accounts",
    "client growth",
    "partnerships",
    "partner relationships",
]

NEGATIVE_TERMS = [
    "employee",
    "people partner",
    "hr",
    "onboarding",
    "implementation",
    "provider",
    "patient",
    "clinical",
    "network development",
]

POSITIVE_DEPT_TERMS = [
    "sales",
    "business development",
    "alliances",
    "client strategy",
]


def _contains_any(text: str, patterns: list[str]) -> int:
    lower = text.lower()
    return sum(1 for pattern in patterns if pattern in lower)


def _department_text(row: dict[str, Any]) -> str:
    parts = []
    for item in row.get("departments_raw") or []:
        name = str(item.get("name") or "").strip()
        if name:
            parts.append(name)
    return " | ".join(parts)


def _focus_text(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("title_clean") or ""),
        _department_text(row),
        str(row.get("responsibilities_clean") or ""),
    ]
    return " ".join(part for part in parts if part).strip()


def _title_bucket(title: str) -> tuple[str, int]:
    lower = title.lower()
    for bucket, patterns in TITLE_POSITIVE_PATTERNS.items():
        if any(pattern in lower for pattern in patterns):
            return bucket, 2
    return "other", 0


def score_phase_e15_account_manager(joined_path: Path, out_json: Path, promotable_jsonl: Path, review_jsonl: Path) -> dict[str, Any]:
    rows = [row for row in read_jsonl(joined_path) if row.get("context_cluster") == "account_manager"]
    scored_rows: list[dict[str, Any]] = []
    promotable_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []

    for row in rows:
        title = str(row.get("title_clean") or "")
        context_text = str(row.get("context_text") or "")
        dept_text = _department_text(row)
        focus_text = _focus_text(row)
        title_bucket, title_score = _title_bucket(title)
        positive_score = _contains_any(context_text, POSITIVE_TERMS)
        dept_score = _contains_any(dept_text, POSITIVE_DEPT_TERMS)
        negative_score = _contains_any(focus_text, NEGATIVE_TERMS)

        total_score = title_score + positive_score + dept_score - negative_score
        if title_score >= 2 and positive_score >= 2 and negative_score == 0:
            decision = "promotable"
        elif title_score >= 2 and total_score >= 3:
            decision = "review_only"
        else:
            decision = "exclude"

        scored = {
            **row,
            "title_bucket": title_bucket,
            "positive_score": positive_score,
            "dept_score": dept_score,
            "negative_score": negative_score,
            "total_score": total_score,
            "decision": decision,
            "recommended_target_label": "account_manager" if decision != "exclude" else None,
            "recommended_role_family": "sales" if decision != "exclude" else None,
        }
        scored_rows.append(scored)
        if decision == "promotable":
            promotable_rows.append(scored)
        elif decision == "review_only":
            review_rows.append(scored)

    payload = {
        "lane_metadata": lane_metadata(
            lane_name="account_manager_context_lane",
            lane_type="recoverable_with_context",
            target_label="account_manager",
            target_family="sales",
            promotable_rows=promotable_rows,
            review_only_rows=review_rows,
            excluded_rows=[row for row in scored_rows if row["decision"] == "exclude"],
        ),
        "joined_rows": len(rows),
        "promotable_count": len(promotable_rows),
        "review_only_count": len(review_rows),
        "excluded_count": len(rows) - len(promotable_rows) - len(review_rows),
        "top_promotable_titles": _top_titles(promotable_rows),
        "top_review_titles": _top_titles(review_rows),
        "decision": (
            "ready_for_account_manager_shadow_batch"
            if len(promotable_rows) >= 15
            else "review_only_keep_context"
        ),
        "rows": scored_rows,
    }

    write_json(out_json, payload)
    write_jsonl(promotable_jsonl, promotable_rows)
    write_jsonl(review_jsonl, review_rows)
    return payload


def _top_titles(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        title = str(row.get("title_clean") or "")
        counts[title] = counts.get(title, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12])


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    payload = score_phase_e15_account_manager(
        joined_path=reports / "phase_e15_context_join_v1.jsonl",
        out_json=reports / "phase_e15_account_manager_scoring_v1.json",
        promotable_jsonl=reports / "phase_e15_account_manager_promotable_v1.jsonl",
        review_jsonl=reports / "phase_e15_account_manager_review_only_v1.jsonl",
    )
    print(
        {
            "promotable_count": payload["promotable_count"],
            "review_only_count": payload["review_only_count"],
            "decision": payload["decision"],
        }
    )
