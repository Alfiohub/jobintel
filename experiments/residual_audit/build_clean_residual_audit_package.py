from __future__ import annotations

from pathlib import Path

from experiments.residual_audit.build_llm_audit_package import build_audit_package
from experiments.title_semantic_layer.common import repo_root


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/residual_audit/reports"
    payload = build_audit_package(
        titled_path=root / "data/jobs/jobs_titled_en_recovery_v57_non_role_shadow.jsonl",
        extracted_path=root / "data/jobs/jobs_extracted_en.jsonl",
        out_jsonl=reports / "residual_audit_sample_v2_clean.jsonl",
        out_manifest=reports / "residual_audit_manifest_v2_clean.json",
    )
    print(payload)
