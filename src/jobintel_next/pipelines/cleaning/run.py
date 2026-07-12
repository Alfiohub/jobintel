from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .stage import CleaningStage
from ..language.io import row_to_canonical


def run_cleaning_stage(
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

    stage = CleaningStage()
    rows_total = 0
    invalid_rows = 0
    samples: list[dict[str, Any]] = []

    with in_path.open("r", encoding="utf-8") as src, out_path.open("w", encoding="utf-8") as out:
        for line in src:
            s = line.strip()
            if not s:
                continue
            row = json.loads(s)
            if not isinstance(row, dict):
                invalid_rows += 1
                continue
            canonical = row_to_canonical(row)
            if canonical is None:
                invalid_rows += 1
                continue

            cleaned = stage.run_one(canonical)
            out_row = dict(row)
            out_row.update(cleaned.to_dict())
            out.write(json.dumps(out_row, ensure_ascii=False) + "\n")

            rows_total += 1
            if len(samples) < sample_size:
                samples.append(
                    {
                        "url": cleaned.url,
                        "title_clean": cleaned.title_clean,
                        "location_clean": cleaned.location_clean,
                        "requirements_clean": cleaned.requirements_clean[:240],
                        "responsibilities_clean": cleaned.responsibilities_clean[:240],
                        "content_hash": cleaned.content_hash,
                    }
                )
            if limit is not None and rows_total >= limit:
                break

    report = {
        "input_path": str(in_path),
        "output_path": str(out_path),
        "rows_total": rows_total,
        "invalid_rows": invalid_rows,
        "sample_cleaned_rows": samples,
        "rules_used": [
            "title_clean: trim whitespace + normalize separators",
            "description_clean: html unescape + strip html tags + whitespace normalization",
            "location_clean: trim/normalize whitespace",
            "requirements/responsibilities: simple heading/sentence heuristics",
            "content_hash: stable sha256 over cleaned text fields",
        ],
        "known_limits": [
            "No semantic normalization in cleaning stage",
            "Section extraction is heuristic and may miss implicit sections",
            "description_clean is linearized text (structure reduced)",
        ],
    }

    report_json = report_path_dir / "cleaning_stage_step8.json"
    report_md = report_path_dir / "cleaning_stage_step8.md"
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Cleaning Stage Step 8",
        "",
        f"Input: `{in_path}`",
        f"Output: `{out_path}`",
        "",
        "## Counts",
        f"- rows_total: {rows_total}",
        f"- invalid_rows: {invalid_rows}",
        "",
        "## Rules Used",
    ]
    for rule in report["rules_used"]:
        md_lines.append(f"- {rule}")
    md_lines.append("")
    md_lines.append("## Known Limits")
    for item in report["known_limits"]:
        md_lines.append(f"- {item}")
    md_lines.append("")
    md_lines.append("## Sample Cleaned Rows")
    for sample in samples:
        md_lines.append(f"- url: {sample['url']}")
        md_lines.append(f"  - title_clean: {sample['title_clean']}")
        md_lines.append(f"  - content_hash: {sample['content_hash']}")

    report_md.write_text("\n".join(md_lines), encoding="utf-8")
    return report

