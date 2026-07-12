from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from .classifier import TitleClassifier
from .context_rules import decide_context_rule
from .io import row_to_cleaned, row_to_extracted


def run_title_stage(
    *,
    input_cleaned_path: str | Path,
    output_path: str | Path,
    input_extracted_path: str | Path | None = None,
    report_dir: str | Path = "docs",
    limit: int | None = None,
    top_k_other: int = 20,
) -> dict[str, Any]:
    cleaned_path = Path(input_cleaned_path)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_path_dir = Path(report_dir)
    report_path_dir.mkdir(parents=True, exist_ok=True)

    extracted_by_url: dict[str, dict[str, Any]] = {}
    if input_extracted_path:
        ex_path = Path(input_extracted_path)
        if ex_path.exists():
            with ex_path.open("r", encoding="utf-8") as fex:
                for line in fex:
                    s = line.strip()
                    if not s:
                        continue
                    row = json.loads(s)
                    if not isinstance(row, dict):
                        continue
                    ex = row_to_extracted(row)
                    if ex:
                        extracted_by_url[ex.url] = row

    classifier = TitleClassifier()
    rows_total = 0
    invalid_rows = 0
    by_title = Counter()
    by_family = Counter()
    by_status = Counter()
    other_titles = Counter()
    non_role_titles = Counter()

    with cleaned_path.open("r", encoding="utf-8") as src, out_path.open("w", encoding="utf-8") as out:
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

            out_row = dict(row)
            context_row = dict(row)
            if cleaned.url in extracted_by_url:
                # Keep lightweight extracted context available when input_extracted was provided.
                ex_row = extracted_by_url[cleaned.url]
                for key in (
                    "departments_raw",
                    "description_clean",
                    "requirements_clean",
                    "responsibilities_clean",
                    "seniority",
                    "employment_type",
                    "location_type",
                    "salary_min",
                    "salary_max",
                    "salary_currency",
                    "salary_period",
                    "skills",
                    "tags",
                ):
                    if key in ex_row and key not in out_row:
                        out_row[key] = ex_row.get(key)
                    if key in ex_row:
                        context_row[key] = ex_row.get(key)

            result = classifier.classify(url=cleaned.url, title_clean=cleaned.title_clean)
            if result.classification_status == "other":
                context_row.update({"url": cleaned.url, "title_clean": cleaned.title_clean})
                context_decision = decide_context_rule(context_row)
                if context_decision is not None:
                    result = result.__class__(
                        url=cleaned.url,
                        normalized_title=context_decision.normalized_title,
                        role_family=context_decision.role_family,
                        classification_status="matched",
                        match_method="rule_pattern",
                        confidence=context_decision.confidence,
                        matched_rule_id=context_decision.matched_rule_id,
                        notes=["context_rule_match"]
                        + [f"context_evidence:{hit}" for hit in context_decision.evidence_hits],
                    )

            out_row.update(result.to_dict())
            out.write(json.dumps(out_row, ensure_ascii=False) + "\n")

            rows_total += 1
            by_title[result.normalized_title] += 1
            by_family[result.role_family] += 1
            by_status[result.classification_status] += 1
            if result.normalized_title == "other":
                other_titles[cleaned.title_clean] += 1
            if result.normalized_title == "non_role_recruiting_entry":
                non_role_titles[cleaned.title_clean] += 1

            if limit is not None and rows_total >= limit:
                break

    report = {
        "input_cleaned_path": str(cleaned_path),
        "input_extracted_path": str(input_extracted_path) if input_extracted_path else None,
        "output_path": str(out_path),
        "rows_total": rows_total,
        "invalid_rows": invalid_rows,
        "counts_by_normalized_title": dict(by_title),
        "counts_by_role_family": dict(by_family),
        "counts_by_status": dict(by_status),
        "top_other_titles": [{"title_clean": t, "count": c} for t, c in other_titles.most_common(top_k_other)],
        "top_non_role_titles": [{"title_clean": t, "count": c} for t, c in non_role_titles.most_common(top_k_other)],
        "known_limits": [
            "Minimal taxonomy/rule set by design in step12.",
            "Classifier is title-centric; extracted context is optional and lightweight.",
            "Policy is conservative: ambiguous titles go to other.",
        ],
    }

    json_path = report_path_dir / "title_stage_step12.json"
    md_path = report_path_dir / "title_stage_step12.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Title Stage Step 12",
        "",
        f"Input cleaned: `{cleaned_path}`",
        f"Input extracted: `{input_extracted_path}`",
        f"Output: `{out_path}`",
        "",
        "## Counts",
        f"- rows_total: {rows_total}",
        f"- invalid_rows: {invalid_rows}",
        "",
        "## Counts by Status",
    ]
    for k, v in by_status.most_common():
        md_lines.append(f"- {k}: {v}")
    md_lines.append("")
    md_lines.append("## Top Other Titles")
    for item in report["top_other_titles"][:20]:
        md_lines.append(f"- {item['title_clean']}: {item['count']}")
    md_lines.append("")
    md_lines.append("## Top Non-Role Titles")
    for item in report["top_non_role_titles"][:20]:
        md_lines.append(f"- {item['title_clean']}: {item['count']}")
    md_lines.append("")
    md_lines.append("## Known Limits")
    for line in report["known_limits"]:
        md_lines.append(f"- {line}")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return report
