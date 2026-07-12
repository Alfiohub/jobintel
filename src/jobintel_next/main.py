from __future__ import annotations

import argparse
import warnings

from .cli import main as cli_main


def main() -> None:
    """Deprecated compatibility wrapper.

    Legacy shape:
      python -m jobintel_next.main --config ... --out ...

    Official command surface:
      jobintel-next ingest run --config ... --out ...
    """
    warnings.warn(
        "jobintel_next.main is deprecated; use 'jobintel-next ingest run ...'",
        DeprecationWarning,
        stacklevel=2,
    )
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cli_main(["ingest", "run", "--config", args.config, "--out", args.out])


if __name__ == "__main__":
    main()
