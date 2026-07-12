from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import read_json, repo_root, write_json


# Focused gap list from E.1 reviewer outcomes and obvious internal-target mismatches.
GAP_CLUSTER_CONFIG: dict[str, dict[str, Any]] = {
    "salesforce_administrator": {
        "decision": "map_to_existing_label",
        "target_label": "it_support_specialist",
        "target_family": "it_operations",
        "confidence": "high",
        "issue_type": "internal_candidate_incoherent",
        "explanation": "Current internal suggestion points to education (`school_administrator`), but title semantics are clearly IT admin/ops.",
    },
    "onboarding_specialist": {
        "decision": "needs_context_not_title_only",
        "target_label": None,
        "target_family": None,
        "confidence": "medium",
        "issue_type": "cross_domain_title",
        "explanation": "Onboarding spans customer success, compliance, operations, and HR; title-only mapping is unstable.",
    },
    "data_science_manager": {
        "decision": "new_label_worth_adding",
        "target_label": "data_science_manager",
        "target_family": "data_science",
        "confidence": "medium",
        "issue_type": "missing_managerial_label",
        "explanation": "Internal candidate (`story_editor`) is clearly wrong; recurring managerial DS titles indicate taxonomy gap.",
    },
    "software_development_manager": {
        "decision": "map_to_existing_label",
        "target_label": "engineering_manager",
        "target_family": "software_engineering",
        "confidence": "high",
        "issue_type": "existing_label_not_retrieved",
        "explanation": "Canonical `engineering_manager` already exists and is semantically aligned.",
    },
    "production_engineer": {
        "decision": "map_to_existing_label",
        "target_label": "manufacturing_engineer",
        "target_family": "industrial_engineering",
        "confidence": "medium",
        "issue_type": "internal_candidate_incoherent",
        "explanation": "Current internal suggestion (`sales_engineer`) is off-domain; industrial/manufacturing family is closer.",
    },
    "fpga_engineer": {
        "decision": "map_to_existing_label",
        "target_label": "electrical_engineer",
        "target_family": "industrial_engineering",
        "confidence": "medium",
        "issue_type": "internal_candidate_incoherent",
        "explanation": "FPGA role is hardware/electrical oriented; current `ml_engineer` suggestion is weak.",
    },
    "it_administrator": {
        "decision": "map_to_existing_label",
        "target_label": "it_support_specialist",
        "target_family": "it_operations",
        "confidence": "medium",
        "issue_type": "existing_label_not_retrieved",
        "explanation": "Current `school_administrator` retrieval is noisy; IT admin maps better to IT operations.",
    },
    "technical_architect": {
        "decision": "map_to_existing_label",
        "target_label": "solutions_architect",
        "target_family": "architecture",
        "confidence": "medium",
        "issue_type": "existing_label_not_retrieved",
        "explanation": "Current internal suggestion is misaligned (`technical_recruiter`); architecture label exists.",
    },
    "procurement_manager": {
        "decision": "taxonomy_merge_or_cleanup_needed",
        "target_label": "procurement_manager",
        "target_family": "logistics",
        "confidence": "medium",
        "issue_type": "taxonomy_granularity_gap",
        "explanation": "Recurring procurement management titles are real but currently forced into unrelated labels.",
    },
    "partner_manager": {
        "decision": "needs_context_not_title_only",
        "target_label": None,
        "target_family": None,
        "confidence": "low",
        "issue_type": "ambiguous_title_family",
        "explanation": "`Partner Manager` spans sales, alliances, people, and channel operations; title-only is insufficient.",
    },
    "sales_representative": {
        "decision": "taxonomy_merge_or_cleanup_needed",
        "target_label": "sales_representative",
        "target_family": "sales",
        "confidence": "medium",
        "issue_type": "core_sales_label_missing",
        "explanation": "High-frequency generic sales title lacks a clean canonical destination without forcing BDR/AE.",
    },
    "operations_analyst": {
        "decision": "needs_context_not_title_only",
        "target_label": None,
        "target_family": None,
        "confidence": "medium",
        "issue_type": "analytics_vs_operations_overlap",
        "explanation": "Can map to data analytics, finance ops, biz ops depending on context not present in title.",
    },
    "designer": {
        "decision": "keep_other_by_policy",
        "target_label": None,
        "target_family": None,
        "confidence": "high",
        "issue_type": "too_generic",
        "explanation": "Naked `designer` remains too broad (product, visual, motion, industrial, etc.).",
    },
    "engineer": {
        "decision": "keep_other_by_policy",
        "target_label": None,
        "target_family": None,
        "confidence": "high",
        "issue_type": "too_generic",
        "explanation": "Naked `engineer` is historically high-risk and not suitable for safe promotion.",
    },
}


def _pick_rows(reviewer_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    index = {row.get("cluster_name", ""): row for row in reviewer_rows}
    selected = []
    for cluster_name, cfg in GAP_CLUSTER_CONFIG.items():
        row = index.get(cluster_name)
        if not row:
            continue
        selected.append(
            {
                "cluster_name": cluster_name,
                "representative_titles": row.get("representative_titles", [])[:5],
                "estimated_volume": row.get("estimated_volume", 0),
                "current_internal_candidate": row.get("top_internal_candidate", {}),
                "top_esco_candidate": row.get("top_esco_candidate", {}),
                "top_onet_candidate": row.get("top_onet_candidate", {}),
                "support_strength": row.get("support_strength", "none"),
                "semantic_confidence": row.get("semantic_confidence", "low"),
                "semantic_confidence_score": row.get("semantic_confidence_score", 0.0),
                "issue_type": cfg["issue_type"],
                "short_explanation": cfg["explanation"],
                "recommended_decision": cfg["decision"],
                "proposed_target_label": cfg["target_label"],
                "proposed_role_family": cfg["target_family"],
                "decision_confidence": cfg["confidence"],
            }
        )
    selected.sort(key=lambda x: x["estimated_volume"], reverse=True)
    return selected


def run_taxonomy_gap_review(root: Path) -> dict[str, Any]:
    phase_e1 = read_json(root / "experiments/title_semantic_layer/reports/phase_e1_reviewer_safe_batch.json")
    reviewer_rows = phase_e1.get("reviewer_table", [])
    baseline = phase_e1.get("baseline", {})

    inventory = _pick_rows(reviewer_rows)

    # Priority shortlist (max 10) by value/risk balance and actionable taxonomy value.
    priority_order = [
        "salesforce_administrator",
        "software_development_manager",
        "production_engineer",
        "fpga_engineer",
        "it_administrator",
        "technical_architect",
        "data_science_manager",
        "sales_representative",
        "procurement_manager",
        "onboarding_specialist",
    ]
    inv_map = {x["cluster_name"]: x for x in inventory}
    priority = [inv_map[name] for name in priority_order if name in inv_map][:10]

    for item in priority:
        decision = item["recommended_decision"]
        vol = int(item.get("estimated_volume", 0))
        if decision in {"map_to_existing_label", "taxonomy_merge_or_cleanup_needed"} and vol >= 10:
            expected_value = "high"
        elif decision in {"new_label_worth_adding", "needs_context_not_title_only"} and vol >= 10:
            expected_value = "medium"
        else:
            expected_value = "low"

        risk = "low" if decision == "map_to_existing_label" else "medium" if decision in {"new_label_worth_adding", "taxonomy_merge_or_cleanup_needed"} else "high" if decision == "keep_other_by_policy" else "medium"

        item["expected_value"] = expected_value
        item["risk"] = risk
        item["why_now"] = (
            "High-volume cluster with wrong current internal target; fixing taxonomy decision improves future semantic routing."
            if expected_value == "high"
            else "Material ambiguity currently blocks safe promotion and keeps semantic reviewer conservative."
        )

    counts = {
        "map_to_existing_label": 0,
        "new_label_worth_adding": 0,
        "keep_other_by_policy": 0,
        "needs_context_not_title_only": 0,
        "taxonomy_merge_or_cleanup_needed": 0,
    }
    for row in inventory:
        counts[row["recommended_decision"]] += 1

    # Final strategy decision
    if counts["needs_context_not_title_only"] >= 3 and counts["taxonomy_merge_or_cleanup_needed"] >= 2:
        decision = "need_hybrid_title_plus_context_design"
        reason = "A meaningful portion of residual gaps are not pure taxonomy misses: they need context signals alongside targeted taxonomy cleanup."
    elif counts["new_label_worth_adding"] + counts["taxonomy_merge_or_cleanup_needed"] >= 4:
        decision = "taxonomy_ready_for_targeted_expansion"
        reason = "Several high-value clusters point to concrete taxonomy additions/cleanup with manageable risk."
    elif counts["map_to_existing_label"] >= 6:
        decision = "taxonomy_mostly_ok_semantics_need_better_context"
        reason = "Most issues are retrieval/mapping quality, not missing taxonomy surface."
    else:
        decision = "keep_taxonomy_stable_and_accept_residual"
        reason = "Gaps are mostly ambiguous or low-value; taxonomy expansion would add noise."

    payload = {
        "baseline": {
            "repo": "joballert2",
            "dataset": baseline.get("dataset", "data/jobs/jobs_titled_en_recovery_v53_safe.jsonl"),
            "rows_total": baseline.get("rows_total", 0),
            "other_baseline": baseline.get("other_baseline", 0),
            "status": baseline.get("status", "unknown"),
        },
        "taxonomy_gap_inventory": inventory,
        "taxonomy_decision_table": inventory,
        "priority_shortlist": priority,
        "taxonomy_review_summary": {
            "true_taxonomy_gaps": counts["new_label_worth_adding"] + counts["taxonomy_merge_or_cleanup_needed"],
            "title_only_ambiguity": counts["needs_context_not_title_only"],
            "keep_other_by_policy": counts["keep_other_by_policy"],
            "resolvable_with_existing_labels": counts["map_to_existing_label"],
            "decision_counts": counts,
        },
        "final_recommendation": {
            "decision": decision,
            "reason": reason,
        },
    }

    write_json(root / "experiments/title_semantic_layer/reports/phase_e2_taxonomy_gap_review.json", payload)
    return payload


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    b = payload["baseline"]
    inventory = payload["taxonomy_gap_inventory"]
    priority = payload["priority_shortlist"]
    summary = payload["taxonomy_review_summary"]
    rec = payload["final_recommendation"]

    lines: list[str] = []
    lines.append("# Fase E.2 — Taxonomy Gap Review mirata")
    lines.append("")
    lines.append("## A. Baseline confirmation")
    lines.append(f"- repo: `{b['repo']}`")
    lines.append(f"- dataset: `{b['dataset']}`")
    lines.append(f"- total rows: `{b['rows_total']}`")
    lines.append(f"- other baseline: `{b['other_baseline']}`")
    lines.append(f"- status: `{b['status']}`")

    lines.append("")
    lines.append("## B. Taxonomy gap inventory")
    for i, row in enumerate(inventory, 1):
        reps = "; ".join(f"{x['title']} ({x['count']})" for x in row["representative_titles"][:3])
        cur = row["current_internal_candidate"]
        lines.append(
            f"{i}. `{row['cluster_name']}` | reps: {reps} | current internal `{cur.get('label','')}/{cur.get('role_family','')}` ({cur.get('score',0)}) | issue `{row['issue_type']}` | {row['short_explanation']}"
        )

    lines.append("")
    lines.append("## C. Taxonomy decision table")
    for i, row in enumerate(inventory, 1):
        target = (
            f"`{row['proposed_target_label']}/{row['proposed_role_family']}`"
            if row.get("proposed_target_label")
            else "`n/a`"
        )
        lines.append(
            f"{i}. `{row['cluster_name']}` | decision `{row['recommended_decision']}` | target {target} | confidence `{row['decision_confidence']}` | rationale: {row['short_explanation']}"
        )

    lines.append("")
    lines.append("## D. Priority shortlist (max 10)")
    for i, row in enumerate(priority, 1):
        lines.append(
            f"{i}. `{row['cluster_name']}` | action `{row['recommended_decision']}` | expected value `{row['expected_value']}` | risk `{row['risk']}` | why now: {row['why_now']}"
        )

    lines.append("")
    lines.append("## E. Taxonomy review summary")
    lines.append(f"- true taxonomy gaps: `{summary['true_taxonomy_gaps']}`")
    lines.append(f"- title-only ambiguity: `{summary['title_only_ambiguity']}`")
    lines.append(f"- keep_other_by_policy: `{summary['keep_other_by_policy']}`")
    lines.append(f"- resolvable with existing labels: `{summary['resolvable_with_existing_labels']}`")
    lines.append(f"- decision counts: `{summary['decision_counts']}`")

    lines.append("")
    lines.append("## F. Final recommendation")
    lines.append(f"- `{rec['decision']}`")
    lines.append(f"- reason: {rec['reason']}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = repo_root()
    payload = run_taxonomy_gap_review(root)
    render_markdown(payload, root / "docs/title_semantic_layer_phase_e2_taxonomy_gap_review.md")
    print("report_json=experiments/title_semantic_layer/reports/phase_e2_taxonomy_gap_review.json")
    print("report_md=docs/title_semantic_layer_phase_e2_taxonomy_gap_review.md")
