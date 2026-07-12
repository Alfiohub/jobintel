from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract title/title_raw from JSONL into one-title-per-line txt")
    ap.add_argument("--input", required=True, help="Input JSONL path")
    ap.add_argument("--out", required=True, help="Output .txt path")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = 0
    written = 0
    with in_path.open("r", encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            s = line.strip()
            if not s:
                continue
            rows += 1
            try:
                obj = json.loads(s)
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            title = str(obj.get("title_raw") or obj.get("title") or "").strip()
            if not title:
                continue
            fout.write(title + "\n")
            written += 1

    print(f"Input rows read: {rows}")
    print(f"Titles written: {written}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
