from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .common import read_json, repo_root, write_json


def build_reviewer_output(ranked_path: Path, out_path: Path, min_samples: int = 30) -> dict[str, Any]:
    ranked = read_json(ranked_path)
    rows = ranked.get("ranked_rows", [])

    sample_rows = rows[: max(min_samples, 30)]

    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_category[row.get("suggested_action", "keep_other_for_now")].append(row)

    opportunities = []
    for row in rows:
        if row.get("suggested_action") in {"safe_rule_candidate", "needs_tighter_rule", "taxonomy_gap"}:
            opportunities.append(
                {
                    "cluster_or_title": row.get("title", ""),
                    "estimated_volume": row.get("count", 0),
                    "target_label": row.get("top_internal", {}).get("normalized_title", ""),
                    "target_family": row.get("top_internal", {}).get("role_family", ""),
                    "suggested_action": row.get("suggested_action", ""),
                    "risk": row.get("overmatch_risk", ""),
                    "internal_score": row.get("top_internal", {}).get("score", 0.0),
                    "why_semantic_layer_adds_value": "external ESCO/O*NET candidate agreement improves confidence gating",
                }
            )
    opportunities.sort(key=lambda x: (x["estimated_volume"], x["internal_score"]), reverse=True)

    failure_modes = []
    for row in rows:
        if row.get("suggested_action") in {"semantic_layer_candidate", "keep_other_for_now", "noise_or_non_role"}:
            failure_modes.append(
                {
                    "cluster_or_title": row.get("title", ""),
                    "estimated_volume": row.get("count", 0),
                    "reason": row.get("suggested_action", ""),
                    "risk": row.get("overmatch_risk", ""),
                }
            )
    failure_modes.sort(key=lambda x: x["estimated_volume"], reverse=True)

    payload = {
        "sample_rows": sample_rows,
        "category_split": {k: sum(int(r.get("count", 0)) for r in v) for k, v in by_category.items()},
        "category_counts": {k: len(v) for k, v in by_category.items()},
        "top_opportunities": opportunities[:20],
        "top_failure_modes": failure_modes[:20],
    }
    write_json(out_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    out = root / "experiments/title_semantic_layer/reports/reviewer_output.json"
    result = build_reviewer_output(
        ranked_path=root / "experiments/title_semantic_layer/reports/ranked_candidates.json",
        out_path=out,
    )
    print(f"reviewer_output -> {out} ({len(result['sample_rows'])} sample rows)")
