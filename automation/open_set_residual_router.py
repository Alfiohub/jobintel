from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

from jobintel_next.pipelines.titles.open_set_router import route_open_set_row


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_router(
    *,
    input_path: Path,
    output_path: Path,
    report_json: Path,
    report_md: Path,
    top_k: int = 20,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_md.parent.mkdir(parents=True, exist_ok=True)

    by_route_status = Counter()
    by_route_lane = Counter()
    by_target = Counter()
    review_titles = Counter()
    taxonomy_gap_titles = Counter()
    sample_by_lane: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rows_total = 0

    with input_path.open("r", encoding="utf-8") as src, output_path.open("w", encoding="utf-8") as out:
        for line in src:
            if not line.strip():
                continue
            row = json.loads(line)
            decision = route_open_set_row(row)

            out_row = dict(row)
            out_row.update(decision.to_dict())
            out.write(json.dumps(out_row, ensure_ascii=False) + "\n")

            rows_total += 1
            by_route_status[decision.route_status] += 1
            by_route_lane[decision.route_lane] += 1
            if decision.suggested_target_label:
                by_target[decision.suggested_target_label] += 1
            if decision.route_status == "manual_review":
                review_titles[str(row.get("title_clean") or row.get("title") or "").strip()] += 1
            if decision.route_status == "taxonomy_gap":
                taxonomy_gap_titles[str(row.get("title_clean") or row.get("title") or "").strip()] += 1

            lane_samples = sample_by_lane[decision.route_lane]
            if len(lane_samples) < 8:
                lane_samples.append(
                    {
                        "title_clean": row.get("title_clean"),
                        "normalized_title": row.get("normalized_title"),
                        "route_status": decision.route_status,
                        "route_lane": decision.route_lane,
                        "suggested_target_label": decision.suggested_target_label,
                        "route_reason": decision.route_reason,
                    }
                )

    payload = {
        "phase": "E.21",
        "decision": "open_set_residual_router_v1_ready",
        "input_dataset": str(input_path.relative_to(REPO_ROOT)),
        "output_dataset": str(output_path.relative_to(REPO_ROOT)),
        "rows_total": rows_total,
        "counts_by_route_status": dict(by_route_status),
        "counts_by_route_lane": dict(by_route_lane),
        "top_suggested_targets": [{"target_label": t, "count": c} for t, c in by_target.most_common(top_k)],
        "top_manual_review_titles": [{"title_clean": t, "count": c} for t, c in review_titles.most_common(top_k)],
        "top_taxonomy_gap_titles": [{"title_clean": t, "count": c} for t, c in taxonomy_gap_titles.most_common(top_k)],
        "sample_by_lane": dict(sample_by_lane),
        "recommendation": {
            "first": "attack_now_manual_review_queue",
            "second": "recoverable_with_context_manual_review_queue",
            "third": "taxonomy_gap_queue",
        },
    }

    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Phase E.21 — Open-Set Residual Router v1",
        "",
        "## Goal",
        "Replace final `other` with explicit routed buckets over the current `v66` baseline.",
        "",
        "## Input",
        f"- dataset: `{payload['input_dataset']}`",
        "",
        "## Output",
        f"- routed dataset: `{payload['output_dataset']}`",
        "",
        "## Counts By Route Status",
    ]
    for key, value in by_route_status.most_common():
        lines.append(f"- `{key}`: `{value}`")
    lines += ["", "## Counts By Route Lane"]
    for key, value in by_route_lane.most_common():
        lines.append(f"- `{key}`: `{value}`")
    lines += ["", "## Top Suggested Targets"]
    for item in payload["top_suggested_targets"][:10]:
        lines.append(f"- `{item['target_label']}`: `{item['count']}`")
    lines += ["", "## Recommendation"]
    lines.append(f"- first: `{payload['recommendation']['first']}`")
    lines.append(f"- second: `{payload['recommendation']['second']}`")
    lines.append(f"- third: `{payload['recommendation']['third']}`")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    payload = run_router(
        input_path=REPO_ROOT / "data/jobs/jobs_titled_en_recovery_v66_partner_lane_candidate.jsonl",
        output_path=REPO_ROOT / "data/jobs/jobs_titled_en_recovery_v67_open_set_router.jsonl",
        report_json=REPO_ROOT / "experiments/residual_audit/reports/phase_e21_open_set_residual_router_v1.json",
        report_md=REPO_ROOT / "docs/phase_e21_open_set_residual_router_v1.md",
    )
    print(
        {
            "decision": payload["decision"],
            "manual_review": payload["counts_by_route_status"].get("manual_review", 0),
            "taxonomy_gap": payload["counts_by_route_status"].get("taxonomy_gap", 0),
        }
    )


if __name__ == "__main__":
    main()
