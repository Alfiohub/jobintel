from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from experiments.title_context_layer.shadow_context_rules import decide_context_rule
from experiments.title_semantic_layer.common import read_jsonl, repo_root, write_json, write_jsonl


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# Phase 11.5 — Shadow Context-Gated Rules Tuning")
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
    lines.append("## Rule Hits")
    for rule_id, count in payload["shadow_result"]["rule_hits"].items():
        lines.append(f"- `{rule_id}`: `{count}`")
    lines.append("")
    lines.append("## Sample Matches")
    for row in payload["sample_matches"]:
        lines.append(
            f"- `{row['title_clean']}` | target `{row['normalized_title']}/{row['role_family']}` | rule `{row['matched_rule_id']}` | evidence `{', '.join(row['evidence_hits'])}` | exclusions `{', '.join(row['exclusion_hits']) if row['exclusion_hits'] else 'none'}`"
        )
    lines.append("")
    lines.append("## Excluded Samples")
    for row in payload["excluded_examples"]:
        lines.append(
            f"- `{row['title_clean']}` | evidence `{', '.join(row['evidence_hits']) if row['evidence_hits'] else 'none'}` | exclusions `{', '.join(row['exclusion_hits']) if row['exclusion_hits'] else 'none'}`"
        )
    lines.append("")
    lines.append("## Recommendation")
    lines.append(f"- `{payload['final_recommendation']['decision']}`")
    lines.append(f"- reason: {payload['final_recommendation']['reason']}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_shadow_context_batch(
    titled_path: Path,
    context_join_path: Path,
    out_jsonl: Path,
    out_report: Path,
) -> dict[str, Any]:
    titled_rows = read_jsonl(titled_path)
    context_rows = {row["url"]: row for row in read_jsonl(context_join_path)}

    out_rows: list[dict[str, Any]] = []
    matches_added = 0
    rule_hits: Counter[str] = Counter()
    sample_matches: list[dict[str, Any]] = []
    excluded_examples: list[dict[str, Any]] = []

    for row in titled_rows:
        out_row = dict(row)
        if row.get("classification_status") == "other" and row.get("url") in context_rows:
            ctx_row = context_rows[str(row["url"])]
            decision = decide_context_rule(ctx_row)
            if decision is not None:
                out_row["normalized_title"] = decision.normalized_title
                out_row["role_family"] = decision.role_family
                out_row["classification_status"] = "matched"
                out_row["match_method"] = "context_shadow_rule"
                out_row["matched_rule_id"] = decision.matched_rule_id
                out_row["confidence"] = decision.confidence
                out_row["notes"] = list(out_row.get("notes") or []) + ["shadow_context_rule_match"]
                matches_added += 1
                rule_hits[decision.matched_rule_id] += 1
                if len(sample_matches) < 12:
                    sample_matches.append(
                        {
                            "url": row.get("url"),
                            "title_clean": row.get("title_clean"),
                            "normalized_title": decision.normalized_title,
                            "role_family": decision.role_family,
                            "matched_rule_id": decision.matched_rule_id,
                            "evidence_hits": decision.evidence_hits,
                            "exclusion_hits": decision.exclusion_hits,
                        }
                    )
            else:
                title = str(ctx_row.get("title_clean") or "")
                if title in {"Onboarding Specialist", "Producer"} and len(excluded_examples) < 10:
                    from experiments.title_context_layer.shadow_context_rules import (
                        _hits,
                        _weighted_onboarding_signal,
                        ONBOARDING_HARD_EXCLUSION,
                        ONBOARDING_SOFT_EXCLUSION,
                        PRODUCER_EXCLUSION,
                        PRODUCER_POSITIVE,
                    )

                    if title == "Onboarding Specialist":
                        pos, neg, score = _weighted_onboarding_signal(ctx_row)
                    else:
                        text = str(ctx_row.get("context_text") or "")
                        pos = _hits(text, PRODUCER_POSITIVE)
                        neg = _hits(text, PRODUCER_EXCLUSION)
                        score = len(pos) - len(neg)
                    excluded_examples.append(
                        {
                            "url": row.get("url"),
                            "title_clean": title,
                            "evidence_hits": pos,
                            "exclusion_hits": neg,
                            "score": score,
                            "hard_exclusion_hits": [hit for hit in neg if hit in ONBOARDING_HARD_EXCLUSION],
                            "soft_exclusion_hits": [hit for hit in neg if hit in ONBOARDING_SOFT_EXCLUSION],
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
        "excluded_examples": excluded_examples,
    }

    decision = (
        "shadow_context_rules_viable_for_review"
        if matches_added >= 10 and ("ctx_onboarding_specialist_customer_success_v2" in rule_hits or "ctx_producer_content_v1" in rule_hits)
        else "shadow_context_rules_need_more_tuning"
    )
    reason = (
        "Tuned context-gated rules generated enough shadow matches to justify formal review before any production candidate patch."
        if decision == "shadow_context_rules_viable_for_review"
        else "Signal exists but current gated rules need more tuning before formal review."
    )
    payload["final_recommendation"] = {"decision": decision, "reason": reason}

    write_json(out_report, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    payload = run_shadow_context_batch(
        titled_path=root / "data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl",
        context_join_path=reports / "context_join_v1.jsonl",
        out_jsonl=root / "data/jobs/jobs_titled_en_recovery_v56_context_shadow_v2.jsonl",
        out_report=reports / "shadow_context_batch_v2.json",
    )
    render_markdown(payload, root / "docs/phase_e5_shadow_context_batch_v2.md")
    print(payload["final_recommendation"])
