from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from .title_classifier import TitleClassifier
from .title_evaluation import build_coverage_report


def _read_titles_from_txt(path: Path) -> List[str]:
    out: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            v = line.strip()
            if v:
                out.append(v)
    return out


def _read_titles_from_csv(path: Path) -> List[str]:
    out: List[str] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        preferred_col = None
        if reader.fieldnames:
            lowered = {c.lower(): c for c in reader.fieldnames}
            for key in ("title", "title_raw", "title_clean"):
                if key in lowered:
                    preferred_col = lowered[key]
                    break
            if preferred_col is None and reader.fieldnames:
                preferred_col = reader.fieldnames[0]
        for row in reader:
            val = str(row.get(preferred_col or "") or "").strip()
            if val:
                out.append(val)
    return out


def _read_titles_from_jsonl(path: Path) -> List[str]:
    out: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            obj = json.loads(s)
            if isinstance(obj, dict):
                val = str(obj.get("title_raw") or obj.get("title") or "").strip()
                if val:
                    out.append(val)
    return out


def _results_to_dicts(results: List[Any]) -> List[Dict[str, Any]]:
    return [r.model_dump() for r in results]


def _load_titles(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path} (cwd={Path.cwd()})")
    suf = path.suffix.lower()
    if suf == ".txt":
        return _read_titles_from_txt(path)
    if suf == ".csv":
        return _read_titles_from_csv(path)
    if suf == ".jsonl":
        return _read_titles_from_jsonl(path)
    raise ValueError(f"unsupported input format: {path.suffix} (use .txt/.csv/.jsonl)")


def _write_csv_rows(path: Path, headers: List[str], rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> None:
    ap = argparse.ArgumentParser(description="Title normalization subsystem CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_one = sub.add_parser("single", help="Classify one title")
    p_one.add_argument("--title", required=True)

    p_batch = sub.add_parser("batch", help="Classify titles from .txt/.csv/.jsonl")
    p_batch.add_argument("--input", required=True)
    p_batch.add_argument("--outdir", required=True)

    args = ap.parse_args()
    classifier = TitleClassifier()

    if args.cmd == "single":
        print(json.dumps(classifier.classify(args.title).model_dump(), ensure_ascii=False, indent=2))
        return

    in_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    try:
        titles = _load_titles(in_path)
    except FileNotFoundError as e:
        ap.error(str(e))
    except ValueError as e:
        ap.error(str(e))
    results = [classifier.classify(t) for t in titles]
    report = build_coverage_report(results)

    results_path = outdir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as f:
        for r in _results_to_dicts(results):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    coverage_path = outdir / "coverage_report.json"
    coverage_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    top_unmatched = report.get("top_unmatched_titles", [])
    _write_csv_rows(
        outdir / "top_unmatched_titles.csv",
        ["title_clean", "count"],
        [dict(x) for x in top_unmatched if isinstance(x, dict)],
    )

    by_title = report.get("counts_by_normalized_title", {})
    title_rows = [{"normalized_title": k, "count": v} for k, v in by_title.items()]
    title_rows.sort(key=lambda r: int(r["count"]), reverse=True)
    _write_csv_rows(outdir / "counts_by_normalized_title.csv", ["normalized_title", "count"], title_rows)

    by_family = report.get("counts_by_role_family", {})
    family_rows = [{"role_family": k, "count": v} for k, v in by_family.items()]
    family_rows.sort(key=lambda r: int(r["count"]), reverse=True)
    _write_csv_rows(outdir / "counts_by_role_family.csv", ["role_family", "count"], family_rows)

    print(f"Wrote: {results_path}")
    print(f"Wrote: {coverage_path}")
    print(f"Wrote: {outdir / 'top_unmatched_titles.csv'}")
    print(f"Wrote: {outdir / 'counts_by_normalized_title.csv'}")
    print(f"Wrote: {outdir / 'counts_by_role_family.csv'}")
    print(f"Rows: {report['rows']} | other_pct: {report['other_pct']}")


if __name__ == "__main__":
    main()
