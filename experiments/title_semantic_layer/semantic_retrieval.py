from __future__ import annotations

import json
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .common import cosine_sparse, hashed_ngram_vector, normalize_title, read_json, read_jsonl, repo_root, write_json

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover
    fuzz = None


def _lexical_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if fuzz is not None:
        return float(fuzz.token_sort_ratio(a, b)) / 100.0
    return SequenceMatcher(None, a, b).ratio()


def _topk(query_text: str, candidates: list[dict[str, Any]], k: int = 5) -> list[dict[str, Any]]:
    qn = normalize_title(query_text)
    qv = hashed_ngram_vector(qn)
    scored = []
    for c in candidates:
        text = c["text"]
        ln = c["normalized_text"]
        lv = c["vector"]
        lex = _lexical_score(qn, ln)
        sem = cosine_sparse(qv, lv)
        score = 0.55 * sem + 0.45 * lex
        scored.append(
            {
                "text": text,
                "score": round(score, 4),
                "lexical_score": round(lex, 4),
                "semantic_score": round(sem, 4),
                **c["meta"],
            }
        )
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]


def _build_internal_candidates(internal_corpus: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in internal_corpus.get("canonical_entries", []):
        normalized_title = row.get("normalized_title", "")
        role_family = row.get("role_family", "")
        aliases = row.get("aliases", []) or [normalize_title(normalized_title.replace("_", " "))]
        for alias in aliases:
            if not alias:
                continue
            out.append(
                {
                    "text": alias,
                    "normalized_text": normalize_title(alias),
                    "vector": hashed_ngram_vector(alias),
                    "meta": {
                        "normalized_title": normalized_title,
                        "role_family": role_family,
                        "source": "internal",
                    },
                }
            )
    return out


def _build_esco_candidates(esco_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in esco_rows:
        pref = row.get("preferred_label", "")
        labels = [pref] + list(row.get("alt_labels", []))
        for label in labels:
            label = (label or "").strip()
            if not label:
                continue
            out.append(
                {
                    "text": label,
                    "normalized_text": normalize_title(label),
                    "vector": hashed_ngram_vector(label),
                    "meta": {
                        "source": "esco",
                        "esco_concept_uri": row.get("concept_uri", ""),
                        "esco_preferred_label": pref,
                        "esco_broader_label": row.get("broader_label", ""),
                        "esco_isco_group": row.get("isco_group_label", ""),
                    },
                }
            )
    return out


def _build_onet_candidates(onet_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in onet_rows:
        title = row.get("title", "")
        labels = [title] + list(row.get("alternate_titles", []))
        for label in labels:
            label = (label or "").strip()
            if not label:
                continue
            out.append(
                {
                    "text": label,
                    "normalized_text": normalize_title(label),
                    "vector": hashed_ngram_vector(label),
                    "meta": {
                        "source": "onet",
                        "onet_soc_code": row.get("soc_code", ""),
                        "onet_title": title,
                    },
                }
            )
    return out


def run_semantic_retrieval(
    dataset_path: Path,
    internal_corpus_path: Path,
    esco_index_path: Path,
    onet_index_path: Path,
    out_path: Path,
    top_n_residual: int = 300,
) -> dict[str, Any]:
    rows = read_jsonl(dataset_path)

    residual_counter: Counter[str] = Counter()
    for row in rows:
        if str(row.get("classification_status") or "") == "other":
            title = str(row.get("title_raw") or "").strip()
            if title:
                residual_counter[title] += 1

    residual_top = residual_counter.most_common(top_n_residual)

    internal_corpus = read_json(internal_corpus_path)
    esco_rows = [json.loads(line) for line in esco_index_path.open("r", encoding="utf-8") if line.strip()]
    onet_rows = [json.loads(line) for line in onet_index_path.open("r", encoding="utf-8") if line.strip()]

    internal_candidates = _build_internal_candidates(internal_corpus)
    esco_candidates = _build_esco_candidates(esco_rows)
    onet_candidates = _build_onet_candidates(onet_rows)

    retrieval_rows = []
    for title, count in residual_top:
        retrieval_rows.append(
            {
                "title": title,
                "count": count,
                "top_internal": _topk(title, internal_candidates, k=5),
                "top_esco": _topk(title, esco_candidates, k=5),
                "top_onet": _topk(title, onet_candidates, k=5),
            }
        )

    payload = {
        "dataset": str(dataset_path),
        "rows_total": len(rows),
        "other_total": sum(residual_counter.values()),
        "residual_titles_considered": len(residual_top),
        "retrieval_rows": retrieval_rows,
    }
    write_json(out_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    out = root / "experiments/title_semantic_layer/reports/semantic_retrieval.json"
    result = run_semantic_retrieval(
        dataset_path=root / "data/jobs/jobs_titled_en_recovery_v53_safe.jsonl",
        internal_corpus_path=root / "experiments/title_semantic_layer/reports/internal_title_corpus.json",
        esco_index_path=root / "experiments/title_semantic_layer/reports/esco_index.jsonl",
        onet_index_path=root / "experiments/title_semantic_layer/reports/onet_index.jsonl",
        out_path=out,
    )
    print(f"semantic_retrieval -> {out} ({result['residual_titles_considered']} titles)")
