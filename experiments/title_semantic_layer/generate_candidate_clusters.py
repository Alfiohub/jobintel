from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .common import read_json, repo_root, write_json


def generate_candidate_clusters(ranked_path: Path, out_path: Path) -> dict[str, Any]:
    ranked = read_json(ranked_path)
    rows = ranked.get("ranked_rows", [])

    grouped: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "estimated_volume": 0,
            "representative_titles": [],
            "actions": defaultdict(int),
            "risk_levels": defaultdict(int),
            "external_support": defaultdict(int),
        }
    )

    for row in rows:
        top_internal = row.get("top_internal", {})
        label = top_internal.get("normalized_title", "other")
        family = top_internal.get("role_family", "other")
        key = (label, family, row.get("suggested_action", "keep_other_for_now"))

        g = grouped[key]
        g["estimated_volume"] += int(row.get("count", 0))
        if len(g["representative_titles"]) < 8:
            g["representative_titles"].append({"title": row.get("title", ""), "count": row.get("count", 0)})
        g["actions"][row.get("suggested_action", "keep_other_for_now")] += 1
        g["risk_levels"][row.get("overmatch_risk", "medium")] += 1
        g["external_support"][row.get("support_strength", "none")] += 1

    clusters = []
    for (label, family, action), g in grouped.items():
        clusters.append(
            {
                "cluster_name": f"{label}_{action}",
                "target_label": label,
                "target_family": family,
                "suggested_action": action,
                "estimated_volume": g["estimated_volume"],
                "representative_titles": g["representative_titles"],
                "risk_levels": dict(g["risk_levels"]),
                "external_support": dict(g["external_support"]),
            }
        )

    clusters.sort(key=lambda x: x["estimated_volume"], reverse=True)
    payload = {
        "cluster_count": len(clusters),
        "clusters": clusters,
    }
    write_json(out_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    out = root / "experiments/title_semantic_layer/reports/semantic_candidate_clusters.json"
    result = generate_candidate_clusters(
        ranked_path=root / "experiments/title_semantic_layer/reports/ranked_candidates.json",
        out_path=out,
    )
    print(f"semantic_candidate_clusters -> {out} ({result['cluster_count']} clusters)")
