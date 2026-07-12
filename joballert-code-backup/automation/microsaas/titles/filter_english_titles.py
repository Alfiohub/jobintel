from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from lingua import Language, LanguageDetectorBuilder


CANDIDATE_LANGUAGES = [
    Language.ENGLISH,
    Language.GERMAN,
    Language.FRENCH,
    Language.ITALIAN,
    Language.SPANISH,
    Language.DUTCH,
    Language.PORTUGUESE,
]

LANG_HINT_MAP = {
    "en": "en",
    "eng": "en",
    "english": "en",
    "de": "non_en",
    "ger": "non_en",
    "german": "non_en",
    "fr": "non_en",
    "fre": "non_en",
    "french": "non_en",
    "it": "non_en",
    "ita": "non_en",
    "italian": "non_en",
    "es": "non_en",
    "spa": "non_en",
    "spanish": "non_en",
    "nl": "non_en",
    "dut": "non_en",
    "dutch": "non_en",
    "pt": "non_en",
    "por": "non_en",
    "portuguese": "non_en",
}

NON_EN_HEURISTICS = [
    re.compile(r"\bm\s*-\s*w\s*-\s*d\b", re.IGNORECASE),
    re.compile(r"\bfür\b", re.IGNORECASE),
    re.compile(r"\bund\b", re.IGNORECASE),
    re.compile(r"\bmitarbeiter\b", re.IGNORECASE),
    re.compile(r"\bmechaniker\b", re.IGNORECASE),
    re.compile(r"\blagerlogistik\b", re.IGNORECASE),
    re.compile(r"\bmechatroniker\b", re.IGNORECASE),
]


def _s(value: Any) -> str:
    return str(value or "").strip()


def _pick_title(row: dict[str, Any]) -> str:
    title = _s(row.get("title") or row.get("title_raw"))
    if title:
        return title
    raw = row.get("raw_payload")
    if isinstance(raw, dict):
        return _s(raw.get("title") or raw.get("title_raw"))
    return ""


def _pick_language_hint(row: dict[str, Any]) -> str:
    candidates = [
        row.get("language"),
        row.get("language_hint"),
        row.get("lang"),
    ]
    raw = row.get("raw_payload")
    if isinstance(raw, dict):
        candidates.extend([raw.get("language"), raw.get("language_hint"), raw.get("lang")])
    for c in candidates:
        v = _s(c).lower()
        if v:
            return v
    return ""


def _lang_hint_bucket(lang_hint: str) -> str | None:
    if not lang_hint:
        return None
    cleaned = re.sub(r"[^a-z]", "", lang_hint.lower())
    if not cleaned:
        return None
    if cleaned in LANG_HINT_MAP:
        return LANG_HINT_MAP[cleaned]
    if cleaned.startswith("en"):
        return "en"
    if cleaned.startswith(("de", "fr", "it", "es", "nl", "pt")):
        return "non_en"
    return None


def _looks_non_english(text: str) -> bool:
    if not text:
        return False
    return any(p.search(text) for p in NON_EN_HEURISTICS)


def _is_too_short_or_ambiguous(text: str) -> bool:
    tokens = re.findall(r"[a-zA-Z]+", text)
    if not tokens:
        return True
    chars = sum(len(t) for t in tokens)
    if chars < 4:
        return True
    # very short and generic single-word titles are often ambiguous for language ID
    if len(tokens) == 1 and len(tokens[0]) <= 5:
        return True
    return False


def detect_bucket(
    *,
    title: str,
    lang_hint: str,
    detector: Any,
    min_confidence: float,
) -> tuple[str, str]:
    hint_bucket = _lang_hint_bucket(lang_hint)
    if hint_bucket == "en":
        return "en", "hint_en"
    if hint_bucket == "non_en":
        return "non_en", "hint_non_en"

    if _looks_non_english(title):
        return "non_en", "heuristic_non_en"

    if _is_too_short_or_ambiguous(title):
        return "unknown", "unknown_short_or_ambiguous"

    lang = detector.detect_language_of(title)
    if lang is None:
        return "unknown", "unknown_detector_none"

    confidences = detector.compute_language_confidence_values(title)
    top_conf = 0.0
    if confidences:
        top_conf = float(getattr(confidences[0], "value", 0.0) or 0.0)
    if top_conf < min_confidence:
        return "unknown", f"unknown_low_confidence_{top_conf:.2f}"

    if lang == Language.ENGLISH:
        return "en", f"detector_{lang.name.lower()}_{top_conf:.2f}"

    if lang in CANDIDATE_LANGUAGES:
        return "non_en", f"detector_{lang.name.lower()}_{top_conf:.2f}"

    return "unknown", f"unknown_out_of_scope_{lang.name.lower()}"


def _write_titles(path: Path, titles: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for t in titles:
            f.write(t + "\n")


def _to_top_rows(counter: Counter[str], top_k: int = 50) -> list[dict[str, Any]]:
    return [{"title": t, "count": c} for t, c in counter.most_common(top_k)]


def main() -> None:
    ap = argparse.ArgumentParser(description="Filter EN titles for evaluation hygiene")
    ap.add_argument("--input", default="data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl")
    ap.add_argument("--out-en", default="data/titles/all_greenhouse_titles_en_filtered.txt")
    ap.add_argument("--out-non-en", default="data/titles/all_greenhouse_titles_non_en.txt")
    ap.add_argument("--out-unknown", default="data/titles/all_greenhouse_titles_unknown.txt")
    ap.add_argument("--report-json", default="docs/title_language_filter_report.json")
    ap.add_argument("--report-md", default="docs/title_language_filter_report.md")
    ap.add_argument("--decisions-csv", default="docs/title_language_filter_decisions.csv")
    ap.add_argument("--decisions-jsonl", default="docs/title_language_filter_decisions.jsonl")
    ap.add_argument("--min-relative-distance", type=float, default=0.30)
    ap.add_argument("--min-confidence", type=float, default=0.55)
    args = ap.parse_args()

    detector = (
        LanguageDetectorBuilder.from_languages(*CANDIDATE_LANGUAGES)
        .with_minimum_relative_distance(max(0.0, args.min_relative_distance))
        .build()
    )

    in_path = Path(args.input)
    en_titles: list[str] = []
    non_en_titles: list[str] = []
    unknown_titles: list[str] = []

    non_en_counter: Counter[str] = Counter()
    unknown_counter: Counter[str] = Counter()
    reason_counter: Counter[str] = Counter()
    decision_rows: list[dict[str, Any]] = []

    rows_total = 0
    skipped_no_title = 0

    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            rows_total += 1
            try:
                row = json.loads(s)
            except Exception:
                continue
            if not isinstance(row, dict):
                continue

            title = _pick_title(row)
            if not title:
                skipped_no_title += 1
                continue
            lang_hint = _pick_language_hint(row)

            bucket, reason = detect_bucket(
                title=title,
                lang_hint=lang_hint,
                detector=detector,
                min_confidence=max(0.0, min(1.0, args.min_confidence)),
            )
            reason_counter[reason] += 1
            decision_rows.append(
                {
                    "bucket": bucket,
                    "reason": reason,
                    "title": title,
                    "url": _s(row.get("url")),
                    "source": _s(row.get("source")),
                    "source_org": _s(row.get("source_org")),
                    "external_id": _s(row.get("external_id")),
                    "language_hint_raw": lang_hint,
                }
            )

            if bucket == "en":
                en_titles.append(title)
            elif bucket == "non_en":
                non_en_titles.append(title)
                non_en_counter[title] += 1
            else:
                unknown_titles.append(title)
                unknown_counter[title] += 1

    _write_titles(Path(args.out_en), en_titles)
    _write_titles(Path(args.out_non_en), non_en_titles)
    _write_titles(Path(args.out_unknown), unknown_titles)

    kept = len(en_titles) + len(non_en_titles) + len(unknown_titles)
    report = {
        "input_path": str(in_path),
        "rows_total": rows_total,
        "rows_with_title": kept,
        "rows_skipped_no_title": skipped_no_title,
        "rows_en": len(en_titles),
        "rows_non_en": len(non_en_titles),
        "rows_unknown": len(unknown_titles),
        "pct_en": round((len(en_titles) * 100.0 / kept), 2) if kept else 0.0,
        "pct_non_en": round((len(non_en_titles) * 100.0 / kept), 2) if kept else 0.0,
        "pct_unknown": round((len(unknown_titles) * 100.0 / kept), 2) if kept else 0.0,
        "policy": {
            "language_hints_first": True,
            "detector": "lingua-language-detector",
            "candidate_languages": [l.name for l in CANDIDATE_LANGUAGES],
            "minimum_relative_distance": args.min_relative_distance,
            "minimum_confidence": args.min_confidence,
            "non_en_heuristics": [p.pattern for p in NON_EN_HEURISTICS],
            "notes": "Prefer conservative unknown/non_en over false EN classifications.",
        },
        "top_50_non_en_titles": _to_top_rows(non_en_counter, 50),
        "top_50_unknown_titles": _to_top_rows(unknown_counter, 50),
        "top_reason_counts": [{"reason": k, "count": v} for k, v in reason_counter.most_common(20)],
        "outputs": {
            "en_titles_txt": str(Path(args.out_en)),
            "non_en_titles_txt": str(Path(args.out_non_en)),
            "unknown_titles_txt": str(Path(args.out_unknown)),
            "decisions_csv": str(Path(args.decisions_csv)),
            "decisions_jsonl": str(Path(args.decisions_jsonl)),
        },
    }

    report_json_path = Path(args.report_json)
    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    decisions_csv_path = Path(args.decisions_csv)
    decisions_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with decisions_csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "bucket",
                "reason",
                "title",
                "url",
                "source",
                "source_org",
                "external_id",
                "language_hint_raw",
            ],
        )
        w.writeheader()
        for row in decision_rows:
            w.writerow(row)

    decisions_jsonl_path = Path(args.decisions_jsonl)
    decisions_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with decisions_jsonl_path.open("w", encoding="utf-8") as f:
        for row in decision_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    md_lines = [
        "# Title Language Filter Report",
        "",
        f"Input: `{in_path}`",
        "",
        "## Summary",
        f"- rows_total: {report['rows_total']}",
        f"- rows_with_title: {report['rows_with_title']}",
        f"- rows_en: {report['rows_en']} ({report['pct_en']}%)",
        f"- rows_non_en: {report['rows_non_en']} ({report['pct_non_en']}%)",
        f"- rows_unknown: {report['rows_unknown']} ({report['pct_unknown']}%)",
        "",
        "## Policy",
        "- Hints first (`language`/`language_hint` when present)",
        "- Lingua fallback on title text with constrained language set",
        f"- with_minimum_relative_distance({args.min_relative_distance})",
        f"- minimum confidence threshold: {args.min_confidence}",
        "- Heuristic non-EN override for strong non-English patterns (e.g. `m-w-d`, German tokens)",
        "",
        "## Audit Files",
        f"- decisions_csv: `{decisions_csv_path}`",
        f"- decisions_jsonl: `{decisions_jsonl_path}`",
        "- Ogni riga contiene bucket, reason e URL annuncio per controllo manuale.",
        "",
        "## Top 50 non_en",
    ]
    for row in report["top_50_non_en_titles"]:
        md_lines.append(f"- {row['count']}x {row['title']}")

    md_lines += ["", "## Top 50 unknown"]
    for row in report["top_50_unknown_titles"]:
        md_lines.append(f"- {row['count']}x {row['title']}")

    Path(args.report_md).write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Wrote: {args.out_en}")
    print(f"Wrote: {args.out_non_en}")
    print(f"Wrote: {args.out_unknown}")
    print(f"Wrote: {args.report_json}")
    print(f"Wrote: {args.report_md}")
    print(f"Wrote: {decisions_csv_path}")
    print(f"Wrote: {decisions_jsonl_path}")
    print(
        f"rows_total={rows_total} en={len(en_titles)} non_en={len(non_en_titles)} unknown={len(unknown_titles)}"
    )


if __name__ == "__main__":
    main()
