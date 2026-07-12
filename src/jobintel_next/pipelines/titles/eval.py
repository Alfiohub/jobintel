from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from typing import Any


_CLUSTER_RULES: list[tuple[str, re.Pattern[str], str, str]] = [
    (
        "healthcare_clinical",
        re.compile(r"\b(nurse|physician|psychiat|therap|clinical|medical|practitioner)\b", re.IGNORECASE),
        "add_new_normalized_title",
        "Volume ricorrente e semanticamente chiaro in area clinica.",
    ),
    (
        "logistics",
        re.compile(r"\b(driver|cdl|delivery|warehouse|logistics)\b", re.IGNORECASE),
        "add_new_normalized_title",
        "Cluster operativo frequente non coperto dalla taxonomy minima v1.",
    ),
    (
        "skilled_trades",
        re.compile(r"\b(technician|mechanic|installer|painter|detailer)\b", re.IGNORECASE),
        "add_new_normalized_title",
        "Titoli skilled trades ripetuti e distinguibili dal titolo.",
    ),
    (
        "education",
        re.compile(r"\b(teacher|instructor|aide|education)\b", re.IGNORECASE),
        "add_new_normalized_title",
        "Cluster education support frequente e con segnali chiari.",
    ),
    (
        "design_creative",
        re.compile(r"\b(designer|copywriter|creative|brand|editor|journalist|producer)\b", re.IGNORECASE),
        "map_to_existing",
        "Parte mappabile a design/content; richiede regole più specifiche.",
    ),
    (
        "engineering_leadership",
        re.compile(r"\b(engineering manager|manager, software engineering|head of engineering)\b", re.IGNORECASE),
        "add_new_normalized_title",
        "Leadership engineering distinta da software_engineer individual contributor.",
    ),
    (
        "compliance_risk",
        re.compile(r"\b(compliance|risk|regulatory)\b", re.IGNORECASE),
        "add_new_normalized_title",
        "Dominio business-specific con volume non trascurabile.",
    ),
    (
        "customer_service",
        re.compile(r"\b(customer service|customer support|service advocate|call center)\b", re.IGNORECASE),
        "map_to_existing",
        "Cluster service spesso assorbibile in operations con regole mirate.",
    ),
    (
        "retail_sales",
        re.compile(r"\b(retail|store|sales associate|floor lead|stylist)\b", re.IGNORECASE),
        "add_new_normalized_title",
        "Cluster retail ricorrente e distinto dal sales enterprise B2B.",
    ),
]


def _cluster_for_title(title: str) -> tuple[str, str, str]:
    for cluster_name, pattern, action, rationale in _CLUSTER_RULES:
        if pattern.search(title):
            return cluster_name, action, rationale
    return "other_long_tail", "keep_other", "Lunga coda eterogenea o ambigua: mantenere other per ora."


def run_title_eval(
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

    rows_total = 0
    invalid_rows = 0
    by_title = Counter()
    by_family = Counter()
    by_status = Counter()
    matched_titles = Counter()
    other_titles = Counter()
    non_role_titles = Counter()
    sample_matched: list[dict[str, Any]] = []
    sample_other: list[dict[str, Any]] = []
    sample_non_role: list[dict[str, Any]] = []

    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            row = json.loads(s)
            if not isinstance(row, dict):
                invalid_rows += 1
                continue

            normalized_title = str(row.get("normalized_title") or "").strip()
            role_family = str(row.get("role_family") or "").strip()
            status = str(row.get("classification_status") or "").strip()
            title_clean = str(row.get("title_clean") or row.get("title") or "").strip()
            if not normalized_title or not role_family or not status:
                invalid_rows += 1
                continue

            rows_total += 1
            by_title[normalized_title] += 1
            by_family[role_family] += 1
            by_status[status] += 1
            if normalized_title == "other":
                other_titles[title_clean] += 1
                if len(sample_other) < sample_size:
                    sample_other.append(
                        {
                            "url": row.get("url"),
                            "title_clean": title_clean,
                            "normalized_title": normalized_title,
                            "role_family": role_family,
                            "classification_status": status,
                            "match_method": row.get("match_method"),
                            "notes": row.get("notes"),
                        }
                    )
            elif normalized_title == "non_role_recruiting_entry":
                non_role_titles[title_clean] += 1
                if len(sample_non_role) < sample_size:
                    sample_non_role.append(
                        {
                            "url": row.get("url"),
                            "title_clean": title_clean,
                            "normalized_title": normalized_title,
                            "role_family": role_family,
                            "classification_status": status,
                            "match_method": row.get("match_method"),
                            "notes": row.get("notes"),
                        }
                    )
            else:
                matched_titles[title_clean] += 1
                if len(sample_matched) < sample_size:
                    sample_matched.append(
                        {
                            "url": row.get("url"),
                            "title_clean": title_clean,
                            "normalized_title": normalized_title,
                            "role_family": role_family,
                            "classification_status": status,
                            "match_method": row.get("match_method"),
                            "confidence": row.get("confidence"),
                        }
                    )

            if limit is not None and rows_total >= limit:
                break

    clusters_acc: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"cluster_name": "", "sample_titles": [], "total_frequency": 0, "recommended_action": "", "rationale": ""}
    )
    for title, count in other_titles.items():
        cluster_name, action, rationale = _cluster_for_title(title)
        c = clusters_acc[cluster_name]
        c["cluster_name"] = cluster_name
        c["total_frequency"] += count
        c["recommended_action"] = action
        c["rationale"] = rationale
        if len(c["sample_titles"]) < 10:
            c["sample_titles"].append(title)

    clusters = sorted(clusters_acc.values(), key=lambda x: int(x["total_frequency"]), reverse=True)

    report = {
        "input_path": str(in_path),
        "rows_total": rows_total,
        "invalid_rows": invalid_rows,
        "counts_by_normalized_title": dict(by_title),
        "counts_by_role_family": dict(by_family),
        "counts_by_status": dict(by_status),
        "top_other_titles": [{"title_clean": t, "count": c} for t, c in other_titles.most_common(top_k)],
        "top_non_role_titles": [{"title_clean": t, "count": c} for t, c in non_role_titles.most_common(top_k)],
        "top_matched_titles": [{"title_clean": t, "count": c} for t, c in matched_titles.most_common(top_k)],
        "sample_matched_rows_file": str(out_dir / "sample_title_matched_step13.jsonl"),
        "sample_other_rows_file": str(out_dir / "sample_title_other_step13.jsonl"),
        "sample_non_role_rows_file": str(out_dir / "sample_title_non_role_step13.jsonl"),
        "other_clusters_file": str(out_dir / "title_other_clusters_step13.json"),
    }

    (out_dir / "title_eval_step13.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "title_other_clusters_step13.json").write_text(json.dumps(clusters, ensure_ascii=False, indent=2), encoding="utf-8")

    with (out_dir / "sample_title_matched_step13.jsonl").open("w", encoding="utf-8") as f:
        for row in sample_matched:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (out_dir / "sample_title_other_step13.jsonl").open("w", encoding="utf-8") as f:
        for row in sample_other:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (out_dir / "sample_title_non_role_step13.jsonl").open("w", encoding="utf-8") as f:
        for row in sample_non_role:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    md_lines = [
        "# Title Eval Step 13",
        "",
        f"Input: `{in_path}`",
        "",
        "## Counts",
        f"- rows_total: {rows_total}",
        f"- invalid_rows: {invalid_rows}",
        "",
        "## Counts by Status",
    ]
    for k, v in by_status.most_common():
        md_lines.append(f"- {k}: {v}")
    md_lines += [
        "",
        "## Top Matched Titles",
    ]
    for item in report["top_matched_titles"][:20]:
        md_lines.append(f"- {item['title_clean']}: {item['count']}")
    md_lines += [
        "",
        "## Top Other Titles",
    ]
    for item in report["top_other_titles"][:20]:
        md_lines.append(f"- {item['title_clean']}: {item['count']}")
    md_lines += [
        "",
        "## Top Non-Role Titles",
    ]
    for item in report["top_non_role_titles"][:20]:
        md_lines.append(f"- {item['title_clean']}: {item['count']}")
    md_lines += [
        "",
        "## Other Clusters",
    ]
    for cluster in clusters:
        md_lines.append(f"- {cluster['cluster_name']}: {cluster['total_frequency']} | action={cluster['recommended_action']}")
    md_lines += [
        "",
        "## Sample Files",
        f"- matched: `{out_dir / 'sample_title_matched_step13.jsonl'}`",
        f"- other: `{out_dir / 'sample_title_other_step13.jsonl'}`",
        f"- clusters: `{out_dir / 'title_other_clusters_step13.json'}`",
    ]
    (out_dir / "title_eval_step13.md").write_text("\n".join(md_lines), encoding="utf-8")
    return report
