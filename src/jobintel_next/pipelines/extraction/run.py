from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from .io import row_to_cleaned
from .stage import ExtractionStage


def run_extraction_stage(
    *,
    input_path: str | Path,
    output_path: str | Path,
    report_dir: str | Path = "docs",
    limit: int | None = None,
    sample_size: int = 5,
) -> dict[str, Any]:
    in_path = Path(input_path)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_path_dir = Path(report_dir)
    report_path_dir.mkdir(parents=True, exist_ok=True)

    stage = ExtractionStage()
    rows_total = 0
    invalid_rows = 0
    samples: list[dict[str, Any]] = []

    fill_counter = Counter()
    with in_path.open("r", encoding="utf-8") as src, out_path.open("w", encoding="utf-8") as out:
        for line in src:
            s = line.strip()
            if not s:
                continue
            row = json.loads(s)
            if not isinstance(row, dict):
                invalid_rows += 1
                continue
            cleaned = row_to_cleaned(row)
            if cleaned is None:
                invalid_rows += 1
                continue

            extracted = stage.run_one(cleaned)
            out_row = dict(row)
            out_row.update(extracted.to_dict())
            out.write(json.dumps(out_row, ensure_ascii=False) + "\n")

            rows_total += 1
            if extracted.seniority:
                fill_counter["seniority"] += 1
            if extracted.employment_type:
                fill_counter["employment_type"] += 1
            if extracted.location_type:
                fill_counter["location_type"] += 1
            if extracted.salary_min is not None or extracted.salary_max is not None:
                fill_counter["salary"] += 1
            if extracted.salary_currency:
                fill_counter["salary_currency"] += 1
            if extracted.salary_period:
                fill_counter["salary_period"] += 1
            if extracted.skills:
                fill_counter["skills"] += 1

            if len(samples) < sample_size:
                samples.append(
                    {
                        "url": extracted.url,
                        "seniority": extracted.seniority,
                        "employment_type": extracted.employment_type,
                        "location_type": extracted.location_type,
                        "salary_min": extracted.salary_min,
                        "salary_max": extracted.salary_max,
                        "salary_currency": extracted.salary_currency,
                        "salary_period": extracted.salary_period,
                        "skills": extracted.skills[:12],
                        "tags": extracted.tags,
                    }
                )

            if limit is not None and rows_total >= limit:
                break

    def _rate(value: int) -> float:
        return round((value * 100.0 / rows_total), 2) if rows_total else 0.0

    filled_stats = {
        "seniority": {"count": fill_counter["seniority"], "pct": _rate(fill_counter["seniority"])},
        "employment_type": {"count": fill_counter["employment_type"], "pct": _rate(fill_counter["employment_type"])},
        "location_type": {"count": fill_counter["location_type"], "pct": _rate(fill_counter["location_type"])},
        "salary": {"count": fill_counter["salary"], "pct": _rate(fill_counter["salary"])},
        "salary_currency": {"count": fill_counter["salary_currency"], "pct": _rate(fill_counter["salary_currency"])},
        "salary_period": {"count": fill_counter["salary_period"], "pct": _rate(fill_counter["salary_period"])},
        "skills": {"count": fill_counter["skills"], "pct": _rate(fill_counter["skills"])},
    }

    report = {
        "input_path": str(in_path),
        "output_path": str(out_path),
        "rows_total": rows_total,
        "invalid_rows": invalid_rows,
        "filled_stats": filled_stats,
        "sample_extracted_rows": samples,
        "known_limits": [
            "Regex/rules approach only; no heavy NLP.",
            "Salary extraction supports common base patterns only.",
            "Skills list is intentionally small in this stage.",
        ],
    }

    report_json = report_path_dir / "extraction_stage_step9.json"
    report_md = report_path_dir / "extraction_stage_step9.md"
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Extraction Stage Step 9",
        "",
        f"Input: `{in_path}`",
        f"Output: `{out_path}`",
        "",
        "## Counts",
        f"- rows_total: {rows_total}",
        f"- invalid_rows: {invalid_rows}",
        "",
        "## Field Fill Rates",
    ]
    for key, value in filled_stats.items():
        md_lines.append(f"- {key}: {value['count']} ({value['pct']}%)")
    md_lines.append("")
    md_lines.append("## Sample Extracted Rows")
    for sample in samples:
        md_lines.append(
            f"- {sample['url']} | seniority={sample['seniority']} | employment_type={sample['employment_type']} | "
            f"location_type={sample['location_type']} | salary=({sample['salary_min']},{sample['salary_max']},{sample['salary_currency']},{sample['salary_period']}) | "
            f"skills={sample['skills']}"
        )
    md_lines.append("")
    md_lines.append("## Known Limits")
    for line in report["known_limits"]:
        md_lines.append(f"- {line}")

    report_md.write_text("\n".join(md_lines), encoding="utf-8")
    return report
