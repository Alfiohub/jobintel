from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import hashed_ngram_vector, read_json, repo_root, write_json


def build_embedding_manifest(internal_corpus: Path, esco_index: Path, onet_index: Path, out_path: Path) -> dict[str, Any]:
    method = "hashed_char_trigram_cosine"
    fallback_reason = "sentence-transformers not configured in this environment; using deterministic local semantic-lite vectors"

    internal = read_json(internal_corpus)
    esco_count = sum(1 for _ in esco_index.open("r", encoding="utf-8"))
    onet_count = sum(1 for _ in onet_index.open("r", encoding="utf-8"))

    probes = [
        "customer onboarding specialist",
        "mortgage loan officer",
        "senior salesforce administrator",
        "community health worker",
    ]
    probe_vectors = {
        p: {
            "non_zero_dims": len(hashed_ngram_vector(p)),
        }
        for p in probes
    }

    manifest = {
        "embedding_method": method,
        "fallback_reason": fallback_reason,
        "corpora_sizes": {
            "internal_canonical": int(internal.get("canonical_count", 0)),
            "esco_index_rows": esco_count,
            "onet_index_rows": onet_count,
        },
        "vector_probe": probe_vectors,
    }
    write_json(out_path, manifest)
    return manifest


if __name__ == "__main__":
    root = repo_root()
    manifest = build_embedding_manifest(
        root / "experiments/title_semantic_layer/reports/internal_title_corpus.json",
        root / "experiments/title_semantic_layer/reports/esco_index.jsonl",
        root / "experiments/title_semantic_layer/reports/onet_index.jsonl",
        root / "experiments/title_semantic_layer/reports/embedding_manifest.json",
    )
    print(f"embedding_manifest -> method={manifest['embedding_method']}")
