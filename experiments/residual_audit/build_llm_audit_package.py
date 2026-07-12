from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_jsonl, repo_root, write_json, write_jsonl


SAMPLE_SIZE = 400
RANDOM_SEED = 42


def _excerpt(text: str | None, limit: int) -> str:
    return " ".join(str(text or "").split())[:limit]


def _department_names(value: Any) -> list[str]:
    out: list[str] = []
    for item in value or []:
        name = str(item.get("name") or "").strip()
        if name:
            out.append(name)
    return out


def _skill_terms(value: Any, limit: int = 12) -> list[str]:
    out: list[str] = []
    for item in value or []:
        if isinstance(item, str):
            term = item.strip()
        elif isinstance(item, dict):
            term = str(item.get("name") or item.get("skill") or "").strip()
        else:
            term = ""
        if term:
            out.append(term)
        if len(out) >= limit:
            break
    return out


def build_audit_package(
    titled_path: Path,
    extracted_path: Path,
    out_jsonl: Path,
    out_manifest: Path,
) -> dict[str, Any]:
    titled_rows = [row for row in read_jsonl(titled_path) if row.get("classification_status") == "other"]
    extracted_by_url = {row["url"]: row for row in read_jsonl(extracted_path) if row.get("url")}

    rng = random.Random(RANDOM_SEED)
    sample_rows = rng.sample(titled_rows, min(SAMPLE_SIZE, len(titled_rows)))

    packaged_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(sample_rows, start=1):
        extracted = extracted_by_url.get(str(row.get("url") or ""), {})
        packaged_rows.append(
            {
                "sample_id": f"residual_audit_v1_{idx:04d}",
                "url": row.get("url"),
                "company_name": row.get("company_name"),
                "title_raw": row.get("title_raw"),
                "title_clean": row.get("title_clean"),
                "employment_type": row.get("employment_type"),
                "seniority": row.get("seniority"),
                "location": {
                    "city": row.get("city"),
                    "region": row.get("region"),
                    "country": row.get("country"),
                    "location_type": row.get("location_type"),
                },
                "source": row.get("source"),
                "current_status": row.get("classification_status"),
                "current_normalized_title": row.get("normalized_title"),
                "current_role_family": row.get("role_family"),
                "skills": _skill_terms(extracted.get("skills") or row.get("skills") or []),
                "departments": _department_names(extracted.get("departments_raw")),
                "description_excerpt": _excerpt(extracted.get("description_clean"), 900),
                "responsibilities_excerpt": _excerpt(extracted.get("responsibilities_clean"), 900),
                "requirements_excerpt": _excerpt(extracted.get("requirements_clean"), 700),
                "annotation_task": "Classify this residual record into one audit bucket and, only if justified, suggest a target label and role family.",
            }
        )

    manifest = {
        "input_dataset": str(titled_path.relative_to(repo_root())),
        "input_other_rows": len(titled_rows),
        "sample_size": len(packaged_rows),
        "random_seed": RANDOM_SEED,
        "output_jsonl": str(out_jsonl.relative_to(repo_root())),
        "annotation_schema": "experiments/residual_audit/annotation_schema.json",
        "annotation_prompt": "experiments/residual_audit/chatgpt_annotation_prompt.md",
    }

    write_jsonl(out_jsonl, packaged_rows)
    write_json(out_manifest, manifest)
    return manifest


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/residual_audit/reports"
    payload = build_audit_package(
        titled_path=root / "data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl",
        extracted_path=root / "data/jobs/jobs_extracted_en.jsonl",
        out_jsonl=reports / "residual_audit_sample_v1.jsonl",
        out_manifest=reports / "residual_audit_manifest_v1.json",
    )
    print(payload)
