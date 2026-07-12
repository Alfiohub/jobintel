from __future__ import annotations

import argparse
import csv
import random
import sqlite3
from collections import Counter
from collections import defaultdict
from pathlib import Path
from typing import Any


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def _load_rows(con: sqlite3.Connection, *, source: str, language: str) -> list[dict[str, Any]]:
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
          ji.city,
          ji.country,
          ji.salary_min,
          ji.salary_max,
          ji.salary_currency,
          jc.language,
          jc.description_clean
        FROM jobs_indexed ji
        LEFT JOIN jobs_clean jc ON jc.id = ji.clean_job_id
        WHERE ji.url IS NOT NULL
          AND ji.url <> ''
          AND lower(trim(ji.source)) = lower(trim(?))
          AND (
            lower(trim(coalesce(jc.language, ''))) = lower(trim(?))
            OR lower(trim(coalesce(jc.language, ''))) LIKE lower(trim(?))
          )
        ORDER BY ji.id
        """
        ,
        (source, language, f"{language}-%"),
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


def _norm_token(value: Any, default: str) -> str:
    s = str(value or "").strip().lower()
    return s if s else default


def _salary_present(row: dict[str, Any]) -> str:
    return "has_salary" if row.get("salary_min") is not None or row.get("salary_max") is not None else "no_salary"


def _count_by_bucket(rows: list[dict[str, Any]], key_fn: Any) -> Counter[str]:
    c: Counter[str] = Counter()
    for r in rows:
        c[key_fn(r)] += 1
    return c


def _make_targets(
    rows: list[dict[str, Any]],
    *,
    target_size: int,
    enabled: bool,
    key_fn: Any,
) -> dict[str, float]:
    if not enabled or target_size <= 0:
        return {}
    counts = _count_by_bucket(rows, key_fn)
    n = max(1, len(rows))
    return {k: (v / n) * target_size for k, v in counts.items()}


def _stratified_sample_with_controls(
    rows: list[dict[str, Any]],
    *,
    target_size: int,
    seed: int,
    control_seniority: bool,
    control_location_type: bool,
    control_salary_presence: bool,
    target_other_title_share: float | None,
) -> list[dict[str, Any]]:
    # Keep legacy behavior when no extra controls are requested.
    if (
        not control_seniority
        and not control_location_type
        and not control_salary_presence
        and target_other_title_share is None
    ):
        return _stratified_sample(rows, target_size=target_size, seed=seed)

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

    sen_targets = _make_targets(
        rows,
        target_size=target_size,
        enabled=control_seniority,
        key_fn=lambda r: _norm_token(r.get("seniority"), "unspecified"),
    )
    loc_targets = _make_targets(
        rows,
        target_size=target_size,
        enabled=control_location_type,
        key_fn=lambda r: _norm_token(r.get("location_type"), "unspecified"),
    )
    sal_targets = _make_targets(
        rows,
        target_size=target_size,
        enabled=control_salary_presence,
        key_fn=_salary_present,
    )
    other_target: float | None = None
    if target_other_title_share is not None:
        other_target = max(0.0, min(1.0, float(target_other_title_share))) * target_size

    sampled: list[dict[str, Any]] = []
    taken_urls: set[str] = set()
    sen_count: Counter[str] = Counter()
    loc_count: Counter[str] = Counter()
    sal_count: Counter[str] = Counter()
    other_count = 0

    def _add(row: dict[str, Any]) -> bool:
        nonlocal other_count
        url = str(row.get("url") or "")
        if not url or url in taken_urls:
            return False
        sampled.append(row)
        taken_urls.add(url)
        if control_seniority:
            sen_count[_norm_token(row.get("seniority"), "unspecified")] += 1
        if control_location_type:
            loc_count[_norm_token(row.get("location_type"), "unspecified")] += 1
        if control_salary_presence:
            sal_count[_salary_present(row)] += 1
        if _norm_token(row.get("normalized_title"), "other") == "other":
            other_count += 1
        return True

    def _candidate_score(row: dict[str, Any]) -> float:
        score = 0.0
        if control_seniority:
            k = _norm_token(row.get("seniority"), "unspecified")
            score += max(0.0, sen_targets.get(k, 0.0) - sen_count.get(k, 0))
        if control_location_type:
            k = _norm_token(row.get("location_type"), "unspecified")
            score += max(0.0, loc_targets.get(k, 0.0) - loc_count.get(k, 0))
        if control_salary_presence:
            k = _salary_present(row)
            score += max(0.0, sal_targets.get(k, 0.0) - sal_count.get(k, 0))
        if other_target is not None:
            is_other = _norm_token(row.get("normalized_title"), "other") == "other"
            if is_other:
                score += max(0.0, other_target - other_count)
            elif other_count > other_target:
                score += 1.0
        return score

    # Minimum 1 per family where possible.
    for fam in families:
        if len(sampled) >= target_size:
            break
        if not by_family[fam]:
            continue
        best_idx, _ = max(enumerate(by_family[fam]), key=lambda x: _candidate_score(x[1]))
        row = by_family[fam].pop(best_idx)
        _add(row)

    fam_idx = 0
    while len(sampled) < target_size and any(by_family[f] for f in families):
        fam = families[fam_idx % len(families)]
        fam_idx += 1
        if not by_family[fam]:
            continue
        best_idx, _ = max(enumerate(by_family[fam]), key=lambda x: _candidate_score(x[1]))
        row = by_family[fam].pop(best_idx)
        _add(row)

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
        "pred_city",
        "pred_country",
        "pred_salary_min",
        "pred_salary_max",
        "pred_salary_currency",
        # Gold labels to fill
        "gold_normalized_title",
        "gold_role_family",
        "gold_experience_years_min",
        "gold_experience_years_max",
        "gold_experience_required",
        "gold_education_level",
        "gold_degree_required",
        "gold_soft_skills",
        "gold_location_type",
        "gold_country",
        "gold_location_city",
        "gold_employment_type",
        "gold_seniority",
        "gold_language_requirements",
        "gold_salary_min",
        "gold_salary_max",
        "gold_salary_currency",
        "gold_salary_period",
        "gold_tools_tech",
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
                    "pred_city": r.get("city") or "",
                    "pred_country": r.get("country") or "",
                    "pred_salary_min": r.get("salary_min") or "",
                    "pred_salary_max": r.get("salary_max") or "",
                    "pred_salary_currency": r.get("salary_currency") or "",
                    "gold_normalized_title": "",
                    "gold_role_family": "",
                    "gold_experience_years_min": "",
                    "gold_experience_years_max": "",
                    "gold_experience_required": "",
                    "gold_education_level": "",
                    "gold_degree_required": "",
                    "gold_soft_skills": "",
                    "gold_location_type": "",
                    "gold_country": "",
                    "gold_location_city": "",
                    "gold_employment_type": "",
                    "gold_seniority": "",
                    "gold_language_requirements": "",
                    "gold_salary_min": "",
                    "gold_salary_max": "",
                    "gold_salary_currency": "",
                    "gold_salary_period": "",
                    "gold_tools_tech": "",
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
    ap.add_argument("--source", default="greenhouse", help="Limit sample to one source.")
    ap.add_argument("--language", default="en", help="Language filter, e.g. en (matches en and en-*).")
    ap.add_argument("--control-seniority", action="store_true", help="Preserve seniority distribution in sample.")
    ap.add_argument(
        "--control-location-type",
        action="store_true",
        help="Preserve location_type distribution in sample.",
    )
    ap.add_argument(
        "--control-salary-presence",
        action="store_true",
        help="Preserve has_salary/no_salary distribution in sample.",
    )
    ap.add_argument(
        "--target-other-title-share",
        type=float,
        default=None,
        help="Optional target share (0..1) for normalized_title == 'other'.",
    )
    args = ap.parse_args()

    con = _connect(args.db)
    rows = _load_rows(con, source=args.source, language=args.language)
    con.close()

    if not rows:
        raise RuntimeError("No rows found in jobs_indexed. Run pipeline first.")

    sample = _stratified_sample_with_controls(
        rows,
        target_size=args.size,
        seed=args.seed,
        control_seniority=args.control_seniority,
        control_location_type=args.control_location_type,
        control_salary_presence=args.control_salary_presence,
        target_other_title_share=args.target_other_title_share,
    )
    if not sample:
        raise RuntimeError("Sampling produced no rows.")

    out_path = Path(args.out)
    _write_csv(out_path, sample)
    print(f"Wrote: {out_path}")
    print(f"Requested size: {args.size} | Actual: {len(sample)}")
    print(
        "Controls:"
        f" seniority={int(args.control_seniority)}"
        f" location_type={int(args.control_location_type)}"
        f" salary_presence={int(args.control_salary_presence)}"
        f" target_other_title_share={args.target_other_title_share}"
    )

    other_share = sum(1 for r in sample if _norm_token(r.get("normalized_title"), "other") == "other") / max(1, len(sample))
    print(f"Sample normalized_title=='other' share: {other_share:.3f}")


if __name__ == "__main__":
    main()
