from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import yaml


def _load_greenhouse_boards(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    boards = (((data.get("sources") or {}).get("greenhouse") or {}).get("boards")) or []
    return [str(x).strip() for x in boards if str(x).strip()]


def _top_companies_from_db(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            """
            SELECT company, COUNT(*) AS c
            FROM seen_jobs
            WHERE source='greenhouse'
            GROUP BY company
            ORDER BY c DESC, company ASC
            """
        ).fetchall()
    return [str(r[0]).strip() for r in rows if r and str(r[0]).strip()]


def build_subset(boards: list[str], ranked_companies: list[str], top_n: int) -> list[str]:
    board_set = set(boards)
    selected: list[str] = []
    seen: set[str] = set()

    for c in ranked_companies:
        if c in board_set and c not in seen:
            selected.append(c)
            seen.add(c)
            if len(selected) >= top_n:
                return selected

    # Fallback: if DB has fewer than top_n intersections, fill from original list order
    for b in boards:
        if b not in seen:
            selected.append(b)
            seen.add(b)
            if len(selected) >= top_n:
                break
    return selected


def write_targets(path: Path, boards: list[str]) -> None:
    payload = {
        "sources": {
            "greenhouse": {
                "enabled": True,
                "boards": boards,
                "content": True,
            }
        }
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a quality Greenhouse subset from existing targets + DB counts.")
    ap.add_argument("--input", default="config/generated/targets.yml")
    ap.add_argument("--db", default="data/jobintel.sqlite")
    ap.add_argument("--output", default="config/generated/targets_quality.yml")
    ap.add_argument("--top-n", type=int, default=500)
    args = ap.parse_args()

    inp = Path(args.input)
    dbp = Path(args.db)
    out = Path(args.output)

    boards = _load_greenhouse_boards(inp)
    ranked = _top_companies_from_db(dbp)
    subset = build_subset(boards=boards, ranked_companies=ranked, top_n=args.top_n)
    write_targets(out, subset)

    print(f"Input boards: {len(boards)}")
    print(f"Ranked companies in DB: {len(ranked)}")
    print(f"Wrote {out} with {len(subset)} greenhouse boards")


if __name__ == "__main__":
    main()

