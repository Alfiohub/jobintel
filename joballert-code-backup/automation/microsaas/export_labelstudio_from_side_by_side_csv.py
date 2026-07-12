from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _s(v: Any) -> str:
    return str(v or "").strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Export Label Studio tasks from manual_qa_side_by_side.csv")
    ap.add_argument("--input-csv", default="docs/manual_qa_side_by_side.csv")
    ap.add_argument("--output-json", default="docs/labelstudio_tasks_side_by_side.json")
    args = ap.parse_args()

    in_path = Path(args.input_csv)
    out_path = Path(args.output_json)

    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows in {in_path}")

    tasks = []
    for r in rows:
        tasks.append(
            {
                "data": {
                    "job_indexed_id": _s(r.get("job_indexed_id")),
                    "url": _s(r.get("url")),
                    "title_clean": _s(r.get("title_clean")),
                    "description_for_qa": _s(r.get("description_for_qa")),
                    "gold_normalized_title": _s(r.get("gold_normalized_title")),
                    "gold_role_family": _s(r.get("gold_role_family")),
                    "gold_location_type": _s(r.get("gold_location_type")),
                    "qa_fix_location_type": _s(r.get("qa_fix_location_type")),
                    "gold_location_city": _s(r.get("gold_location_city")),
                    "qa_fix_location_city": _s(r.get("qa_fix_location_city")),
                    "gold_country": _s(r.get("gold_country")),
                    "qa_fix_country": _s(r.get("qa_fix_country")),
                    "gold_employment_type": _s(r.get("gold_employment_type")),
                    "qa_fix_employment_type": _s(r.get("qa_fix_employment_type")),
                    "gold_seniority": _s(r.get("gold_seniority")),
                    "qa_fix_seniority": _s(r.get("qa_fix_seniority")),
                    "gold_salary_min": _s(r.get("gold_salary_min")),
                    "qa_fix_salary_min": _s(r.get("qa_fix_salary_min")),
                    "gold_salary_max": _s(r.get("gold_salary_max")),
                    "qa_fix_salary_max": _s(r.get("qa_fix_salary_max")),
                    "gold_salary_currency": _s(r.get("gold_salary_currency")),
                    "qa_fix_salary_currency": _s(r.get("qa_fix_salary_currency")),
                    "gold_salary_period": _s(r.get("gold_salary_period")),
                    "qa_fix_salary_period": _s(r.get("qa_fix_salary_period")),
                    "qa_status": _s(r.get("qa_status")),
                    "qa_notes": _s(r.get("qa_notes")),
                }
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")
    print(f"Tasks: {len(tasks)}")


if __name__ == "__main__":
    main()
