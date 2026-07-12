from __future__ import annotations

import math
from pathlib import Path

from experiments.title_semantic_layer.common import read_jsonl, repo_root, write_json, write_jsonl


BATCH_SIZE = 25


def build_batches(sample_path: Path, out_dir: Path, index_path: Path) -> dict[str, object]:
    rows = read_jsonl(sample_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    batch_files: list[dict[str, object]] = []
    total_batches = math.ceil(len(rows) / BATCH_SIZE)
    for i in range(total_batches):
        start = i * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(rows))
        batch_rows = rows[start:end]
        batch_id = f"batch_{i + 1:02d}"
        batch_file = out_dir / f"{batch_id}.jsonl"
        write_jsonl(batch_file, batch_rows)
        batch_files.append(
            {
                "batch_id": batch_id,
                "batch_file": str(batch_file.relative_to(repo_root())),
                "start_index": start + 1,
                "end_index": end,
                "row_count": len(batch_rows),
                "expected_annotation_output": f"experiments/residual_audit/reports/annotations/{batch_id}_annotations.jsonl",
            }
        )

    payload = {
        "input_sample": str(sample_path.relative_to(repo_root())),
        "batch_size": BATCH_SIZE,
        "total_rows": len(rows),
        "total_batches": total_batches,
        "batches": batch_files,
    }
    write_json(index_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/residual_audit/reports"
    payload = build_batches(
        sample_path=reports / "residual_audit_sample_v1.jsonl",
        out_dir=reports / "chatgpt_batches_v1",
        index_path=reports / "chatgpt_batches_v1_index.json",
    )
    print(payload)
