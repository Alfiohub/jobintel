from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def _load_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            obj = json.loads(s)
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate title normalization quality.")
    parser.add_argument("--indexed-jsonl", required=True, help="Path to jobs_indexed.jsonl")
    parser.add_argument("--report-md", required=True, help="Output Markdown report path")
    parser.add_argument("--unmatched-csv", required=True, help="Output CSV for top unmatched titles")
    parser.add_argument("--top-n", type=int, default=50, help="Top unmatched titles to export")
    args = parser.parse_args()

    rows = _load_rows(Path(args.indexed_jsonl))
    if not rows:
        raise SystemExit("No rows found in indexed JSONL")

    total = len(rows)
    unmatched_titles: Counter[str] = Counter()
    role_family_counts: Counter[str] = Counter()
    normalized_title_counts: Counter[str] = Counter()

    for r in rows:
        role_family = str(r.get("role_family") or "other")
        normalized_title = str(r.get("normalized_title") or "other")
        occupation_group = str(r.get("occupation_group") or "other")
        title = str(r.get("title_clean") or r.get("title_raw") or "")

        role_family_counts[role_family] += 1
        normalized_title_counts[normalized_title] += 1

        if (
            normalized_title == "other"
            or role_family == "other"
            or occupation_group == "other"
        ):
            unmatched_titles[title] += 1

    unmatched = sum(unmatched_titles.values())
    matched = total - unmatched
    coverage_pct = round((matched * 100.0) / total, 2)
    other_like_pct = round((unmatched * 100.0) / total, 2)

    top_unmatched = unmatched_titles.most_common(max(1, args.top_n))
    top_families = role_family_counts.most_common(20)
    top_normalized = normalized_title_counts.most_common(20)

    report = Path(args.report_md)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "\n".join(
            [
                "# Title Normalization Evaluation",
                "",
                f"- input: `{args.indexed_jsonl}`",
                f"- total rows: `{total}`",
                f"- matched rows: `{matched}`",
                f"- unmatched rows (other-like): `{unmatched}`",
                f"- coverage: `{coverage_pct}%`",
                f"- other_like: `{other_like_pct}%`",
                "",
                "## Top Role Families",
                "",
                "| role_family | count | pct |",
                "|---|---:|---:|",
                *[
                    f"| {fam} | {cnt} | {round((cnt*100.0)/total,2)}% |"
                    for fam, cnt in top_families
                ],
                "",
                "## Top Normalized Titles",
                "",
                "| normalized_title | count | pct |",
                "|---|---:|---:|",
                *[
                    f"| {title} | {cnt} | {round((cnt*100.0)/total,2)}% |"
                    for title, cnt in top_normalized
                ],
                "",
                f"## Top {len(top_unmatched)} Unmatched Titles",
                "",
                "| title | count |",
                "|---|---:|",
                *[f"| {title} | {cnt} |" for title, cnt in top_unmatched],
                "",
            ]
        ),
        encoding="utf-8",
    )

    unmatched_csv = Path(args.unmatched_csv)
    unmatched_csv.parent.mkdir(parents=True, exist_ok=True)
    with unmatched_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["title", "count"])
        for title, cnt in top_unmatched:
            w.writerow([title, cnt])

    print(f"Wrote report: {report}")
    print(f"Wrote unmatched CSV: {unmatched_csv}")
    print(f"coverage={coverage_pct}% other_like={other_like_pct}%")


if __name__ == "__main__":
    main()
