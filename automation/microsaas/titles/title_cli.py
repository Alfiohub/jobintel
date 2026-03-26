from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from .title_classifier import TitleClassifier
from .title_evaluation import build_coverage_report


def _read_titles_from_csv(path: Path, column: str) -> list[str]:
    out: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            val = str(row.get(column) or "").strip()
            if val:
                out.append(val)
    return out


def _read_titles_from_jsonl(path: Path, key: str) -> list[str]:
    out: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            obj = json.loads(s)
            if isinstance(obj, dict):
                val = str(obj.get(key) or "").strip()
                if val:
                    out.append(val)
    return out


def _results_to_dicts(results: list[Any]) -> list[dict[str, Any]]:
    return [r.model_dump() for r in results]


def main() -> None:
    ap = argparse.ArgumentParser(description="Title normalization subsystem CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_one = sub.add_parser("classify-one", help="Classify one title")
    p_one.add_argument("--title", required=True)

    p_batch = sub.add_parser("classify-file", help="Classify titles from CSV or JSONL")
    p_batch.add_argument("--input", required=True)
    p_batch.add_argument("--format", choices=["csv", "jsonl"], required=True)
    p_batch.add_argument("--column", default="title_clean", help="CSV column or JSONL key")
    p_batch.add_argument("--out", required=True)

    p_rep = sub.add_parser("coverage-report", help="Classify + coverage report")
    p_rep.add_argument("--input", required=True)
    p_rep.add_argument("--format", choices=["csv", "jsonl"], required=True)
    p_rep.add_argument("--column", default="title_clean")
    p_rep.add_argument("--out", required=True)

    args = ap.parse_args()
    classifier = TitleClassifier()

    if args.cmd == "classify-one":
        print(json.dumps(classifier.classify(args.title).model_dump(), ensure_ascii=False, indent=2))
        return

    in_path = Path(args.input)
    if args.format == "csv":
        titles = _read_titles_from_csv(in_path, args.column)
    else:
        titles = _read_titles_from_jsonl(in_path, args.column)

    results = [classifier.classify(t) for t in titles]

    if args.cmd == "classify-file":
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(_results_to_dicts(results), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote: {out_path}")
        print(f"Rows: {len(results)}")
        return

    report = build_coverage_report(results)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")
    print(f"Rows: {report['rows']} | other_pct: {report['other_pct']}")


if __name__ == "__main__":
    main()
