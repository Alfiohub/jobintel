from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from .io import row_to_canonical
from .stage import LanguageStage


def run_language_gate(
    *,
    input_path: str | Path,
    outdir: str | Path,
    report_dir: str | Path = "docs",
    limit: int | None = None,
    top_k: int = 20,
) -> dict[str, Any]:
    in_path = Path(input_path)
    output_dir = Path(outdir)
    report_path_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path_dir.mkdir(parents=True, exist_ok=True)

    out_en = output_dir / "jobs_en_filtered.jsonl"
    out_non_en = output_dir / "jobs_non_en.jsonl"
    out_unknown = output_dir / "jobs_unknown_language.jsonl"

    stage = LanguageStage()

    rows_total = 0
    invalid_rows = 0
    reasons_by_bucket: dict[str, Counter[str]] = {
        "en": Counter(),
        "non_en": Counter(),
        "unknown": Counter(),
    }

    with (
        in_path.open("r", encoding="utf-8") as src,
        out_en.open("w", encoding="utf-8") as f_en,
        out_non_en.open("w", encoding="utf-8") as f_non_en,
        out_unknown.open("w", encoding="utf-8") as f_unknown,
    ):
        for line in src:
            s = line.strip()
            if not s:
                continue
            obj = json.loads(s)
            if not isinstance(obj, dict):
                invalid_rows += 1
                continue
            canonical = row_to_canonical(obj)
            if canonical is None:
                invalid_rows += 1
                continue

            decision = stage.run_one(canonical)
            out_row = canonical.to_dict()
            out_row["language_bucket"] = decision.bucket
            out_row["language_reason"] = decision.reason
            out_row["language_code"] = decision.language_code
            out_row["language_confidence"] = decision.confidence

            if decision.bucket == "en":
                f_en.write(json.dumps(out_row, ensure_ascii=False) + "\n")
            elif decision.bucket == "non_en":
                f_non_en.write(json.dumps(out_row, ensure_ascii=False) + "\n")
            else:
                f_unknown.write(json.dumps(out_row, ensure_ascii=False) + "\n")

            reasons_by_bucket[decision.bucket][decision.reason] += 1
            rows_total += 1
            if limit is not None and rows_total >= limit:
                break

    rows_en = sum(reasons_by_bucket["en"].values())
    rows_non_en = sum(reasons_by_bucket["non_en"].values())
    rows_unknown = sum(reasons_by_bucket["unknown"].values())

    def _pct(value: int) -> float:
        return round((value * 100.0 / rows_total), 2) if rows_total else 0.0

    report = {
        "input_path": str(in_path),
        "rows_total": rows_total,
        "invalid_rows": invalid_rows,
        "rows_en": rows_en,
        "rows_non_en": rows_non_en,
        "rows_unknown": rows_unknown,
        "pct_en": _pct(rows_en),
        "pct_non_en": _pct(rows_non_en),
        "pct_unknown": _pct(rows_unknown),
        "top_reasons_by_bucket": {
            bucket: [{"reason": reason, "count": count} for reason, count in ctr.most_common(top_k)]
            for bucket, ctr in reasons_by_bucket.items()
        },
        "output_files": {
            "en": str(out_en),
            "non_en": str(out_non_en),
            "unknown": str(out_unknown),
        },
    }

    report_json = report_path_dir / "language_gate_step7.json"
    report_md = report_path_dir / "language_gate_step7.md"
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Language Gate Step 7",
        "",
        f"Input: `{in_path}`",
        "",
        "## Counts",
        f"- rows_total: {rows_total}",
        f"- invalid_rows: {invalid_rows}",
        f"- rows_en: {rows_en} ({_pct(rows_en)}%)",
        f"- rows_non_en: {rows_non_en} ({_pct(rows_non_en)}%)",
        f"- rows_unknown: {rows_unknown} ({_pct(rows_unknown)}%)",
        "",
        "## Output Files",
        f"- en: `{out_en}`",
        f"- non_en: `{out_non_en}`",
        f"- unknown: `{out_unknown}`",
        "",
    ]
    for bucket in ("en", "non_en", "unknown"):
        md_lines.append(f"## Top Reasons ({bucket})")
        for item in report["top_reasons_by_bucket"][bucket][:10]:
            md_lines.append(f"- {item['reason']}: {item['count']}")
        md_lines.append("")
    report_md.write_text("\n".join(md_lines), encoding="utf-8")

    return report

