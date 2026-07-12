from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path
from typing import Any


def _s(value: Any) -> str:
    return str(value or "").strip()


def _load_full_descriptions(db_path: Path) -> dict[str, str]:
    if not db_path.exists():
        return {}
    con = sqlite3.connect(str(db_path))
    try:
        rows = con.execute(
            "SELECT ji.id, "
            "COALESCE(jc.description_clean, rj.description_raw, '') AS full_description "
            "FROM jobs_indexed ji "
            "LEFT JOIN jobs_clean jc ON jc.id = ji.clean_job_id "
            "LEFT JOIN raw_jobs rj ON rj.id = jc.raw_job_id"
        ).fetchall()
    finally:
        con.close()
    return {str(r[0]): _s(r[1]) for r in rows}


def main() -> None:
    ap = argparse.ArgumentParser(description="Export Label Studio tasks for manual QA with full description when available.")
    ap.add_argument("--input-csv", default="docs/gold_eval_set_v1_en_locv4_autolabeled.csv")
    ap.add_argument("--db", default="data/jobintel_microsaas_loccheck_2k_v4.sqlite")
    ap.add_argument("--output-json", default="docs/labelstudio_tasks_manual_qa_locv4.json")
    args = ap.parse_args()

    in_path = Path(args.input_csv)
    out_path = Path(args.output_json)
    db_path = Path(args.db)

    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows found in {in_path}")

    full_desc = _load_full_descriptions(db_path)

    tasks: list[dict[str, Any]] = []
    for r in rows:
        job_id = _s(r.get("job_indexed_id"))
        desc_full = full_desc.get(job_id, "")
        desc_excerpt = _s(r.get("description_clean_excerpt"))
        description = desc_full or desc_excerpt

        tasks.append(
            {
                "data": {
                    "job_indexed_id": job_id,
                    "url": _s(r.get("url")),
                    "title_clean": _s(r.get("title_clean")),
                    "description_clean": description,
                    "pred_location_type": _s(r.get("pred_location_type")),
                    "pred_city": _s(r.get("pred_city")),
                    "pred_country": _s(r.get("pred_country")),
                    "pred_employment_type": _s(r.get("pred_employment_type")),
                    "pred_seniority": _s(r.get("pred_seniority")),
                    "pred_salary_min": _s(r.get("pred_salary_min")),
                    "pred_salary_max": _s(r.get("pred_salary_max")),
                    "pred_salary_currency": _s(r.get("pred_salary_currency")),
                    "gold_location_type": _s(r.get("gold_location_type")),
                    "gold_location_city": _s(r.get("gold_location_city")),
                    "gold_country": _s(r.get("gold_country")),
                    "gold_employment_type": _s(r.get("gold_employment_type")),
                    "gold_seniority": _s(r.get("gold_seniority")),
                    "gold_salary_min": _s(r.get("gold_salary_min")),
                    "gold_salary_max": _s(r.get("gold_salary_max")),
                    "gold_salary_currency": _s(r.get("gold_salary_currency")),
                    "gold_salary_period": _s(r.get("gold_salary_period")),
                }
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")
    print(f"Tasks: {len(tasks)}")


if __name__ == "__main__":
    main()
