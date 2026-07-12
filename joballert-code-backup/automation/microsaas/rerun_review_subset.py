from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


ALLOWED_LOCATION_TYPE = {"remote", "hybrid", "onsite", "unspecified"}
COUNTRY_ALIASES = {
    "us": "US",
    "usa": "US",
    "united states": "US",
    "uk": "GB",
    "united kingdom": "GB",
    "gb": "GB",
    "de": "DE",
    "germany": "DE",
    "fr": "FR",
    "france": "FR",
    "es": "ES",
    "spain": "ES",
    "it": "IT",
    "italy": "IT",
    "nl": "NL",
    "netherlands": "NL",
    "pl": "PL",
    "poland": "PL",
    "pt": "PT",
    "portugal": "PT",
    "ie": "IE",
    "ireland": "IE",
    "ch": "CH",
    "switzerland": "CH",
    "ro": "RO",
    "romania": "RO",
    "ca": "CA",
    "canada": "CA",
    "au": "AU",
    "australia": "AU",
    "in": "IN",
    "india": "IN",
}


def _s(value: Any) -> str:
    return str(value or "").strip()


def _is_review_row(row: dict[str, str]) -> bool:
    return _s(row.get("needs_review")) == "1" or _s(row.get("review_status")).lower() != "approved"


def _normalize_country(value: Any) -> str:
    raw = _s(value)
    if not raw:
        return ""
    k = re.sub(r"[^a-z0-9 ]", " ", raw.lower())
    k = re.sub(r"\s+", " ", k).strip()
    if k in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[k]
    compact = k.replace(" ", "")
    if len(compact) == 2 and compact.isalpha():
        return compact.upper()
    return ""


def _normalize_location_type(value: Any) -> str:
    s = _s(value).lower().replace("-", "_").replace(" ", "_")
    if not s:
        return ""
    return s if s in ALLOWED_LOCATION_TYPE else "unspecified"


def _extract_first_json_obj(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    start = -1
    depth = 0
    in_string = False
    escaped = False
    for i, ch in enumerate(text):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_string:
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    obj = json.loads(text[start : i + 1])
                    if isinstance(obj, dict):
                        return obj
                except Exception:
                    continue
    return None


def _call_ollama(
    prompt: str,
    *,
    model: str,
    url: str,
    timeout_sec: int,
    num_ctx: int,
    num_predict: int,
    num_thread: int | None,
) -> dict[str, Any]:
    options: dict[str, Any] = {"temperature": 0, "num_ctx": num_ctx, "num_predict": num_predict}
    if num_thread and num_thread > 0:
        options["num_thread"] = num_thread
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": options,
    }
    req = urlrequest.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout_sec) as resp:
        body = resp.read().decode("utf-8")
    raw = json.loads(body).get("response", "")
    if not isinstance(raw, str):
        raise RuntimeError("Ollama response missing response string")
    parsed = _extract_first_json_obj(raw)
    if not parsed:
        raise RuntimeError("Could not parse JSON object from Ollama response")
    return parsed


def _parse_set_arg(values: list[str] | None) -> set[str]:
    out: set[str] = set()
    for v in values or []:
        for part in v.split(","):
            tok = part.strip().lower()
            if tok:
                out.add(tok)
    return out


def _build_review_index(
    review_cases_path: Path,
    *,
    key_field: str,
    filter_categories: set[str],
    filter_primary: set[str],
) -> dict[str, dict[str, str]]:
    rows = list(csv.DictReader(review_cases_path.open("r", encoding="utf-8")))
    out: dict[str, dict[str, str]] = {}
    for r in rows:
        key = _s(r.get(key_field))
        if not key:
            continue
        cats = {_s(x).lower() for x in _s(r.get("review_categories")).split("|") if _s(x)}
        primary = _s(r.get("primary_review_category")).lower()
        if filter_categories and not (cats & filter_categories):
            continue
        if filter_primary and primary not in filter_primary:
            continue
        out[key] = {k: _s(v) for k, v in r.items()}
    return out


def _matches_filters(
    row: dict[str, str],
    *,
    filter_categories: set[str],
    filter_primary: set[str],
    review_meta: dict[str, str] | None,
) -> bool:
    if not filter_categories and not filter_primary:
        return _is_review_row(row)

    cats: set[str] = set()
    primary = ""
    if review_meta is not None:
        cats = {_s(x).lower() for x in _s(review_meta.get("review_categories")).split("|") if _s(x)}
        primary = _s(review_meta.get("primary_review_category")).lower()
    else:
        cats = {_s(x).lower() for x in _s(row.get("review_categories")).split("|") if _s(x)}
        primary = _s(row.get("primary_review_category")).lower()

    cat_ok = (not filter_categories) or bool(cats & filter_categories)
    pri_ok = (not filter_primary) or (primary in filter_primary)
    return _is_review_row(row) and cat_ok and pri_ok


def _prompt_for_rerun(row: dict[str, str], *, categories: str) -> str:
    excerpt = _s(row.get("description_clean_excerpt"))[:500]
    return (
        "You are doing a second-pass correction for a job labeling row already in review.\n"
        "Focus only on these fields: normalized_title, role_family, location_type, country.\n"
        "Return ONLY one JSON object with keys:\n"
        "rerun_gold_normalized_title, rerun_gold_role_family, rerun_gold_location_type, rerun_gold_country,\n"
        "rerun_confidence, rerun_needs_review, rerun_notes.\n"
        "Rules:\n"
        "- rerun_confidence must be 0..1 number.\n"
        "- rerun_location_type in {remote,hybrid,onsite,unspecified} or null.\n"
        "- rerun_country country name or ISO-2 or null.\n"
        "- rerun_needs_review true if still ambiguous.\n"
        f"review_categories: {categories}\n"
        f"title_raw: {_s(row.get('title_raw'))}\n"
        f"title_clean: {_s(row.get('title_clean'))}\n"
        f"description_clean_excerpt: {excerpt}\n"
        f"current_gold_normalized_title: {_s(row.get('gold_normalized_title'))}\n"
        f"current_gold_role_family: {_s(row.get('gold_role_family'))}\n"
        f"current_gold_location_type: {_s(row.get('gold_location_type'))}\n"
        f"current_gold_country: {_s(row.get('gold_country'))}\n"
    )


def _merge_policy(row: dict[str, str], rerun: dict[str, str], *, min_confidence: float) -> str:
    try:
        conf = float(_s(rerun.get("rerun_confidence")) or "0")
    except Exception:
        conf = 0.0
    needs_review = _s(rerun.get("rerun_needs_review")) in {"1", "true", "yes"}
    if conf < min_confidence or needs_review:
        return "still_review"

    rerun_values = [
        _s(rerun.get("rerun_gold_normalized_title")),
        _s(rerun.get("rerun_gold_role_family")),
        _s(rerun.get("rerun_gold_location_type")),
        _s(rerun.get("rerun_gold_country")),
    ]
    if not any(rerun_values):
        return "keep_original"

    changed = False
    if _s(rerun.get("rerun_gold_normalized_title")) and _s(rerun.get("rerun_gold_normalized_title")) != _s(row.get("gold_normalized_title")):
        changed = True
    if _s(rerun.get("rerun_gold_role_family")) and _s(rerun.get("rerun_gold_role_family")) != _s(row.get("gold_role_family")):
        changed = True
    if _s(rerun.get("rerun_gold_location_type")) and _s(rerun.get("rerun_gold_location_type")) != _s(row.get("gold_location_type")):
        changed = True
    if _s(rerun.get("rerun_gold_country")) and _s(rerun.get("rerun_gold_country")) != _s(row.get("gold_country")):
        changed = True
    return "use_rerun" if changed else "keep_original"


def main() -> None:
    ap = argparse.ArgumentParser(description="Rerun LLM only on selected review subset.")
    ap.add_argument("--input", required=True, help="Autolabeled CSV")
    ap.add_argument("--out", required=True, help="Output CSV with rerun_* columns")
    ap.add_argument("--review-cases", default="", help="Optional review_cases.csv from analyze_review_cases.py")
    ap.add_argument("--key-field", default="url", help="Join key between input and review_cases (default: url)")
    ap.add_argument("--filter-category", action="append", default=[], help="Category filter (repeatable or comma-separated)")
    ap.add_argument("--filter-primary", action="append", default=[], help="Primary category filter (repeatable or comma-separated)")
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/generate")
    ap.add_argument("--timeout-sec", type=int, default=120)
    ap.add_argument("--num-ctx", type=int, default=1024)
    ap.add_argument("--num-predict", type=int, default=180)
    ap.add_argument("--num-thread", type=int, default=1)
    ap.add_argument("--max-retries", type=int, default=2)
    ap.add_argument("--min-rerun-confidence", type=float, default=0.70)
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.out)
    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows found in {in_path}")

    filter_categories = _parse_set_arg(args.filter_category)
    filter_primary = _parse_set_arg(args.filter_primary)

    review_index: dict[str, dict[str, str]] = {}
    if _s(args.review_cases):
        review_index = _build_review_index(
            Path(args.review_cases),
            key_field=args.key_field,
            filter_categories=filter_categories,
            filter_primary=filter_primary,
        )

    rerun_count = 0
    errors = 0
    skipped = 0

    for row in rows:
        key = _s(row.get(args.key_field))
        review_meta = review_index.get(key) if review_index else None
        if review_index and not review_meta:
            skipped += 1
            continue
        if not _matches_filters(
            row,
            filter_categories=filter_categories,
            filter_primary=filter_primary,
            review_meta=review_meta,
        ):
            skipped += 1
            continue

        categories_txt = _s((review_meta or {}).get("review_categories") or row.get("review_categories"))

        try:
            out: dict[str, Any] | None = None
            last_err: Exception | None = None
            for _ in range(max(1, args.max_retries + 1)):
                try:
                    out = _call_ollama(
                        _prompt_for_rerun(row, categories=categories_txt),
                        model=args.model,
                        url=args.ollama_url,
                        timeout_sec=max(10, args.timeout_sec),
                        num_ctx=max(256, args.num_ctx),
                        num_predict=max(64, args.num_predict),
                        num_thread=(args.num_thread if args.num_thread > 0 else None),
                    )
                    break
                except RuntimeError as e:
                    last_err = e
                    if "Could not parse JSON object" not in str(e):
                        raise
            if out is None:
                raise last_err if last_err else RuntimeError("unknown rerun error")

            row["rerun_gold_normalized_title"] = _s(out.get("rerun_gold_normalized_title"))
            row["rerun_gold_role_family"] = _s(out.get("rerun_gold_role_family"))
            row["rerun_gold_location_type"] = _normalize_location_type(out.get("rerun_gold_location_type"))
            row["rerun_gold_country"] = _normalize_country(out.get("rerun_gold_country"))
            try:
                conf = float(out.get("rerun_confidence"))
            except Exception:
                conf = 0.0
            row["rerun_confidence"] = f"{conf:.3f}"
            row["rerun_needs_review"] = "1" if bool(out.get("rerun_needs_review")) else "0"
            row["rerun_notes"] = _s(out.get("rerun_notes"))
            row["rerun_policy"] = _merge_policy(row, row, min_confidence=args.min_rerun_confidence)
            rerun_count += 1
        except (urlerror.URLError, urlerror.HTTPError, TimeoutError, RuntimeError, ValueError) as e:
            row["rerun_confidence"] = "0.000"
            row["rerun_needs_review"] = "1"
            row["rerun_notes"] = f"rerun_error: {e}"
            row["rerun_policy"] = "still_review"
            errors += 1

    fieldnames = list(rows[0].keys())
    for extra in (
        "rerun_gold_normalized_title",
        "rerun_gold_role_family",
        "rerun_gold_location_type",
        "rerun_gold_country",
        "rerun_confidence",
        "rerun_needs_review",
        "rerun_notes",
        "rerun_policy",
    ):
        if extra not in fieldnames:
            fieldnames.append(extra)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote: {out_path}")
    print(f"Rows total: {len(rows)} | rerun_subset: {rerun_count} | errors: {errors} | skipped: {skipped}")


if __name__ == "__main__":
    main()

