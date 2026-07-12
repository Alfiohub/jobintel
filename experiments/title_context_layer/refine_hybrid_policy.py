from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_json, repo_root, write_json


PRIORITY_TITLES = ["Onboarding Specialist", "Partner Manager", "Producer"]

PROMOTION_POLICY = {
    "Onboarding Specialist": {
        "safe_family": "customer_success",
        "min_dominant_share": 0.8,
        "min_high_conf_examples": 2,
        "conflict_families": {"people_operations", "compliance_risk"},
        "recommended_target": ("customer_success_manager", "customer_success"),
        "promotion_type": "tight_rule_candidate",
    },
    "Partner Manager": {
        "safe_family": "sales",
        "min_dominant_share": 0.8,
        "min_high_conf_examples": 2,
        "conflict_families": {"people_operations", "operations"},
        "recommended_target": ("account_manager", "sales"),
        "promotion_type": "tight_rule_candidate",
    },
    "Producer": {
        "safe_family": "content",
        "min_dominant_share": 0.85,
        "min_high_conf_examples": 3,
        "conflict_families": {"software_engineering", "operations"},
        "recommended_target": ("content_producer", "content"),
        "promotion_type": "tight_rule_candidate",
    },
}


def _review_cluster(rows: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    total = len(rows)
    fam_counter: Counter[str] = Counter()
    high_conf_counter: Counter[str] = Counter()
    for row in rows:
        fam = str(row.get("top_context_family") or "none")
        fam_counter[fam] += 1
        if str(row.get("context_confidence")) == "high":
            high_conf_counter[fam] += 1

    dominant_family, dominant_count = fam_counter.most_common(1)[0] if fam_counter else ("none", 0)
    dominant_share = (dominant_count / total) if total else 0.0
    high_conf_examples = high_conf_counter.get(policy["safe_family"], 0)
    conflicting_examples = sum(fam_counter.get(fam, 0) for fam in policy["conflict_families"])

    ready = (
        dominant_family == policy["safe_family"]
        and dominant_share >= policy["min_dominant_share"]
        and high_conf_examples >= policy["min_high_conf_examples"]
    )
    if ready and conflicting_examples > max(1, total // 5):
        ready = False

    decision = "ready_for_tight_rule" if ready else "review_only_keep_context"
    return {
        "dominant_family": dominant_family,
        "dominant_count": dominant_count,
        "dominant_share": round(dominant_share, 4),
        "high_conf_examples_for_safe_family": high_conf_examples,
        "conflicting_examples": conflicting_examples,
        "decision": decision,
        "recommended_target_label": policy["recommended_target"][0],
        "recommended_target_family": policy["recommended_target"][1],
        "promotion_type": policy["promotion_type"],
    }


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# Phase 11.2 — Context Scoring Refinement")
    lines.append("")
    lines.append("## Priority Titles")
    for item in payload["clusters"]:
        lines.append(f"### `{item['title_clean']}`")
        lines.append(f"- volume: `{item['volume']}`")
        lines.append(f"- dominant family: `{item['dominant_family']}`")
        lines.append(f"- dominant share: `{item['dominant_share']}`")
        lines.append(f"- high-confidence examples: `{item['high_conf_examples_for_safe_family']}`")
        lines.append(f"- conflicting examples: `{item['conflicting_examples']}`")
        lines.append(f"- recommended target: `{item['recommended_target_label']}/{item['recommended_target_family']}`")
        lines.append(f"- decision: `{item['decision']}`")
        lines.append("- sample evidence:")
        for ex in item["examples"]:
            lines.append(
                f"  - `{ex['company_name']}` | family `{ex['top_context_family']}` | conf `{ex['context_confidence']}` | score `{ex['top_context_score']}` | url `{ex['url']}`"
            )
        lines.append("")
    lines.append("## Final Recommendation")
    lines.append(f"- `{payload['final_recommendation']['decision']}`")
    lines.append(f"- reason: {payload['final_recommendation']['reason']}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refine_hybrid_policy(review_path: Path, scores_path: Path, out_path: Path) -> dict[str, Any]:
    review = read_json(review_path)
    scores = read_json(scores_path)
    rows = scores["rows"]
    by_title: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        title = str(row.get("title_clean") or "")
        if title in PRIORITY_TITLES:
            by_title[title].append(row)

    clusters: list[dict[str, Any]] = []
    ready_count = 0
    for title in PRIORITY_TITLES:
        title_rows = by_title.get(title, [])
        policy = PROMOTION_POLICY[title]
        reviewed = _review_cluster(title_rows, policy)
        examples = []
        for row in title_rows[:3]:
            examples.append(
                {
                    "url": row.get("url"),
                    "company_name": row.get("company_name"),
                    "top_context_family": row.get("top_context_family"),
                    "top_context_score": row.get("top_context_score"),
                    "context_confidence": row.get("context_confidence"),
                }
            )
        item = {
            "title_clean": title,
            "volume": len(title_rows),
            **reviewed,
            "examples": examples,
        }
        if item["decision"] == "ready_for_tight_rule":
            ready_count += 1
        clusters.append(item)

    final_decision = (
        "ready_for_context_gated_rule_design" if ready_count >= 2 else "context_signal_still_reviewer_only"
    )
    final_reason = (
        "At least two priority ambiguous titles have dominant context families strong enough to justify drafting future gated production rules."
        if final_decision == "ready_for_context_gated_rule_design"
        else "Context helps triage, but the signal is still too mixed for drafting safe context-gated rules."
    )

    payload = {
        "priority_titles": PRIORITY_TITLES,
        "clusters": clusters,
        "final_recommendation": {"decision": final_decision, "reason": final_reason},
    }
    write_json(out_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    payload = refine_hybrid_policy(
        review_path=reports / "hybrid_review_v1.json",
        scores_path=reports / "context_signal_scores_v1.json",
        out_path=reports / "hybrid_policy_refinement_v1.json",
    )
    render_markdown(payload, root / "docs/phase_e5_hybrid_policy_refinement_v1.md")
    print(payload["final_recommendation"])
