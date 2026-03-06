from __future__ import annotations

import argparse
import re
import sqlite3
from collections import Counter
from pathlib import Path

import yaml


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\+\#\.\-]{1,}")

STOPWORDS = {
    "and",
    "the",
    "for",
    "with",
    "from",
    "into",
    "your",
    "you",
    "our",
    "are",
    "job",
    "jobs",
    "role",
    "team",
    "senior",
    "junior",
    "manager",
    "lead",
    "principal",
    "intern",
    "internship",
    "remote",
    "onsite",
    "hybrid",
    "new",
}

ALIASES = {
    "postgresql": "postgres",
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "ml": "machinelearning",
    "ai": "artificialintelligence",
}


def _normalize_token(token: str) -> str | None:
    t = token.strip().lower()
    if not t:
        return None
    t = ALIASES.get(t, t)
    if t in STOPWORDS:
        return None
    if len(t) < 2:
        return None
    return t


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN_RE.findall((text or "").lower()):
        n = _normalize_token(raw)
        if n:
            tokens.append(n)
    return tokens


def _fetch_rows(db_path: Path, source: str | None) -> list[tuple[str, str, str]]:
    sql = "SELECT title, company, location FROM seen_jobs"
    params: list[str] = []
    if source:
        sql += " WHERE source=?"
        params.append(source)

    with sqlite3.connect(db_path) as con:
        rows = con.execute(sql, params).fetchall()
    return [(str(r[0] or ""), str(r[1] or ""), str(r[2] or "")) for r in rows]


def _extract(rows: list[tuple[str, str, str]], top_n: int, min_count: int) -> dict:
    unigram = Counter()
    bigram = Counter()

    for title, company, location in rows:
        text = f"{title} {company} {location}".strip()
        tokens = _tokenize(text)
        if not tokens:
            continue
        unigram.update(tokens)
        for i in range(len(tokens) - 1):
            pair = f"{tokens[i]} {tokens[i+1]}"
            bigram[pair] += 1

    top_uni = [{"keyword": k, "count": c} for k, c in unigram.most_common(top_n) if c >= min_count]
    top_bi = [{"keyword": k, "count": c} for k, c in bigram.most_common(top_n) if c >= min_count]

    return {
        "top_unigrams": top_uni,
        "top_bigrams": top_bi,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract normalized keywords from seen_jobs.")
    ap.add_argument("--db", default="data/jobintel.sqlite")
    ap.add_argument("--source", default="", help="Optional source filter, e.g. greenhouse")
    ap.add_argument("--top-n", type=int, default=200)
    ap.add_argument("--min-count", type=int, default=20)
    ap.add_argument("--output", default="config/generated/keywords.yml")
    args = ap.parse_args()

    db_path = Path(args.db)
    rows = _fetch_rows(db_path, args.source.strip() or None)
    stats = _extract(rows=rows, top_n=args.top_n, min_count=args.min_count)

    payload = {
        "meta": {
            "db": str(db_path),
            "source": args.source.strip() or "all",
            "rows": len(rows),
            "top_n": args.top_n,
            "min_count": args.min_count,
        },
        "keywords": stats,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Rows scanned: {len(rows)}")
    print(f"Unigrams: {len(stats['top_unigrams'])}")
    print(f"Bigrams: {len(stats['top_bigrams'])}")


if __name__ == "__main__":
    main()

