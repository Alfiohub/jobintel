from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from experiments.residual_audit.non_role_recruiting_entry_analysis import classify_non_role_candidate
from experiments.title_semantic_layer.common import read_jsonl, repo_root, write_json, write_jsonl


def _description_blob(extracted: dict[str, Any]) -> str:
    return " ".join(
        str(extracted.get(field) or "")
        for field in ("description_clean", "responsibilities_clean", "requirements_clean")
    )


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# Phase E.8.1 — Shadow Non-Role Macro-Class Draft")
    lines.append("")
    lines.append("## Baseline")
    lines.append(f"- input dataset: `{payload['baseline']['dataset']}`")
    lines.append(f"- rows total: `{payload['baseline']['rows_total']}`")
    lines.append(f"- other before: `{payload['baseline']['other_before']}`")
    lines.append("")
    lines.append("## Shadow Result")
    lines.append(f"- non-role candidates total: `{payload['shadow_result']['non_role_total']}`")
    lines.append(f"- from other: `{payload['shadow_result']['from_other']}`")
    lines.append(f"- from matched: `{payload['shadow_result']['from_matched']}`")
    lines.append(f"- occupational other after shadow: `{payload['shadow_result']['other_after_occupational']}`")
    lines.append(f"- delta occupational other: `{payload['shadow_result']['delta_other']}`")
    lines.append("")
    lines.append("## Top Pattern Hits")
    for row in payload["top_pattern_hits"]:
        lines.append(f"- `{row['pattern']}`: `{row['count']}`")
    lines.append("")
    lines.append("## Sample Other -> Non-Role")
    for row in payload["sample_other_to_non_role"]:
        lines.append(f"- `{row['title_clean']}` | company `{row['company_name']}` | hits `{', '.join(row['pattern_hits'])}`")
    lines.append("")
    lines.append("## Sample Matched -> Non-Role")
    for row in payload["sample_matched_to_non_role"]:
        lines.append(
            f"- `{row['title_clean']}` | current `{row['normalized_title']}/{row['role_family']}` | rule `{row['matched_rule_id']}` | hits `{', '.join(row['pattern_hits'])}`"
        )
    lines.append("")
    lines.append("## Recommendation")
    lines.append(f"- `{payload['recommendation']['decision']}`")
    lines.append(f"- reason: {payload['recommendation']['reason']}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_shadow_non_role_macroclass(
    titled_path: Path,
    extracted_path: Path,
    out_jsonl: Path,
    out_report: Path,
) -> dict[str, Any]:
    titled_rows = read_jsonl(titled_path)
    extracted_by_url = {row["url"]: row for row in read_jsonl(extracted_path) if row.get("url")}

    out_rows: list[dict[str, Any]] = []
    pattern_hits: Counter[str] = Counter()
    from_other = 0
    from_matched = 0
    sample_other_to_non_role: list[dict[str, Any]] = []
    sample_matched_to_non_role: list[dict[str, Any]] = []

    for row in titled_rows:
        out_row = dict(row)
        extracted = extracted_by_url.get(str(row.get("url") or ""), {})
        is_candidate, hits = classify_non_role_candidate(
            str(row.get("title_clean") or ""),
            _description_blob(extracted),
        )
        if is_candidate:
            previous_status = str(row.get("classification_status") or "")
            if previous_status == "other":
                from_other += 1
                if len(sample_other_to_non_role) < 12:
                    sample_other_to_non_role.append(
                        {
                            "title_clean": row.get("title_clean"),
                            "company_name": row.get("company_name"),
                            "pattern_hits": hits,
                        }
                    )
            elif previous_status == "matched":
                from_matched += 1
                if len(sample_matched_to_non_role) < 12:
                    sample_matched_to_non_role.append(
                        {
                            "title_clean": row.get("title_clean"),
                            "normalized_title": row.get("normalized_title"),
                            "role_family": row.get("role_family"),
                            "matched_rule_id": row.get("matched_rule_id"),
                            "pattern_hits": hits,
                        }
                    )
            for hit in hits:
                pattern_hits[hit] += 1

            out_row["classification_status"] = "non_role"
            out_row["normalized_title"] = "non_role_recruiting_entry"
            out_row["role_family"] = "non_role"
            out_row["match_method"] = "shadow_non_role_macroclass"
            out_row["matched_rule_id"] = "shadow_non_role_recruiting_entry_v1"
            out_row["confidence"] = 0.95
            out_row["notes"] = list(out_row.get("notes") or []) + ["shadow_non_role_recruiting_entry"]

        out_rows.append(out_row)

    write_jsonl(out_jsonl, out_rows)

    other_before = sum(1 for row in titled_rows if row.get("classification_status") == "other")
    other_after = sum(1 for row in out_rows if row.get("classification_status") == "other")
    payload = {
        "baseline": {
            "dataset": str(titled_path.relative_to(repo_root())),
            "rows_total": len(titled_rows),
            "other_before": other_before,
        },
        "shadow_result": {
            "output_dataset": str(out_jsonl.relative_to(repo_root())),
            "non_role_total": from_other + from_matched,
            "from_other": from_other,
            "from_matched": from_matched,
            "other_after_occupational": other_after,
            "delta_other": other_after - other_before,
        },
        "top_pattern_hits": [
            {"pattern": pattern, "count": count}
            for pattern, count in pattern_hits.most_common(15)
        ],
        "sample_other_to_non_role": sample_other_to_non_role,
        "sample_matched_to_non_role": sample_matched_to_non_role,
        "recommendation": {
            "decision": "shadow_non_role_macroclass_viable",
            "reason": "The dataset contains a measurable recruiting-placeholder slice that should be separated from occupational coding before future residual analysis.",
        },
    }
    write_json(out_report, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/residual_audit/reports"
    payload = run_shadow_non_role_macroclass(
        titled_path=root / "data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl",
        extracted_path=root / "data/jobs/jobs_extracted_en.jsonl",
        out_jsonl=root / "data/jobs/jobs_titled_en_recovery_v57_non_role_shadow.jsonl",
        out_report=reports / "non_role_macroclass_shadow_v1.json",
    )
    render_markdown(payload, root / "docs/phase_e8_non_role_macroclass_shadow_v1.md")
    print(payload["recommendation"])
