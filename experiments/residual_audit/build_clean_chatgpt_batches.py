from __future__ import annotations

from experiments.residual_audit.build_chatgpt_batches import build_batches
from experiments.title_semantic_layer.common import repo_root


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/residual_audit/reports"
    payload = build_batches(
        sample_path=reports / "residual_audit_sample_v2_clean.jsonl",
        out_dir=reports / "chatgpt_batches_v2_clean",
        index_path=reports / "chatgpt_batches_v2_clean_index.json",
    )
    print(payload)
