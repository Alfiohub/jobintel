from __future__ import annotations

import argparse
import csv
import random
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def _load_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        SELECT
          ji.id,
          ji.source,
          ji.source_job_id,
          ji.url,
          ji.company_name,
          ji.title_raw,
          ji.title_clean,
          ji.normalized_title,
          ji.role_family,
          ji.seniority,
          ji.employment_type,
          ji.location_type,
          ji.country,
          jc.description_clean
        FROM jobs_indexed ji
        LEFT JOIN jobs_clean jc ON jc.id = ji.clean_job_id
        WHERE ji.url IS NOT NULL AND ji.url <> ''
        ORDER BY ji.id
        """
    ).fetchall()
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append({k: r[k] for k in r.keys()})
    return out


def _stratified_sample(rows: list[dict[str, Any]], target_size: int, seed: int) -> list[dict[str, Any]]:
    if target_size <= 0:
        return []
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        fam = str(row.get("role_family") or "other")
        by_family[fam].append(row)

    rnd = random.Random(seed)
    for fam_rows in by_family.values():
        rnd.shuffle(fam_rows)

    families = sorted(by_family.keys(), key=lambda f: len(by_family[f]), reverse=True)
    if not families:
        return []

    # Minimum 1 per family (where available), then round-robin fill.
    sampled: list[dict[str, Any]] = []
    taken_urls: set[str] = set()
    for fam in families:
        if len(sampled) >= target_size:
            break
        if not by_family[fam]:
            continue
        row = by_family[fam].pop()
        url = str(row.get("url") or "")
        if url and url not in taken_urls:
            sampled.append(row)
            taken_urls.add(url)

    fam_idx = 0
    while len(sampled) < target_size and any(by_family[f] for f in families):
        fam = families[fam_idx % len(families)]
        fam_idx += 1
        if not by_family[fam]:
            continue
        row = by_family[fam].pop()
        url = str(row.get("url") or "")
        if not url or url in taken_urls:
            continue
        sampled.append(row)
        taken_urls.add(url)

    return sampled


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        # Stable identifiers/context
        "job_indexed_id",
        "source",
        "source_job_id",
        "url",
        "company_name",
        "title_raw",
        "title_clean",
        "description_clean_excerpt",
        # Current system predictions (for reviewer context)
        "pred_normalized_title",
        "pred_role_family",
        "pred_seniority",
        "pred_employment_type",
        "pred_location_type",
        "pred_country",
        # Gold labels to fill
        "gold_normalized_title",
        "gold_role_family",
        "gold_experience_years_min",
        "gold_experience_years_max",
        "gold_experience_required",
        "gold_education_level",
        "gold_degree_required",
        "gold_soft_skills",
        # QA metadata
        "labeler",
        "review_status",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            desc = str(r.get("description_clean") or "")
            w.writerow(
                {
                    "job_indexed_id": r.get("id"),
                    "source": r.get("source") or "",
                    "source_job_id": r.get("source_job_id") or "",
                    "url": r.get("url") or "",
                    "company_name": r.get("company_name") or "",
                    "title_raw": r.get("title_raw") or "",
                    "title_clean": r.get("title_clean") or "",
                    "description_clean_excerpt": desc[:600],
                    "pred_normalized_title": r.get("normalized_title") or "",
                    "pred_role_family": r.get("role_family") or "",
                    "pred_seniority": r.get("seniority") or "",
                    "pred_employment_type": r.get("employment_type") or "",
                    "pred_location_type": r.get("location_type") or "",
                    "pred_country": r.get("country") or "",
                    "gold_normalized_title": "",
                    "gold_role_family": "",
                    "gold_experience_years_min": "",
                    "gold_experience_years_max": "",
                    "gold_experience_required": "",
                    "gold_education_level": "",
                    "gold_degree_required": "",
                    "gold_soft_skills": "",
                    "labeler": "",
                    "review_status": "todo",
                    "notes": "",
                }
            )


def main() -> None:
    ap = argparse.ArgumentParser(description="Build stratified gold eval CSV from jobs_indexed.")
    ap.add_argument("--db", default="data/jobintel_microsaas.sqlite")
    ap.add_argument("--out", default="docs/gold_eval_set_v1.csv")
    ap.add_argument("--size", type=int, default=800)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    con = _connect(args.db)
    rows = _load_rows(con)
    con.close()

    if not rows:
        raise RuntimeError("No rows found in jobs_indexed. Run pipeline first.")

    sample = _stratified_sample(rows, target_size=args.size, seed=args.seed)
    if not sample:
        raise RuntimeError("Sampling produced no rows.")

    out_path = Path(args.out)
    _write_csv(out_path, sample)
    print(f"Wrote: {out_path}")
    print(f"Requested size: {args.size} | Actual: {len(sample)}")


if __name__ == "__main__":
    main()
