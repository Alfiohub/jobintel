from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from automation.microsaas.location_normalization import CITY_TO_COUNTRY, COUNTRY_ALIASES
except ModuleNotFoundError:
    from location_normalization import CITY_TO_COUNTRY, COUNTRY_ALIASES


US_STATE_CODES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}


def _s(v: Any) -> str:
    return str(v or "").strip()


def _norm(text: str) -> str:
    t = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    return re.sub(r"\s+", " ", t).strip()


def _to_iso2(value: str) -> str:
    raw = _s(value)
    if not raw:
        return ""
    n = _norm(raw)
    if not n:
        return ""
    if n in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[n]
    compact = n.replace(" ", "")
    if len(compact) == 2 and compact.isalpha():
        return compact.upper()
    return ""


def _city_country_guesses(city_raw: str) -> set[str]:
    city = _s(city_raw)
    if not city:
        return set()
    parts = [p.strip() for p in re.split(r"[|,;/&]+", city) if p.strip()]
    out: set[str] = set()
    for p in parts:
        guess = CITY_TO_COUNTRY.get(_norm(p))
        if guess:
            out.add(guess)
    return out


def _merge_notes(existing: str, tag: str) -> str:
    a = _s(existing)
    if not a:
        return tag
    if tag in a:
        return a
    return f"{a} | {tag}"


def main() -> None:
    ap = argparse.ArgumentParser(description="Deterministic country backfill/fix from existing city/country fields.")
    ap.add_argument("--input", default="docs/gold_eval_set_v1_en_locv5_autolabeled.csv")
    ap.add_argument("--output", default="docs/gold_eval_set_v1_en_locv5_autolabeled.csv")
    ap.add_argument("--backup", action="store_true")
    ap.add_argument("--report-json", default="docs/review_analysis_locv5/deterministic_country_rules_apply.json")
    ap.add_argument("--report-txt", default="docs/review_analysis_locv5/deterministic_country_rules_apply.txt")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    report_json = Path(args.report_json)
    report_txt = Path(args.report_txt)

    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows found in {in_path}")

    fieldnames = list(rows[0].keys())
    counters: Counter[str] = Counter()
    touched: list[dict[str, str]] = []

    for row in rows:
        jid = _s(row.get("job_indexed_id"))
        current_raw = _s(row.get("gold_country"))
        current = _to_iso2(current_raw)
        city = _s(row.get("gold_location_city"))
        city_guesses = sorted(_city_country_guesses(city))

        new_country = current
        reason = ""

        # Rule 1: normalize alias/full-name to ISO2 where possible.
        if current_raw and current and current_raw != current:
            new_country = current
            reason = "country_normalized_iso2"

        # Rule 2: empty country + unique city guess.
        if not new_country and len(city_guesses) == 1:
            new_country = city_guesses[0]
            reason = reason or "country_from_city_text"

        # Rule 3: state-code in country field + unique city guess.
        if current in US_STATE_CODES and len(city_guesses) == 1:
            new_country = city_guesses[0]
            reason = reason or "country_state_code_corrected_by_city"

        # Rule 4: clear mismatch with unique city guess.
        if new_country and len(city_guesses) == 1 and new_country != city_guesses[0]:
            new_country = city_guesses[0]
            reason = reason or "country_mismatch_corrected_by_city"

        if new_country and new_country != current_raw:
            row["gold_country"] = new_country
            row["notes"] = _merge_notes(_s(row.get("notes")), f"det_country_rule:{reason}")
            counters[reason] += 1
            touched.append(
                {
                    "job_indexed_id": jid,
                    "city": city,
                    "before_country": current_raw,
                    "after_country": new_country,
                    "reason": reason,
                }
            )

    if args.backup:
        backup_path = out_path.with_suffix(out_path.suffix + ".det_country_rules.bak")
        shutil.copy2(in_path, backup_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    report = {
        "input_csv": str(in_path),
        "output_csv": str(out_path),
        "rows": len(rows),
        "changed_rows": len(touched),
        "counts_by_reason": dict(counters),
        "sample_changes": touched[:200],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report_txt.parent.mkdir(parents=True, exist_ok=True)
    report_txt.write_text(
        "\n".join(
            [
                "Deterministic Country Backfill Report",
                f"rows: {len(rows)}",
                f"changed_rows: {len(touched)}",
                *(f"{k}: {v}" for k, v in sorted(counters.items())),
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote: {out_path}")
    print(f"Wrote: {report_json}")
    print(f"Wrote: {report_txt}")
    print(f"Changed rows: {len(touched)}")


if __name__ == "__main__":
    main()
