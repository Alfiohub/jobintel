from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_json, read_jsonl, repo_root, write_json, write_jsonl


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# Phase E.15.2 — Account Manager Shadow Batch v1")
    lines.append("")
    lines.append("## Baseline")
    lines.append(f"- input dataset: `{payload['baseline']['dataset']}`")
    lines.append(f"- other before: `{payload['baseline']['other_before']}`")
    lines.append("")
    lines.append("## Shadow Result")
    lines.append(f"- shadow matches added: `{payload['shadow_result']['matches_added']}`")
    lines.append(f"- other after shadow: `{payload['shadow_result']['other_after']}`")
    lines.append(f"- delta other: `{payload['shadow_result']['delta_other']}`")
    lines.append("")
    lines.append("## Sample Matches")
    for row in payload["sample_matches"]:
        lines.append(
            f"- `{row['title_clean']}` | target `{row['normalized_title']}/{row['role_family']}` | url `{row['url']}`"
        )
    lines.append("")
    lines.append("## Recommendation")
    lines.append(f"- `{payload['final_recommendation']['decision']}`")
    lines.append(f"- reason: {payload['final_recommendation']['reason']}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_phase_e15_account_manager_shadow_batch(
    titled_path: Path,
    promotable_path: Path,
    out_jsonl: Path,
    out_report: Path,
) -> dict[str, Any]:
    approved_urls = {row["url"] for row in read_jsonl(promotable_path)}

    titled_rows = read_jsonl(titled_path)
    out_rows: list[dict[str, Any]] = []
    sample_matches: list[dict[str, Any]] = []
    rule_hits: Counter[str] = Counter()
    matches_added = 0

    for row in titled_rows:
        out_row = dict(row)
        if row.get("classification_status") == "other" and row.get("url") in approved_urls:
            out_row["normalized_title"] = "account_manager"
            out_row["role_family"] = "sales"
            out_row["classification_status"] = "matched"
            out_row["match_method"] = "context_shadow_rule"
            out_row["matched_rule_id"] = "ctx_account_manager_lane_v1"
            out_row["confidence"] = 0.8
            out_row["notes"] = list(out_row.get("notes") or []) + ["phase_e15_account_manager_shadow_match"]
            matches_added += 1
            rule_hits["ctx_account_manager_lane_v1"] += 1
            if len(sample_matches) < 12:
                sample_matches.append(
                    {
                        "url": row.get("url"),
                        "title_clean": row.get("title_clean"),
                        "normalized_title": out_row["normalized_title"],
                        "role_family": out_row["role_family"],
                    }
                )
        out_rows.append(out_row)

    write_jsonl(out_jsonl, out_rows)

    other_before = sum(1 for row in titled_rows if row.get("classification_status") == "other")
    other_after = sum(1 for row in out_rows if row.get("classification_status") == "other")
    payload = {
        "baseline": {
            "dataset": str(titled_path.relative_to(repo_root())),
            "other_before": other_before,
        },
        "shadow_result": {
            "output_dataset": str(out_jsonl.relative_to(repo_root())),
            "matches_added": matches_added,
            "other_after": other_after,
            "delta_other": other_after - other_before,
            "rule_hits": dict(rule_hits),
        },
        "sample_matches": sample_matches,
    }

    decision = "account_manager_shadow_lane_viable" if matches_added >= 15 else "account_manager_shadow_lane_needs_more_work"
    reason = (
        "The partner/client-strategy subset produces enough shadow matches to justify formal review for a production-candidate context gate."
        if decision == "account_manager_shadow_lane_viable"
        else "Signal exists, but the account-manager subset is still too small for the next production-candidate review."
    )
    payload["final_recommendation"] = {"decision": decision, "reason": reason}
    write_json(out_report, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    payload = run_phase_e15_account_manager_shadow_batch(
        titled_path=root / "data/jobs/jobs_titled_en_recovery_v61_attack_now_batch.jsonl",
        promotable_path=reports / "phase_e15_account_manager_promotable_v1.jsonl",
        out_jsonl=root / "data/jobs/jobs_titled_en_recovery_v62_account_manager_shadow.jsonl",
        out_report=reports / "phase_e15_account_manager_shadow_batch_v1.json",
    )
    render_markdown(payload, root / "docs/phase_e15_account_manager_shadow_batch_v1.md")
    print(payload["final_recommendation"])
