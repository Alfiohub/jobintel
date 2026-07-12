from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from jobintel_next.domain.models import CanonicalRawJob, LanguageDecision

from .io import row_to_canonical
from .stage import LanguageStage

def run_language_eval(
    *,
    input_path: str | Path,
    outdir: str | Path,
    limit: int | None = None,
    sample_size: int = 50,
    top_k: int = 20,
) -> dict[str, Any]:
    in_path = Path(input_path)
    out_dir = Path(outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stage = LanguageStage()

    rows_total = 0
    invalid_rows = 0
    decisions: list[tuple[CanonicalRawJob, LanguageDecision]] = []

    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
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
            decisions.append((canonical, decision))
            rows_total += 1
            if limit is not None and rows_total >= limit:
                break

    by_bucket = Counter(dec.bucket for _, dec in decisions)
    reasons_by_bucket: dict[str, Counter[str]] = {
        "en": Counter(),
        "non_en": Counter(),
        "unknown": Counter(),
    }
    titles_by_bucket: dict[str, Counter[str]] = {
        "en": Counter(),
        "non_en": Counter(),
        "unknown": Counter(),
    }

    for canonical, decision in decisions:
        reasons_by_bucket[decision.bucket][decision.reason] += 1
        titles_by_bucket[decision.bucket][canonical.title] += 1

    def _pct(v: int) -> float:
        return round((v * 100.0 / rows_total), 2) if rows_total else 0.0

    def _write_samples(bucket: str) -> str:
        path = out_dir / f"sample_{bucket}.jsonl"
        written = 0
        with path.open("w", encoding="utf-8") as f:
            for canonical, decision in decisions:
                if decision.bucket != bucket:
                    continue
                record = {
                    "url": canonical.url,
                    "source": canonical.source,
                    "source_org": canonical.source_org,
                    "external_id": canonical.external_id,
                    "title": canonical.title,
                    "language_hint": canonical.language_hint,
                    "bucket": decision.bucket,
                    "reason": decision.reason,
                    "language_code": decision.language_code,
                    "confidence": decision.confidence,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                written += 1
                if written >= sample_size:
                    break
        return str(path)

    sample_paths = {
        "en": _write_samples("en"),
        "non_en": _write_samples("non_en"),
        "unknown": _write_samples("unknown"),
    }

    rows_en = by_bucket.get("en", 0)
    rows_non_en = by_bucket.get("non_en", 0)
    rows_unknown = by_bucket.get("unknown", 0)

    diagnostics: list[str] = []
    unknown_pct = _pct(rows_unknown)
    non_en_pct = _pct(rows_non_en)
    if unknown_pct >= 30.0:
        diagnostics.append("Policy likely too prudent on this corpus (high unknown rate).")
    if rows_en and non_en_pct <= 1.0 and unknown_pct <= 5.0:
        diagnostics.append("Policy may be too aggressive toward EN classification.")
    if not diagnostics:
        diagnostics.append("No obvious global imbalance detected from bucket ratios.")

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
        "sample_files": sample_paths,
        "top_titles_by_bucket": {
            b: [{"title": t, "count": c} for t, c in ctr.most_common(top_k)] for b, ctr in titles_by_bucket.items()
        },
        "top_reasons_by_bucket": {
            b: [{"reason": r, "count": c} for r, c in ctr.most_common(top_k)] for b, ctr in reasons_by_bucket.items()
        },
        "diagnostics": diagnostics,
    }

    json_path = out_dir / "language_eval_step6.json"
    md_path = out_dir / "language_eval_step6.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines: list[str] = []
    md_lines.append("# Language Eval Step 6")
    md_lines.append("")
    md_lines.append(f"Input: `{in_path}`")
    md_lines.append("")
    md_lines.append("## Counts")
    md_lines.append(f"- rows_total: {rows_total}")
    md_lines.append(f"- invalid_rows: {invalid_rows}")
    md_lines.append(f"- rows_en: {rows_en} ({_pct(rows_en)}%)")
    md_lines.append(f"- rows_non_en: {rows_non_en} ({_pct(rows_non_en)}%)")
    md_lines.append(f"- rows_unknown: {rows_unknown} ({_pct(rows_unknown)}%)")
    md_lines.append("")
    md_lines.append("## Sample Files")
    md_lines.append(f"- en: `{sample_paths['en']}`")
    md_lines.append(f"- non_en: `{sample_paths['non_en']}`")
    md_lines.append(f"- unknown: `{sample_paths['unknown']}`")
    md_lines.append("")

    for bucket in ("en", "non_en", "unknown"):
        md_lines.append(f"## Top Reasons ({bucket})")
        for item in report["top_reasons_by_bucket"][bucket][:10]:
            md_lines.append(f"- {item['reason']}: {item['count']}")
        md_lines.append("")

        md_lines.append(f"## Top Titles ({bucket})")
        for item in report["top_titles_by_bucket"][bucket][:10]:
            md_lines.append(f"- {item['title']}: {item['count']}")
        md_lines.append("")

    md_lines.append("## Diagnostics")
    for line in diagnostics:
        md_lines.append(f"- {line}")
    md_lines.append("")

    # Add one example per bucket for manual inspection.
    md_lines.append("## Examples")
    for bucket in ("en", "non_en", "unknown"):
        md_lines.append(f"### {bucket}")
        sample_file = Path(sample_paths[bucket])
        example = None
        if sample_file.exists():
            with sample_file.open("r", encoding="utf-8") as f:
                first = f.readline().strip()
                if first:
                    example = json.loads(first)
        if example:
            md_lines.append(f"- title: {example['title']}")
            md_lines.append(f"- reason: {example['reason']}")
            md_lines.append(f"- url: {example['url']}")
        else:
            md_lines.append("- (no sample)")
        md_lines.append("")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return report
