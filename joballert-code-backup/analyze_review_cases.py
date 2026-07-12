from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


CATEGORY_ORDER = [
    "timeout_error",
    "network_error",
    "json_parse_error",
    "runtime_error",
    "low_confidence",
    "missing_normalized_title",
    "missing_role_family",
    "location_without_country",
    "salary_without_currency",
    "salary_without_period",
    "experience_range_invalid",
    "experience_parse_invalid",
    "too_many_core_fields_missing",
    "sparse_output",
    "uncategorized_review",
]

CORE_FIELDS = [
    "gold_normalized_title",
    "gold_role_family",
    "gold_location_type",
    "gold_employment_type",
    "gold_seniority",
]


def _s(value: Any) -> str:
    return str(value or "").strip()


def _is_review_row(row: dict[str, str]) -> bool:
    needs_review = _s(row.get("needs_review")) == "1"
    status = _s(row.get("review_status")).lower()
    not_approved = bool(status) and status != "approved"
    return needs_review or not_approved


def _to_float(value: Any) -> float | None:
    try:
        return float(_s(value))
    except Exception:
        return None


def _extract_categories(row: dict[str, str]) -> list[str]:
    categories: set[str] = set()
    notes = _s(row.get("notes")).lower()

    if "timeout_error" in notes:
        categories.add("timeout_error")
    if "network_error" in notes:
        categories.add("network_error")
    if "json_parse_error" in notes or "could not parse json object" in notes:
        categories.add("json_parse_error")
    if "runtime_error" in notes:
        categories.add("runtime_error")

    conf = _to_float(row.get("label_confidence"))
    if conf is not None and conf < 0.65:
        categories.add("low_confidence")

    if not _s(row.get("gold_normalized_title")):
        categories.add("missing_normalized_title")
    if not _s(row.get("gold_role_family")):
        categories.add("missing_role_family")

    if _s(row.get("gold_location_type")) and not _s(row.get("gold_country")):
        categories.add("location_without_country")

    salary_present = bool(_s(row.get("gold_salary_min")) or _s(row.get("gold_salary_max")))
    if salary_present and not _s(row.get("gold_salary_currency")):
        categories.add("salary_without_currency")
    if salary_present and not _s(row.get("gold_salary_period")):
        categories.add("salary_without_period")

    exp_min_raw = _s(row.get("gold_experience_years_min"))
    exp_max_raw = _s(row.get("gold_experience_years_max"))
    if exp_min_raw and exp_max_raw:
        try:
            if int(exp_min_raw) > int(exp_max_raw):
                categories.add("experience_range_invalid")
        except ValueError:
            categories.add("experience_parse_invalid")

    missing_core = sum(1 for k in CORE_FIELDS if not _s(row.get(k)))
    if missing_core >= 3:
        categories.add("too_many_core_fields_missing")
    if missing_core >= 4:
        categories.add("sparse_output")

    ordered = [c for c in CATEGORY_ORDER if c in categories]
    if not ordered:
        ordered = ["uncategorized_review"]
    return ordered


def _primary_category(categories: list[str]) -> str:
    if categories:
        return categories[0]
    return "uncategorized_review"


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze review cases from autolabeled CSV.")
    ap.add_argument("--input", required=True, help="Input autolabeled CSV path")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--top-combinations", type=int, default=20, help="Top N category combinations in summary")
    args = ap.parse_args()

    in_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows found in {in_path}")

    base_fieldnames = list(rows[0].keys())
    extra_fieldnames = ["review_categories", "primary_review_category", "missing_core_count"]
    out_fieldnames = base_fieldnames + [c for c in extra_fieldnames if c not in base_fieldnames]

    review_rows: list[dict[str, str]] = []
    by_primary: dict[str, list[dict[str, str]]] = {}
    category_counter: Counter[str] = Counter()
    primary_counter: Counter[str] = Counter()
    combo_counter: Counter[str] = Counter()

    for row in rows:
        if not _is_review_row(row):
            continue
        categories = _extract_categories(row)
        primary = _primary_category(categories)
        combo = "|".join(categories) if categories else "uncategorized_review"
        missing_core = sum(1 for k in CORE_FIELDS if not _s(row.get(k)))

        for c in categories:
            category_counter[c] += 1
        primary_counter[primary] += 1
        combo_counter[combo] += 1

        out_row = dict(row)
        out_row["review_categories"] = combo
        out_row["primary_review_category"] = primary
        out_row["missing_core_count"] = str(missing_core)
        review_rows.append(out_row)
        by_primary.setdefault(primary, []).append(out_row)

    review_cases_csv = outdir / "review_cases.csv"
    _write_csv(review_cases_csv, review_rows, out_fieldnames)

    for primary, prows in by_primary.items():
        safe = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in primary)
        _write_csv(outdir / f"review_{safe}.csv", prows, out_fieldnames)

    summary = {
        "input_csv": str(in_path),
        "total_rows": len(rows),
        "total_review_rows": len(review_rows),
        "counts_by_category": dict(category_counter.most_common()),
        "counts_by_primary_review_category": dict(primary_counter.most_common()),
        "top_category_combinations": [
            {"combination": k, "count": v} for k, v in combo_counter.most_common(max(1, args.top_combinations))
        ],
    }

    summary_json = outdir / "review_summary.json"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "Review Analysis Summary",
        f"Input: {in_path}",
        f"Total rows: {len(rows)}",
        f"Total review rows: {len(review_rows)}",
        "",
        "Counts By Category:",
    ]
    if category_counter:
        for k, v in category_counter.most_common():
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- (none)")
    lines += ["", "Counts By Primary Review Category:"]
    if primary_counter:
        for k, v in primary_counter.most_common():
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- (none)")
    lines += ["", "Top Category Combinations:"]
    if combo_counter:
        for k, v in combo_counter.most_common(max(1, args.top_combinations)):
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- (none)")
    lines += [
        "",
        f"Wrote: {review_cases_csv}",
        f"Wrote: {summary_json}",
        f"Per-primary CSV files: {len(by_primary)}",
    ]

    summary_txt = outdir / "review_summary.txt"
    summary_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote: {review_cases_csv}")
    print(f"Wrote: {summary_json}")
    print(f"Wrote: {summary_txt}")
    print(f"Review rows: {len(review_rows)}")


if __name__ == "__main__":
    main()
