from __future__ import annotations

import argparse
import warnings

from jobintel_next.cli import run_ingest_run


"""
Deprecated wrapper kept for compatibility.
Official command surface:
  jobintel-next ingest run --config ... --out ...
"""


def main() -> None:
    warnings.warn(
        "automation/export_greenhouse_jobs.py is deprecated; use 'jobintel-next ingest run ...'",
        DeprecationWarning,
        stacklevel=2,
    )
    ap = argparse.ArgumentParser(description="DEPRECATED wrapper: use jobintel-next ingest run")
    ap.add_argument("--config", required=True, help="YAML config containing sources.*")
    ap.add_argument("--output", required=True, help="Output JSONL path")
    args = ap.parse_args()
    raise SystemExit(run_ingest_run(args.config, args.output))


if __name__ == "__main__":
    main()
