from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_json, read_jsonl, repo_root, write_json


TITLE_POLICY: dict[str, dict[str, str]] = {
    "Onboarding Specialist": {
        "customer_success": "needs_tighter_rule",
        "people_operations": "needs_context_not_title_only",
        "compliance_risk": "needs_context_not_title_only",
    },
    "Implementation Engineer": {
        "software_engineering": "needs_tighter_rule",
        "customer_success": "needs_context_not_title_only",
        "sales": "keep_other_for_now",
    },
    "Partner Manager": {
        "sales": "needs_tighter_rule",
        "operations": "needs_context_not_title_only",
        "people_operations": "keep_other_for_now",
    },
    "Producer": {
        "content": "needs_tighter_rule",
        "software_engineering": "needs_context_not_title_only",
        "operations": "keep_other_for_now",
    },
    "Designer": {
        "design": "needs_tighter_rule",
        "marketing": "needs_context_not_title_only",
        "product_management": "keep_other_for_now",
    },
    "Operations Analyst": {
        "operations": "needs_context_not_title_only",
        "data_analytics": "needs_tighter_rule",
        "compliance_risk": "keep_other_for_now",
    },
}


def _top_examples(rows: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    out = []
    for row in rows[:limit]:
        out.append(
            {
                "url": row.get("url"),
                "company_name": row.get("company_name"),
                "top_context_family": row.get("top_context_family"),
                "top_context_score": row.get("top_context_score"),
                "context_confidence": row.get("context_confidence"),
                "departments_raw": row.get("departments_raw"),
                "skills": row.get("skills"),
            }
        )
    return out


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# Phase 11.1 — Hybrid Title + Context Pilot Review")
    lines.append("")
    lines.append("## Pilot Summary")
    lines.append(f"- joined rows: `{payload['summary']['joined_rows']}`")
    lines.append(f"- target titles: `{', '.join(payload['summary']['target_titles'])}`")
    lines.append("")
    lines.append("## Cluster Review")
    for item in payload["clusters"]:
        lines.append(f"### `{item['title_clean']}`")
        lines.append(f"- volume: `{item['volume']}`")
        lines.append(f"- dominant context family: `{item['dominant_context_family']}`")
        lines.append(f"- dominant family count: `{item['dominant_count']}`")
        lines.append(f"- recommended action: `{item['recommended_action']}`")
        lines.append(f"- rationale: {item['rationale']}")
        lines.append("- sample evidence:")
        for ex in item["examples"]:
            lines.append(
                f"  - `{ex['company_name']}` | family `{ex['top_context_family']}` | conf `{ex['context_confidence']}` | score `{ex['top_context_score']}` | url `{ex['url']}`"
            )
        lines.append("")
    lines.append("## Recommendation")
    lines.append(f"- `{payload['final_recommendation']['decision']}`")
    lines.append(f"- reason: {payload['final_recommendation']['reason']}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def review_hybrid_candidates(joined_path: Path, scores_path: Path, out_path: Path) -> dict[str, Any]:
    joined_rows = read_jsonl(joined_path)
    scored = read_json(scores_path)
    scored_rows = scored["rows"]
    by_title: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        by_title[str(row.get("title_clean") or "")].append(row)

    clusters: list[dict[str, Any]] = []
    for title, rows in sorted(by_title.items()):
        fam_counts: dict[str, int] = defaultdict(int)
        for row in rows:
            if row.get("top_context_family"):
                fam_counts[str(row["top_context_family"])] += 1
        dominant_family, dominant_count = max(fam_counts.items(), key=lambda x: x[1]) if fam_counts else ("none", 0)
        action = TITLE_POLICY.get(title, {}).get(dominant_family, "keep_other_for_now")
        rationale = (
            f"context repeatedly points to `{dominant_family}`"
            if dominant_family != "none"
            else "no stable context family emerged"
        )
        clusters.append(
            {
                "title_clean": title,
                "volume": len(rows),
                "dominant_context_family": dominant_family,
                "dominant_count": dominant_count,
                "recommended_action": action,
                "examples": _top_examples(rows),
                "rationale": rationale,
            }
        )

    shortlisted = [c for c in clusters if c["recommended_action"] in {"needs_tighter_rule", "needs_context_not_title_only"}]
    decision = (
        "ready_for_hybrid_pilot"
        if len([c for c in shortlisted if c["recommended_action"] == "needs_tighter_rule"]) >= 2
        else "hybrid_signal_present_but_review_only"
    )
    reason = (
        "At least two ambiguous title families now show repeated context patterns that could support a future gated rule."
        if decision == "ready_for_hybrid_pilot"
        else "Context adds value, but current outputs should remain reviewer-only until explicit promotion policy is defined."
    )

    payload = {
        "summary": {
            "joined_rows": len(joined_rows),
            "target_titles": sorted(by_title.keys()),
        },
        "clusters": clusters,
        "final_recommendation": {"decision": decision, "reason": reason},
    }
    write_json(out_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    payload = review_hybrid_candidates(
        joined_path=reports / "context_join_v1.jsonl",
        scores_path=reports / "context_signal_scores_v1.json",
        out_path=reports / "hybrid_review_v1.json",
    )
    render_markdown(payload, root / "docs/phase_e5_hybrid_context_pilot_v1.md")
    print(payload["final_recommendation"])
