from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_jsonl, repo_root, write_json


NON_ROLE_TITLE_PATTERNS = [
    "general application",
    "general applications",
    "open application",
    "general interest",
    "future opportunities",
    "future opportunity",
    "talent community",
    "talent pool",
    "expression of interest",
    "apply here",
    "don’t see what you’re looking for",
    "don't see what you're looking for",
    "don't see a role that fits",
    "didn't see the role you were looking for",
    "drop your resume",
    "future consideration",
]

NON_ROLE_DESCRIPTION_PATTERNS = [
    "send us your resume",
    "keep your information on file",
    "don't see a position",
    "don't see an opportunity",
    "join our talent community",
    "future openings",
    "drop your resume",
    "apply for future opportunities",
]


def classify_non_role_candidate(title: str, description: str) -> tuple[bool, list[str]]:
    title_l = (title or "").lower()
    desc_l = (description or "").lower()
    hits: list[str] = []

    for pat in NON_ROLE_TITLE_PATTERNS:
        if pat in title_l:
            hits.append(f"title:{pat}")
    for pat in NON_ROLE_DESCRIPTION_PATTERNS:
        if pat in desc_l:
            hits.append(f"description:{pat}")

    return (len(hits) > 0), hits


def analyze_non_role_candidates(
    titled_path: Path,
    extracted_path: Path,
    out_path: Path,
) -> dict[str, Any]:
    extracted_by_url = {row["url"]: row for row in read_jsonl(extracted_path) if row.get("url")}
    titled_rows = read_jsonl(titled_path)

    candidates: list[dict[str, Any]] = []
    status_counter: Counter[str] = Counter()
    pattern_counter: Counter[str] = Counter()
    examples_by_pattern: defaultdict[str, list[str]] = defaultdict(list)

    for row in titled_rows:
        url = str(row.get("url") or "")
        extracted = extracted_by_url.get(url, {})
        description = " ".join(
            str(extracted.get(field) or "")
            for field in ("description_clean", "responsibilities_clean", "requirements_clean")
        )
        is_candidate, hits = classify_non_role_candidate(str(row.get("title_clean") or ""), description)
        if not is_candidate:
            continue

        status = str(row.get("classification_status") or "")
        status_counter[status] += 1
        for hit in hits:
            pattern_counter[hit] += 1
            if len(examples_by_pattern[hit]) < 5:
                examples_by_pattern[hit].append(str(row.get("title_raw") or ""))

        candidates.append(
            {
                "url": url,
                "company_name": row.get("company_name"),
                "title_raw": row.get("title_raw"),
                "title_clean": row.get("title_clean"),
                "classification_status": status,
                "normalized_title": row.get("normalized_title"),
                "role_family": row.get("role_family"),
                "matched_rule_id": row.get("matched_rule_id"),
                "pattern_hits": hits,
            }
        )

    payload = {
        "input_dataset": str(titled_path.relative_to(repo_root())),
        "rows_total": len(titled_rows),
        "candidate_count": len(candidates),
        "candidate_share": round(len(candidates) / len(titled_rows), 4) if titled_rows else 0.0,
        "status_counts": dict(status_counter),
        "top_pattern_hits": [
            {"pattern": pattern, "count": count, "examples": examples_by_pattern[pattern]}
            for pattern, count in pattern_counter.most_common(20)
        ],
        "sample_candidates": candidates[:50],
    }
    write_json(out_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/residual_audit/reports"
    result = analyze_non_role_candidates(
        titled_path=root / "data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl",
        extracted_path=root / "data/jobs/jobs_extracted_en.jsonl",
        out_path=reports / "non_role_recruiting_entry_analysis_v1.json",
    )
    print(result)
