from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def count_statuses(dataset_path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    with dataset_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            status = str(row.get("classification_status") or "").strip() or "missing"
            counts[status] = counts.get(status, 0) + 1
    return counts


def top_items(items: list[dict[str, Any]], key: str, limit: int = 5) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: int(item.get(key) or 0), reverse=True)[:limit]


def build_orchestrator_payload() -> dict[str, Any]:
    baseline_dataset = REPO_ROOT / "data/jobs/jobs_titled_en_recovery_v66_partner_lane_candidate.jsonl"
    baseline_counts = count_statuses(baseline_dataset)

    hardening = read_json(
        REPO_ROOT / "experiments/title_context_layer/reports/phase_e16_engine_hardening_v1.json"
    )
    recoverability = read_json(REPO_ROOT / "experiments/residual_audit/reports/recoverability_backlog_v1.json")
    shortlist = read_json(REPO_ROOT / "experiments/residual_audit/reports/phase_e10_next_batch_shortlist_v1.json")
    non_role_shadow = read_json(REPO_ROOT / "experiments/residual_audit/reports/non_role_macroclass_shadow_v1.json")
    non_role_official = read_json(
        REPO_ROOT / "experiments/residual_audit/reports/phase_e18_non_role_official_rerun_v1.json"
    )
    partner_review = read_json(
        REPO_ROOT / "experiments/title_context_layer/reports/phase_e15_partner_lane_formal_review_v1.json"
    )
    partner_acceptance = read_json(
        REPO_ROOT / "experiments/title_context_layer/reports/phase_e19_partner_lane_acceptance_v1.json"
    )
    account_review = read_json(
        REPO_ROOT / "experiments/title_context_layer/reports/phase_e15_account_manager_formal_review_v1.json"
    )
    taxonomy_decision = read_json(
        REPO_ROOT / "experiments/residual_audit/reports/phase_e12_taxonomy_decision_draft_v1.json"
    )
    account_scoring = read_json(
        REPO_ROOT / "experiments/title_context_layer/reports/phase_e15_account_manager_scoring_v1.json"
    )
    partner_refinement = read_json(
        REPO_ROOT / "experiments/title_context_layer/reports/phase_e15_partner_lane_refinement_v1.json"
    )

    attack_now_candidates = []
    for item in top_items(recoverability["attack_now"], "projected_residual_volume", limit=8):
        attack_now_candidates.append(
            {
                "lane_type": "attack_now",
                "target_label": item["target_label"],
                "projected_residual_volume": item["projected_residual_volume"],
                "count_in_sample": item["count_in_sample"],
                "status": "candidate",
                "examples": item.get("example_titles", [])[:4],
            }
        )

    context_candidates = [
        {
            "lane_type": "recoverable_with_context",
            "lane_name": "partner_lane_context_lane",
            "target_label": "account_manager",
            "target_family": "sales",
            "status": partner_review["decision"],
            "shadow_delta_other": partner_review["shadow_delta_other"],
            "risk": partner_review["risk"],
            "recommendation": partner_review["recommendation"],
            "concentration": partner_refinement["lane_metadata"]["concentration"],
        },
        {
            "lane_type": "recoverable_with_context",
            "lane_name": "account_manager_context_lane",
            "target_label": "account_manager",
            "target_family": "sales",
            "status": account_review["decision"],
            "shadow_delta_other": account_review["shadow_delta_other"],
            "risk": account_scoring["lane_metadata"]["risk_level"],
            "recommendation": account_review["recommendation"],
            "concentration": account_scoring["lane_metadata"]["concentration"],
        },
    ]

    taxonomy_candidates = []
    for item in taxonomy_decision["approved_candidates"]:
        taxonomy_candidates.append(
            {
                "lane_type": "taxonomy_gap",
                "target_label": item["normalized_title"],
                "target_family": item["role_family"],
                "status": item["status"],
            }
        )
    for item in taxonomy_decision["deferred"]:
        taxonomy_candidates.append(
            {
                "lane_type": "taxonomy_gap",
                "target_label": item["normalized_title"],
                "target_family": None,
                "status": item["status"],
            }
        )

    return {
        "phase": "E.20",
        "decision": "orchestrator_v2_ready",
        "baseline": {
            "dataset": str(baseline_dataset.relative_to(REPO_ROOT)),
            "rows_total": sum(baseline_counts.values()),
            "counts_by_status": baseline_counts,
            "other": baseline_counts.get("other", 0),
        },
        "engine_hardening": hardening,
        "lanes": {
            "non_role": {
                "lane_type": "non_role",
                "status": "completed_official",
                "candidate_count_shadow": non_role_shadow["shadow_result"]["non_role_total"],
                "from_other_shadow": non_role_shadow["shadow_result"]["from_other"],
                "from_matched_shadow": non_role_shadow["shadow_result"]["from_matched"],
                "delta_other_shadow": non_role_shadow["shadow_result"]["delta_other"],
                "official_dataset": non_role_official["official_rerun"]["dataset"],
                "official_delta_other": non_role_official["delta_vs_v61"]["other"],
            },
            "attack_now": {
                "lane_type": "attack_now",
                "status": "active",
                "top_candidates": attack_now_candidates,
            },
            "recoverable_with_context": {
                "lane_type": "recoverable_with_context",
                "status": "active",
                "top_candidates": [
                    {
                        "lane_type": "recoverable_with_context",
                        "lane_name": "partner_lane_context_lane",
                        "target_label": "account_manager",
                        "target_family": "sales",
                        "status": partner_acceptance["decision"],
                        "shadow_delta_other": partner_review["shadow_delta_other"],
                        "official_delta_other": partner_acceptance["delta"]["other"],
                        "risk": partner_review["risk"],
                        "recommendation": "accepted_precision_first_leave_stable",
                        "concentration": partner_refinement["lane_metadata"]["concentration"],
                    },
                    context_candidates[1],
                ],
            },
            "taxonomy_gap": {
                "lane_type": "taxonomy_gap",
                "status": "active",
                "top_candidates": taxonomy_candidates,
            },
        },
        "recommended_execution_order": [
            {
                "step": 1,
                "action": "rerank_attack_now_from_v66",
                "why": "Non-role and partner-lane gains are already absorbed into the current baseline.",
            },
            {
                "step": 2,
                "action": "reopen_next_context_lane",
                "why": "Partner lane is now accepted; the next context opportunity should be selected from the remaining residual.",
            },
            {
                "step": 3,
                "action": "taxonomy_patch_followup_rules",
                "why": "Quantitative researcher and credit analyst now have official taxonomy support but still need exploitation rules.",
            },
            {
                "step": 4,
                "action": "refresh_residual_audit_only_if_signal_shifts",
                "why": "A new broad audit is not needed immediately; reuse the existing discipline unless the residual profile materially changes.",
            },
        ],
        "source_reports": {
            "recoverability_backlog": str(
                (REPO_ROOT / "experiments/residual_audit/reports/recoverability_backlog_v1.json").relative_to(REPO_ROOT)
            ),
            "next_batch_shortlist": str(
                (REPO_ROOT / "experiments/residual_audit/reports/phase_e10_next_batch_shortlist_v1.json").relative_to(REPO_ROOT)
            ),
            "non_role_shadow": str(
                (REPO_ROOT / "experiments/residual_audit/reports/non_role_macroclass_shadow_v1.json").relative_to(REPO_ROOT)
            ),
            "partner_lane_review": str(
                (REPO_ROOT / "experiments/title_context_layer/reports/phase_e15_partner_lane_formal_review_v1.json").relative_to(REPO_ROOT)
            ),
            "account_lane_review": str(
                (REPO_ROOT / "experiments/title_context_layer/reports/phase_e15_account_manager_formal_review_v1.json").relative_to(REPO_ROOT)
            ),
            "taxonomy_decision": str(
                (REPO_ROOT / "experiments/residual_audit/reports/phase_e12_taxonomy_decision_draft_v1.json").relative_to(REPO_ROOT)
            ),
        },
    }


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    baseline = payload["baseline"]
    lines = [
        "# Phase E.20 — Residual Recovery Orchestrator v2",
        "",
        "## Goal",
        "Rerun the orchestrator on the current baseline after official non-role promotion and partner-lane acceptance.",
        "",
        "## Baseline",
        f"- dataset: `{baseline['dataset']}`",
        f"- rows_total: `{baseline['rows_total']}`",
        f"- other: `{baseline['other']}`",
        "",
        "## Lane Status",
        f"- non_role: `{payload['lanes']['non_role']['status']}`",
        f"- attack_now: `{payload['lanes']['attack_now']['status']}`",
        f"- recoverable_with_context: `{payload['lanes']['recoverable_with_context']['status']}`",
        f"- taxonomy_gap: `{payload['lanes']['taxonomy_gap']['status']}`",
        "",
        "## Non-Role",
        f"- candidate_count_shadow: `{payload['lanes']['non_role']['candidate_count_shadow']}`",
        f"- from_other_shadow: `{payload['lanes']['non_role']['from_other_shadow']}`",
        f"- from_matched_shadow: `{payload['lanes']['non_role']['from_matched_shadow']}`",
        f"- delta_other_shadow: `{payload['lanes']['non_role']['delta_other_shadow']}`",
        f"- official_delta_other: `{payload['lanes']['non_role']['official_delta_other']}`",
        "",
        "## Top Attack-Now Candidates",
    ]
    for item in payload["lanes"]["attack_now"]["top_candidates"]:
        lines.append(
            f"- `{item['target_label']}` | projected `{item['projected_residual_volume']}` | sample `{item['count_in_sample']}`"
        )
    lines += ["", "## Top Context Candidates"]
    for item in payload["lanes"]["recoverable_with_context"]["top_candidates"]:
        lines.append(
            f"- `{item['lane_name']}` -> `{item['target_label']}/{item['target_family']}` | "
            f"status `{item['status']}` | shadow `{item['shadow_delta_other']}`"
            + (f" | official `{item['official_delta_other']}`" if 'official_delta_other' in item else "")
            + f" | risk `{item['risk']}`"
        )
    lines += ["", "## Taxonomy Candidates"]
    for item in payload["lanes"]["taxonomy_gap"]["top_candidates"]:
        lines.append(
            f"- `{item['target_label']}` | family `{item['target_family']}` | status `{item['status']}`"
        )
    lines += ["", "## Recommended Execution Order"]
    for item in payload["recommended_execution_order"]:
        lines.append(f"- step {item['step']}: `{item['action']}` | {item['why']}")
    lines += [
        "",
        "## Recommendation",
        f"- `{payload['decision']}`",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_orchestrator_payload()
    json_path = REPO_ROOT / "experiments/residual_audit/reports/phase_e20_residual_recovery_orchestrator_v2.json"
    md_path = REPO_ROOT / "docs/phase_e20_residual_recovery_orchestrator_v2.md"
    write_json(json_path, payload)
    render_markdown(payload, md_path)
    print(
        {
            "decision": payload["decision"],
            "baseline_other": payload["baseline"]["other"],
            "top_context_lane": payload["lanes"]["recoverable_with_context"]["top_candidates"][0]["lane_name"],
        }
    )


if __name__ == "__main__":
    main()
