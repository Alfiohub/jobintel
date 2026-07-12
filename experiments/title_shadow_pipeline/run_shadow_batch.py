from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re


def run(input_path: Path, candidate_report: Path, output_path: Path, selected_count: int = 3) -> dict[str, object]:
    report = json.loads(candidate_report.read_text(encoding="utf-8"))
    selected = list(report.get("selected_for_shadow_batch") or [])[:selected_count]

    compiled = []
    for item in selected:
        pat = re.compile(str(item["lexical_pattern"]))
        compiled.append((item, pat))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    other_before = 0
    other_after = 0
    hits = Counter()

    with input_path.open("r", encoding="utf-8") as src, output_path.open("w", encoding="utf-8") as out:
        for line in src:
            if not line.strip():
                continue
            rows += 1
            row = json.loads(line)
            was_other = row.get("classification_status") == "other"
            if was_other:
                other_before += 1

            title = (row.get("title_clean") or row.get("title_raw") or "").strip().lower()
            applied = None
            if was_other and title:
                for item, pat in compiled:
                    if pat.search(title):
                        applied = item
                        break

            if applied is not None:
                row["shadow_prev_normalized_title"] = row.get("normalized_title")
                row["shadow_prev_role_family"] = row.get("role_family")
                row["shadow_prev_classification_status"] = row.get("classification_status")
                row["normalized_title"] = applied["target_label"]
                row["role_family"] = applied["target_family"]
                row["classification_status"] = "matched"
                row["match_method"] = "shadow_rule"
                row["matched_rule_id"] = f"shadow::{applied['cluster_name']}"
                row["confidence"] = max(float(row.get("confidence") or 0.0), 0.86)
                notes = list(row.get("notes") or [])
                notes.append(f"shadow_batch:{applied['cluster_name']}")
                row["notes"] = notes
                row["title_is_other"] = False
                hits[applied["cluster_name"]] += 1

            if row.get("classification_status") == "other":
                other_after += 1
            out.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "rows_total": rows,
        "other_before": other_before,
        "other_after": other_after,
        "delta_other": other_after - other_before,
        "selected_clusters": selected,
        "cluster_hits": dict(hits),
    }
    (output_path.parent / "shadow_batch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Run shadow batch mappings over baseline titled dataset")
    ap.add_argument("--input", required=True)
    ap.add_argument("--candidate-report", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--selected-count", type=int, default=3)
    args = ap.parse_args()

    run(Path(args.input), Path(args.candidate_report), Path(args.output), selected_count=args.selected_count)


if __name__ == "__main__":
    main()
