from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from pathlib import Path
from typing import Any

try:
    from automation.microsaas.title_normalization import TITLE_RULES
except ModuleNotFoundError:
    from title_normalization import TITLE_RULES


ROLE_FAMILY_TO_GROUP: dict[str, str] = {}
for _, _, fam, group in TITLE_RULES:
    ROLE_FAMILY_TO_GROUP.setdefault(fam, group)

ALLOWED_TITLES = {n for _, n, _, _ in TITLE_RULES} | {"other"}
ALLOWED_FAMILIES = {f for _, _, f, _ in TITLE_RULES} | {"other"}


def _s(v: Any) -> str:
    return str(v or "").strip()


def _slug(v: str) -> str:
    s = _s(v).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def _regex_from_sample_titles(sample_titles: str) -> str:
    # Keep only first 1-2 title phrases; avoid location tails.
    parts = [_s(p) for p in sample_titles.split("|") if _s(p)]
    out: list[str] = []
    for p in parts[:2]:
        base = p
        for sep in [" | ", " - ", " — "]:
            if sep in base:
                base = base.split(sep)[0]
        base = re.sub(r"\([^\)]*\)", " ", base)
        base = re.sub(r"\s+", " ", base).strip().lower()
        if not base:
            continue
        esc = re.escape(base).replace(r"\ ", r"\\s+")
        pat = rf"\b{esc}\b"
        if pat not in out:
            out.append(pat)
    return "|".join(out) if out else r"\bTODO_REVIEW_ME\b"


def _load_existing_rule_signatures() -> set[tuple[str, str, str]]:
    return {(pat, n, f) for pat, n, f, _ in TITLE_RULES}


def _render_candidate_module(path: Path, rows: list[dict[str, str]]) -> None:
    lines: list[str] = [
        "from __future__ import annotations",
        "",
        "# Auto-approved map_existing rules (safe gate).",
        "TITLE_RULES_CANDIDATES: list[tuple[str, str, str, str]] = [",
    ]
    for r in rows:
        lines.append(
            f"    ({r['regex']!r}, {r['normalized_title']!r}, {r['role_family']!r}, {r['occupation_group']!r}),"
        )
    lines.append("]")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _apply_to_title_rules(target: Path, rows: list[dict[str, str]], backup: bool = True) -> None:
    text = target.read_text(encoding="utf-8")
    marker = "\n]\n\n\ndef normalize_title"
    pos = text.find(marker)
    if pos < 0:
        raise RuntimeError("Could not find TITLE_RULES closing marker in title_normalization.py")

    insert_lines = []
    for r in rows:
        insert_lines.append(
            f"    ({r['regex']!r}, {r['normalized_title']!r}, {r['role_family']!r}, {r['occupation_group']!r}),"
        )

    if not insert_lines:
        return

    if backup:
        bak = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, bak)

    new_text = text[:pos] + "\n" + "\n".join(insert_lines) + text[pos:]
    target.write_text(new_text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Auto-approve safe map_existing candidates and optionally apply to TITLE_RULES.")
    ap.add_argument("--candidates-csv", default="docs/taxonomy_expansion_candidates_2k_v2.csv")
    ap.add_argument("--out-patch", default="docs/taxonomy_patch_map_existing_safe.py")
    ap.add_argument("--report-json", default="docs/taxonomy_map_existing_safe_report.json")
    ap.add_argument("--min-confidence", type=float, default=0.80)
    ap.add_argument("--min-count", type=int, default=5)
    ap.add_argument("--apply", action="store_true", help="Apply approved rules directly to title_normalization.py")
    ap.add_argument("--title-rules-file", default="automation/microsaas/title_normalization.py")
    args = ap.parse_args()

    path = Path(args.candidates_csv)
    if not path.exists():
        raise RuntimeError(f"Candidates CSV not found: {path}")

    rows = list(csv.DictReader(path.open("r", encoding="utf-8")))
    existing = _load_existing_rule_signatures()

    approved: list[dict[str, str]] = []
    rejected = 0

    for r in rows:
        if _s(r.get("proposed_action")).lower() != "map_existing":
            continue
        conf = float(_s(r.get("confidence_score")) or 0.0)
        cnt = int(float(_s(r.get("count")) or 0))
        n_title = _slug(_s(r.get("proposed_normalized_title")))
        n_family = _slug(_s(r.get("proposed_role_family")))

        if conf < args.min_confidence or cnt < args.min_count:
            rejected += 1
            continue
        if n_title not in ALLOWED_TITLES or n_title == "other":
            rejected += 1
            continue
        if n_family not in ALLOWED_FAMILIES or n_family == "other":
            rejected += 1
            continue

        regex = _regex_from_sample_titles(_s(r.get("sample_titles")))
        key = (regex, n_title, n_family)
        if key in existing:
            continue

        approved.append(
            {
                "cluster_key": _s(r.get("cluster_key")),
                "normalized_title": n_title,
                "role_family": n_family,
                "occupation_group": ROLE_FAMILY_TO_GROUP.get(n_family, "business"),
                "regex": regex,
                "count": str(cnt),
                "confidence_score": f"{conf:.4f}",
            }
        )

    _render_candidate_module(Path(args.out_patch), approved)

    if args.apply and approved:
        _apply_to_title_rules(Path(args.title_rules_file), approved, backup=True)

    report = {
        "input_csv": str(path),
        "approved_rules": len(approved),
        "rejected_rows": rejected,
        "min_confidence": args.min_confidence,
        "min_count": args.min_count,
        "applied": bool(args.apply),
        "out_patch": args.out_patch,
    }
    Path(args.report_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
