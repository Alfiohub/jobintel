from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from common import normalize_title


def split_labels(raw: str) -> list[str]:
    if not raw:
        return []
    parts: list[str] = []
    for block in raw.replace(";", "\n").split("\n"):
        s = block.strip()
        if s:
            parts.append(s)
    return parts


def run(esco_dir: Path, outdir: Path) -> dict[str, object]:
    occ_path = esco_dir / "occupations_en.csv"
    broad_path = esco_dir / "broaderRelationsOccPillar_en.csv"
    isco_path = esco_dir / "ISCOGroups_en.csv"

    uri_to_broader: dict[str, str] = {}
    if broad_path.exists():
        with broad_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                uri = (row.get("conceptUri") or "").strip()
                broader = (row.get("broaderLabel") or "").strip()
                if uri and broader:
                    uri_to_broader[uri] = broader

    isco_label: dict[str, str] = {}
    if isco_path.exists():
        with isco_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                uri = (row.get("conceptUri") or "").strip()
                label = (row.get("preferredLabel") or "").strip()
                if uri and label:
                    isco_label[uri] = label

    entries: list[dict[str, str]] = []
    occupations = 0
    aliases = 0
    with occ_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            occupations += 1
            uri = (row.get("conceptUri") or "").strip()
            pref = (row.get("preferredLabel") or "").strip()
            isco = (row.get("iscoGroup") or "").strip()
            broader = uri_to_broader.get(uri, "")
            isco_family = isco_label.get(f"http://data.europa.eu/esco/isco/{isco}", "") if isco else ""

            title_variants = [pref] + split_labels(row.get("altLabels") or "")
            seen: set[str] = set()
            for variant in title_variants:
                n = normalize_title(variant)
                if not n or n in seen:
                    continue
                seen.add(n)
                aliases += 1
                entries.append(
                    {
                        "source": "esco",
                        "normalized_title": n,
                        "raw_title": variant,
                        "canonical_title": pref,
                        "broader_label": broader,
                        "isco_family": isco_family,
                    }
                )

    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "esco_lookup.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    meta = {
        "occupations": occupations,
        "lookup_rows": len(entries),
        "aliases_processed": aliases,
        "files": {
            "occupations_en": str(occ_path),
            "broaderRelationsOccPillar_en": str(broad_path),
            "ISCOGroups_en": str(isco_path),
        },
    }
    (outdir / "esco_lookup_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def main() -> None:
    ap = argparse.ArgumentParser(description="Build ESCO lookup index")
    ap.add_argument("--esco-dir", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    run(Path(args.esco_dir), Path(args.outdir))


if __name__ == "__main__":
    main()
