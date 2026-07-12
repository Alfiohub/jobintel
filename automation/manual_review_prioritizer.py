from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _priority_score(*, lane: str, count: int, unique_titles: int, unique_companies: int) -> float:
    lane_weight = {
        "attack_now": 1.0,
        "recoverable_with_context": 0.8,
        "long_tail": 0.2,
    }.get(lane, 0.1)
    diversity_bonus = min(unique_titles / 10.0, 1.0) * 0.3 + min(unique_companies / 10.0, 1.0) * 0.3
    volume_score = min(count / 100.0, 5.0)
    return round((volume_score + diversity_bonus) * lane_weight, 4)


def build_prioritizer_payload(input_path: Path) -> dict[str, Any]:
    groups: dict[tuple[str, str | None], dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "titles": Counter(),
            "companies": Counter(),
            "examples": [],
            "route_reason": Counter(),
            "route_status": "manual_review",
        }
    )

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("route_status") != "manual_review":
                continue
            lane = row.get("route_lane")
            target = row.get("suggested_target_label")
            key = (lane, target)
            group = groups[key]
            group["count"] += 1
            title = str(row.get("title_clean") or "").strip()
            company = str(row.get("company_name") or "").strip()
            if title:
                group["titles"][title] += 1
            if company:
                group["companies"][company] += 1
            reason = str(row.get("route_reason") or "").strip()
            if reason:
                group["route_reason"][reason] += 1
            if len(group["examples"]) < 6:
                group["examples"].append(
                    {
                        "title_clean": title,
                        "company_name": company,
                        "url": row.get("url"),
                    }
                )

    prioritized: list[dict[str, Any]] = []
    for (lane, target), group in groups.items():
        unique_titles = len(group["titles"])
        unique_companies = len(group["companies"])
        priority_score = _priority_score(
            lane=str(lane),
            count=int(group["count"]),
            unique_titles=unique_titles,
            unique_companies=unique_companies,
        )
        prioritized.append(
            {
                "lane": lane,
                "suggested_target_label": target,
                "count": group["count"],
                "unique_titles": unique_titles,
                "unique_companies": unique_companies,
                "priority_score": priority_score,
                "top_titles": dict(group["titles"].most_common(8)),
                "top_companies": dict(group["companies"].most_common(8)),
                "route_reasons": dict(group["route_reason"].most_common()),
                "examples": group["examples"],
            }
        )

    prioritized.sort(key=lambda item: (item["priority_score"], item["count"]), reverse=True)

    attack_now = [item for item in prioritized if item["lane"] == "attack_now"]
    context = [item for item in prioritized if item["lane"] == "recoverable_with_context"]
    long_tail = [item for item in prioritized if item["lane"] == "long_tail"]

    return {
        "phase": "E.22",
        "decision": "manual_review_prioritizer_v1_ready",
        "input_dataset": _display_path(input_path),
        "manual_review_total": sum(item["count"] for item in prioritized),
        "queues": {
            "attack_now": attack_now,
            "recoverable_with_context": context,
            "long_tail": long_tail[:20],
        },
        "recommendation": {
            "first_attack_now_target": attack_now[0]["suggested_target_label"] if attack_now else None,
            "first_context_target": context[0]["suggested_target_label"] if context else None,
            "long_tail_policy": "do_not_work_cluster_by_cluster_without_semantic_clustering",
        },
    }


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# Phase E.22 — Manual Review Prioritizer v1",
        "",
        "## Goal",
        "Turn the open-set router manual-review mass into ordered actionable queues.",
        "",
        f"- input dataset: `{payload['input_dataset']}`",
        f"- manual_review_total: `{payload['manual_review_total']}`",
        "",
        "## Attack-Now Queue",
    ]
    for item in payload["queues"]["attack_now"][:10]:
        lines.append(
            f"- `{item['suggested_target_label']}` | count `{item['count']}` | "
            f"titles `{item['unique_titles']}` | companies `{item['unique_companies']}` | "
            f"priority `{item['priority_score']}`"
        )
    lines += ["", "## Recoverable-With-Context Queue"]
    for item in payload["queues"]["recoverable_with_context"][:10]:
        lines.append(
            f"- `{item['suggested_target_label']}` | count `{item['count']}` | "
            f"titles `{item['unique_titles']}` | companies `{item['unique_companies']}` | "
            f"priority `{item['priority_score']}`"
        )
    lines += ["", "## Long-Tail Policy"]
    lines.append(f"- `{payload['recommendation']['long_tail_policy']}`")
    lines += ["", "## Recommendation"]
    lines.append(f"- first attack_now target: `{payload['recommendation']['first_attack_now_target']}`")
    lines.append(f"- first context target: `{payload['recommendation']['first_context_target']}`")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    input_path = REPO_ROOT / "data/jobs/jobs_titled_en_recovery_v67_open_set_router.jsonl"
    payload = build_prioritizer_payload(input_path)
    json_path = REPO_ROOT / "experiments/residual_audit/reports/phase_e22_manual_review_prioritizer_v1.json"
    md_path = REPO_ROOT / "docs/phase_e22_manual_review_prioritizer_v1.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    render_markdown(payload, md_path)
    print(
        {
            "decision": payload["decision"],
            "attack_now_top": payload["recommendation"]["first_attack_now_target"],
            "context_top": payload["recommendation"]["first_context_target"],
        }
    )


if __name__ == "__main__":
    main()
