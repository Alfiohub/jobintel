from __future__ import annotations

from pathlib import Path

from .common import read_json, repo_root, write_json
from .run_semantic_bootstrap import run_phase_e_semantic_bootstrap


IN_SCOPE = [
    "software development manager",
    "production engineer",
    "fpga engineer",
    "it administrator",
    "technical architect",
    "data science manager",
]


def _index_ranked(path: Path) -> dict[str, dict]:
    ranked = read_json(path)
    out = {}
    for row in ranked.get("ranked_rows", []):
        out[str(row.get("title", "")).lower().strip()] = row
    return out


def run_phase_e3_cleanup(root: Path) -> dict:
    dataset = root / "data/jobs/jobs_titled_en_recovery_v53_safe.jsonl"

    baseline = run_phase_e_semantic_bootstrap(dataset, apply_overlay=False, output_prefix="baseline_no_overlay")
    overlay = run_phase_e_semantic_bootstrap(dataset, apply_overlay=True, output_prefix="overlay_e3")

    baseline_ranked = _index_ranked(root / "experiments/title_semantic_layer/reports/baseline_no_overlay_ranked_candidates.json")
    overlay_ranked = _index_ranked(root / "experiments/title_semantic_layer/reports/overlay_e3_ranked_candidates.json")

    comparisons = []
    for title in IN_SCOPE:
        before = baseline_ranked.get(title, {})
        after = overlay_ranked.get(title, {})
        before_internal = before.get("top_internal", {})
        after_internal = after.get("top_internal", {})
        comparisons.append(
            {
                "title": title,
                "before_label": before_internal.get("normalized_title", ""),
                "before_family": before_internal.get("role_family", ""),
                "before_score": before_internal.get("score", 0.0),
                "after_label": after_internal.get("normalized_title", ""),
                "after_family": after_internal.get("role_family", ""),
                "after_score": after_internal.get("score", 0.0),
                "changed": (
                    before_internal.get("normalized_title", "") != after_internal.get("normalized_title", "")
                    or before_internal.get("role_family", "") != after_internal.get("role_family", "")
                ),
            }
        )

    payload = {
        "baseline": overlay["baseline"],
        "overlay_summary": {
            "baseline_internal_canonical_count": baseline["semantic_bootstrap_summary"]["internal_canonical_count"],
            "overlay_internal_canonical_count": overlay["semantic_bootstrap_summary"]["internal_canonical_count"],
        },
        "comparisons": comparisons,
        "report_paths": {
            "baseline_bootstrap": "experiments/title_semantic_layer/reports/phase_e_bootstrap_report_baseline_no_overlay.json",
            "overlay_bootstrap": "experiments/title_semantic_layer/reports/phase_e_bootstrap_report_overlay_e3.json",
        },
    }
    write_json(root / "experiments/title_semantic_layer/reports/phase_e3_targeted_cleanup_report.json", payload)
    return payload


def render_markdown(payload: dict, out_path: Path) -> None:
    lines = []
    lines.append("# Phase E.3 — Targeted Taxonomy Cleanup Patch")
    lines.append("")
    lines.append("## Scope")
    for item in IN_SCOPE[:-1]:
        lines.append(f"- `{item}`")
    lines.append(f"- `{IN_SCOPE[-1]}` as new-label experiment")
    lines.append("")
    lines.append("## Comparison")
    for row in payload["comparisons"]:
        lines.append(
            f"- `{row['title']}` | before `{row['before_label']}/{row['before_family']}` ({row['before_score']}) | after `{row['after_label']}/{row['after_family']}` ({row['after_score']}) | changed `{row['changed']}`"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("- This patch affects only the semantic layer corpus and retrieval.")
    lines.append("- No production classifier files were modified.")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = repo_root()
    payload = run_phase_e3_cleanup(root)
    out = root / "docs/phase_e3_targeted_taxonomy_cleanup_patch.md"
    render_markdown(payload, out)
    print("report_json=experiments/title_semantic_layer/reports/phase_e3_targeted_cleanup_report.json")
    print("report_md=docs/phase_e3_targeted_taxonomy_cleanup_patch.md")
