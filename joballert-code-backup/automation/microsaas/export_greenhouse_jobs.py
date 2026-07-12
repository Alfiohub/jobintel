from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jobintel.collectors.greenhouse import build_collector
from jobintel.config import load_config


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return value


def _job_to_row(job: Any) -> dict[str, Any]:
    if is_dataclass(job):
        data = asdict(job)
    else:
        raise TypeError(f"unsupported job type: {type(job)!r}")
    return _jsonable(data)


def main() -> None:
    ap = argparse.ArgumentParser(description="Export all Greenhouse jobs from config to canonical JSONL.")
    ap.add_argument("--config", required=True, help="YAML config containing sources.greenhouse.boards")
    ap.add_argument("--output", required=True, help="Output JSONL path")
    args = ap.parse_args()

    cfg = load_config(args.config)
    greenhouse_cfg = cfg.sources_raw.get("greenhouse", {})
    collector = build_collector(greenhouse_cfg)
    if collector is None:
        raise RuntimeError("greenhouse collector is disabled or has no boards configured")

    jobs = collector.fetch()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    seen_ids: set[str] = set()

    kept = 0
    with out_path.open("w", encoding="utf-8") as f:
        for job in jobs:
            row = _job_to_row(job)
            job_id = str(row.get("id") or "").strip()
            if job_id and job_id in seen_ids:
                continue
            if job_id:
                seen_ids.add(job_id)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            kept += 1

    print(f"Fetched jobs: {len(jobs)}")
    print(f"Wrote jobs: {kept}")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
