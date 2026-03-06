from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path

from jobintel.api import _compute_query_embedding, _cosine, _to_float_list


DEFAULT_QUERIES = [
    "senior data engineer remote",
    "python airflow dbt",
    "analytics director healthcare",
    "business analyst retail energy",
    "staff machine learning scientist",
    "solutions architect cloud",
    "enterprise account executive saas",
    "customer success manager",
    "technical recruiter contract",
    "product manager platform",
    "frontend react typescript",
    "devops kubernetes terraform",
    "data analyst tableau sql",
    "bi analyst power bi",
    "head of engineering",
    "hr business partner",
    "implementation consultant",
    "field cto",
    "ml engineer llm",
    "sales development representative",
]


def _load_embeddings(db_path: str) -> dict[str, list[float]]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT url, embedding_json FROM jobs_indexed "
        "WHERE url IS NOT NULL AND url <> '' AND embedding_json IS NOT NULL AND embedding_json <> ''"
    ).fetchall()
    out: dict[str, list[float]] = {}
    for row in rows:
        url = str(row["url"]).strip()
        if not url:
            continue
        emb = _to_float_list(row["embedding_json"])
        if emb:
            out[url] = emb
    return out


def _rank(url_to_emb: dict[str, list[float]], q_emb: list[float], k: int) -> list[str]:
    scored = [(_cosine(q_emb, emb), url) for url, emb in url_to_emb.items()]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [url for _, url in scored[:k]]


def _queries(path: str) -> list[str]:
    if not path:
        return DEFAULT_QUERIES
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):
        raise ValueError("--queries-json must contain list[str]")
    return raw


def main() -> None:
    ap = argparse.ArgumentParser(description="Export CSV for manual semantic eval (hash vs openai, Precision@3).")
    ap.add_argument("--hash-db", default="data/jobintel_microsaas.sqlite")
    ap.add_argument("--openai-db", default="data/jobintel_microsaas_openai.sqlite")
    ap.add_argument("--openai-model", default="text-embedding-3-small")
    ap.add_argument("--timeout-sec", type=int, default=20)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--queries-json", default="")
    ap.add_argument("--out", default="docs/semantic_eval_top3.csv")
    args = ap.parse_args()

    qs = _queries(args.queries_json)
    hash_map = _load_embeddings(args.hash_db)
    openai_map = _load_embeddings(args.openai_db)
    common = sorted(set(hash_map.keys()) & set(openai_map.keys()))
    if not common:
        raise RuntimeError("No common URLs between hash/openai DBs.")
    hash_common = {u: hash_map[u] for u in common}
    openai_common = {u: openai_map[u] for u in common}
    hash_dim = len(next(iter(hash_common.values())))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = [
        "query",
        "intent_notes",
        "hash_top1_url",
        "hash_top1_relevant",
        "hash_top2_url",
        "hash_top2_relevant",
        "hash_top3_url",
        "hash_top3_relevant",
        "openai_top1_url",
        "openai_top1_relevant",
        "openai_top2_url",
        "openai_top2_relevant",
        "openai_top3_url",
        "openai_top3_relevant",
        "winner",
        "review_notes",
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for q in qs:
            q_hash, _ = _compute_query_embedding(
                q,
                semantic_provider="hash",
                semantic_model=None,
                timeout_sec=args.timeout_sec,
                hash_dim=hash_dim,
            )
            q_openai, _ = _compute_query_embedding(
                q,
                semantic_provider="openai",
                semantic_model=args.openai_model,
                timeout_sec=args.timeout_sec,
                hash_dim=hash_dim,
            )
            hash_top = _rank(hash_common, q_hash, args.k)
            openai_top = _rank(openai_common, q_openai, args.k)
            row = [
                q,
                "",
                hash_top[0] if len(hash_top) > 0 else "",
                "",
                hash_top[1] if len(hash_top) > 1 else "",
                "",
                hash_top[2] if len(hash_top) > 2 else "",
                "",
                openai_top[0] if len(openai_top) > 0 else "",
                "",
                openai_top[1] if len(openai_top) > 1 else "",
                "",
                openai_top[2] if len(openai_top) > 2 else "",
                "",
                "",
                "",
            ]
            w.writerow(row)

    print(f"Wrote evaluation CSV: {out_path}")
    print(f"Queries: {len(qs)} | Common URLs: {len(common)}")


if __name__ == "__main__":
    main()

