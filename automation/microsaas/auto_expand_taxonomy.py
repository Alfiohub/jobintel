from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from automation.microsaas.title_normalization import TITLE_RULES, normalize_title
except ModuleNotFoundError:
    from title_normalization import TITLE_RULES, normalize_title


STOP_WORDS = {
    "senior",
    "sr",
    "junior",
    "jr",
    "lead",
    "principal",
    "staff",
    "head",
    "director",
    "manager",
    "intern",
    "ii",
    "iii",
    "iv",
    "remote",
    "hybrid",
    "onsite",
    "site",
    "wfh",
    "contract",
    "freelance",
    "part",
    "time",
    "full",
    "usa",
    "us",
    "uk",
    "eu",
    "emea",
    "apac",
    "latam",
    "jan",
    "january",
    "feb",
    "february",
    "mar",
    "march",
    "apr",
    "april",
    "may",
    "jun",
    "june",
    "jul",
    "july",
    "aug",
    "august",
    "sep",
    "sept",
    "september",
    "oct",
    "october",
    "nov",
    "november",
    "dec",
    "december",
}

TOKEN_RE = re.compile(r"[^a-z0-9]+")

ALLOWED_NORMALIZED_TITLE = {n for _, n, _, _ in TITLE_RULES} | {"other"}
ALLOWED_ROLE_FAMILY = {f for _, _, f, _ in TITLE_RULES} | {"other"}
ROLE_FAMILY_TO_GROUP: dict[str, str] = {}
for _, _, fam, group in TITLE_RULES:
    ROLE_FAMILY_TO_GROUP.setdefault(fam, group)


@dataclass
class ClusterDecision:
    cluster_key: str
    sample_titles: str
    count: int
    proposed_action: str
    proposed_normalized_title: str
    proposed_role_family: str
    confidence_score: float
    rationale: str


def _s(v: Any) -> str:
    return str(v or "").strip()


def _tokenize_label(v: str) -> str:
    s = _s(v).lower()
    if not s:
        return ""
    s = s.replace("&", " and ")
    s = TOKEN_RE.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _is_closed_title(v: str) -> bool:
    t = _tokenize_label(v)
    return bool(t) and t in ALLOWED_NORMALIZED_TITLE and t != "other"


def _is_closed_family(v: str) -> bool:
    t = _tokenize_label(v)
    return bool(t) and t in ALLOWED_ROLE_FAMILY and t != "other"


def _safe_int(v: Any, default: int = 1) -> int:
    try:
        i = int(float(v))
        return i if i > 0 else default
    except Exception:
        return default


def _canonical_title_signature(title: str) -> str:
    raw = _s(title).lower()
    raw = re.sub(r"\([^\)]*\)", " ", raw)
    # Remove common trailing location/noise chunks after separators.
    raw = re.sub(r"\s+[|\-]\s+.*$", " ", raw)
    raw = re.sub(r"\b(all levels?|multiple openings?)\b", " ", raw)
    toks = [t for t in TOKEN_RE.split(raw) if t and t not in STOP_WORDS and not t.isdigit()]
    if not toks:
        return "unknown"
    return "_".join(toks[:4])


def _title_to_regex_fragment(title: str) -> str:
    t = _s(title).lower()
    t = re.sub(r"\([^\)]*\)", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return ""
    esc = re.escape(t)
    esc = esc.replace(r"\ ", r"\\s+")
    return rf"\b{esc}\b"


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    rows = list(csv.DictReader(path.open("r", encoding="utf-8")))
    return [dict(r) for r in rows]


def _read_sqlite_rows(db_path: Path, table: str, where: str) -> list[dict[str, str]]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        query = f"SELECT * FROM {table}"
        if where.strip():
            query += f" WHERE {where}"
        cur = con.execute(query)
        out: list[dict[str, str]] = []
        for row in cur.fetchall():
            d = {k: _s(row[k]) for k in row.keys()}
            out.append(d)
        return out
    finally:
        con.close()


def _pick_title_for_row(row: dict[str, str]) -> str:
    for key in ("title_clean", "title_raw", "onet_title"):
        v = _s(row.get(key))
        if v:
            return v
    return ""


def _infer_role_family_from_text(title: str) -> str:
    t = _s(title).lower()
    # Try existing rules first.
    n_title, n_family, _ = normalize_title(title)
    if _is_closed_family(n_family):
        return _tokenize_label(n_family)

    # Lightweight fallback for new labels.
    rules: list[tuple[str, str]] = [
        (r"\bproduct owner\b|\bproduct\b", "product_management"),
        (r"\bqa\b|\bquality assurance\b|\btester\b", "software_engineering"),
        (r"\bsecurity\b", "it_operations"),
        (r"\bsupport\b|\bhelp desk\b", "it_operations"),
        (r"\bdata\b|\banalytics?\b|\bbi\b", "data_analytics"),
        (r"\bengineer\b|\bdeveloper\b", "software_engineering"),
        (r"\brecruit\w+\b|\btalent\b", "recruiting"),
        (r"\bmarketing\b|\bseo\b|\bcontent\b", "marketing"),
        (r"\bsales\b|\baccount\b", "sales"),
    ]
    for pat, fam in rules:
        if re.search(pat, t):
            return fam
    return "other"


def _is_other_row(row: dict[str, str]) -> bool:
    for key in ("normalized_title", "pred_normalized_title", "gold_normalized_title"):
        v = _tokenize_label(row.get(key, ""))
        if v == "other":
            return True
    # If missing all normalized title fields, treat as candidate row.
    has_any = any(_s(row.get(k)) for k in ("normalized_title", "pred_normalized_title", "gold_normalized_title"))
    return not has_any


def _evidence_for_row(row: dict[str, str]) -> dict[str, list[str]]:
    title_votes: list[str] = []
    family_votes: list[str] = []
    ext_title_votes: list[str] = []

    pred_title = _tokenize_label(row.get("pred_normalized_title"))
    pred_family = _tokenize_label(row.get("pred_role_family"))
    sug_title = _tokenize_label(row.get("suggested_normalized_title"))
    sug_family = _tokenize_label(row.get("suggested_role_family"))

    if _is_closed_title(pred_title):
        title_votes.append(pred_title)
    elif pred_title and pred_title != "other":
        ext_title_votes.append(pred_title)

    if _is_closed_family(pred_family):
        family_votes.append(pred_family)

    if _is_closed_title(sug_title):
        title_votes.append(sug_title)
    elif sug_title and sug_title != "other":
        ext_title_votes.append(sug_title)

    if _is_closed_family(sug_family):
        family_votes.append(sug_family)

    onet_title = _s(row.get("onet_title"))
    if onet_title:
        n_title, n_family, _ = normalize_title(onet_title)
        n_title = _tokenize_label(n_title)
        n_family = _tokenize_label(n_family)
        if _is_closed_title(n_title):
            title_votes.append(n_title)
        elif n_title and n_title != "other":
            ext_title_votes.append(n_title)
        if _is_closed_family(n_family):
            family_votes.append(n_family)

        # also keep a tokenized free-text onet title as extension hint
        ext_onet = _tokenize_label(onet_title)
        if ext_onet and ext_onet not in ALLOWED_NORMALIZED_TITLE and ext_onet != "other":
            ext_title_votes.append(ext_onet)

    title_clean = _s(row.get("title_clean"))
    if title_clean:
        t_title, t_family, _ = normalize_title(title_clean)
        t_title = _tokenize_label(t_title)
        t_family = _tokenize_label(t_family)
        if _is_closed_title(t_title):
            title_votes.append(t_title)
        if _is_closed_family(t_family):
            family_votes.append(t_family)

    return {
        "title_votes": title_votes,
        "family_votes": family_votes,
        "ext_title_votes": ext_title_votes,
    }


def _top_vote(counter: Counter[str]) -> tuple[str, int, float]:
    if not counter:
        return "", 0, 0.0
    label, count = counter.most_common(1)[0]
    total = sum(counter.values())
    return label, count, (count / total if total > 0 else 0.0)


def _cluster_key(row: dict[str, str], ev: dict[str, list[str]]) -> str:
    if ev["title_votes"]:
        return f"title::{Counter(ev['title_votes']).most_common(1)[0][0]}"
    if ev["ext_title_votes"]:
        return f"ext::{Counter(ev['ext_title_votes']).most_common(1)[0][0]}"
    sig = _canonical_title_signature(_pick_title_for_row(row))
    return f"sig::{sig}"


def _build_clusters(rows: list[dict[str, str]]) -> tuple[dict[str, list[dict[str, str]]], dict[int, dict[str, list[str]]]]:
    clusters: dict[str, list[dict[str, str]]] = defaultdict(list)
    evidence_by_idx: dict[int, dict[str, list[str]]] = {}
    for idx, row in enumerate(rows):
        ev = _evidence_for_row(row)
        evidence_by_idx[idx] = ev
        ck = _cluster_key(row, ev)
        row["__idx"] = str(idx)
        clusters[ck].append(row)
    return clusters, evidence_by_idx


def _sample_titles(rows: list[dict[str, str]], max_samples: int = 3) -> str:
    seen: list[str] = []
    for r in rows:
        t = _pick_title_for_row(r)
        if t and t not in seen:
            seen.append(t)
        if len(seen) >= max_samples:
            break
    return " | ".join(seen)


def _decide_cluster(
    cluster_key: str,
    rows: list[dict[str, str]],
    evidence_by_idx: dict[int, dict[str, list[str]]],
    *,
    min_cluster_size: int,
    min_confidence: float,
    allow_extend: bool,
) -> ClusterDecision:
    weight_count = 0
    title_counter: Counter[str] = Counter()
    family_counter: Counter[str] = Counter()
    ext_counter: Counter[str] = Counter()
    pred_counter: Counter[str] = Counter()

    for r in rows:
        w = _safe_int(r.get("frequency") or r.get("count") or 1, 1)
        weight_count += w
        idx = int(r["__idx"])
        ev = evidence_by_idx[idx]
        for t in ev["title_votes"]:
            title_counter[t] += w
        for f in ev["family_votes"]:
            family_counter[f] += w
        for t in ev["ext_title_votes"]:
            ext_counter[t] += w
        p = _tokenize_label(r.get("pred_normalized_title"))
        if _is_closed_title(p):
            pred_counter[p] += w

    top_title, _, title_share = _top_vote(title_counter)
    top_family, _, family_share = _top_vote(family_counter)
    top_pred, _, pred_share = _top_vote(pred_counter)
    top_ext, _, ext_share = _top_vote(ext_counter)
    # Signature fallback for highly fragmented sources (e.g. title variants with location/date suffixes).
    sig = cluster_key.split("::", 1)[1] if "::" in cluster_key else cluster_key

    # 1) map_existing: closed-set pred title appears often with good agreement
    if top_pred and weight_count >= min_cluster_size and pred_share >= min_confidence:
        fam = top_family
        if not fam:
            # fallback family from normalize_title on top sample
            t0 = _pick_title_for_row(rows[0]) if rows else ""
            _, fam2, _ = normalize_title(t0)
            fam = _tokenize_label(fam2)
        if not _is_closed_family(fam):
            fam = "other"
        conf = min(1.0, (pred_share * 0.7) + (family_share * 0.2) + (min(weight_count, 50) / 50.0 * 0.1))
        return ClusterDecision(
            cluster_key=cluster_key,
            sample_titles=_sample_titles(rows),
            count=weight_count,
            proposed_action="map_existing",
            proposed_normalized_title=top_pred,
            proposed_role_family=fam,
            confidence_score=round(conf, 4),
            rationale=(
                f"pred_normalized_title converges on '{top_pred}' with share={pred_share:.2f}; "
                f"cluster_size={weight_count}"
            ),
        )

    # 1b) map_existing from normalized title rules if cluster titles converge to a closed-set label.
    if top_title and _is_closed_title(top_title) and weight_count >= min_cluster_size and title_share >= min_confidence:
        fam = top_family
        if not _is_closed_family(fam):
            fam = _infer_role_family_from_text(_pick_title_for_row(rows[0]) if rows else "")
        if not _is_closed_family(fam):
            fam = "other"
        conf = min(1.0, (title_share * 0.8) + (family_share * 0.1) + (min(weight_count, 50) / 50.0 * 0.1))
        return ClusterDecision(
            cluster_key=cluster_key,
            sample_titles=_sample_titles(rows),
            count=weight_count,
            proposed_action="map_existing",
            proposed_normalized_title=top_title,
            proposed_role_family=fam,
            confidence_score=round(conf, 4),
            rationale=(
                f"rule-normalized title converges on '{top_title}' with share={title_share:.2f}; "
                f"cluster_size={weight_count}"
            ),
        )

    # 2) extend_taxonomy: out-of-set candidate converges + enough size + confidence
    if allow_extend and top_ext and weight_count >= min_cluster_size and ext_share >= min_confidence:
        fam = top_family
        if not _is_closed_family(fam):
            pred_fam = _tokenize_label(rows[0].get("pred_role_family")) if rows else ""
            fam = pred_fam if _is_closed_family(pred_fam) else "other"
        conf = min(1.0, (ext_share * 0.75) + (family_share * 0.15) + (min(weight_count, 80) / 80.0 * 0.10))
        if conf >= min_confidence:
            return ClusterDecision(
                cluster_key=cluster_key,
                sample_titles=_sample_titles(rows),
                count=weight_count,
                proposed_action="extend_taxonomy",
                proposed_normalized_title=top_ext,
                proposed_role_family=fam,
                confidence_score=round(conf, 4),
                rationale=(
                    f"suggested/onet/title cluster converges on new label '{top_ext}' with share={ext_share:.2f}; "
                    f"cluster_size={weight_count}"
                ),
            )

    # 2b) extend from signature when no strong closed-set signal exists but cluster is repeated.
    if allow_extend and sig and sig != "unknown" and weight_count >= min_cluster_size:
        # Confidence increases with size; penalize if signature is too generic.
        generic = {"manager", "engineer", "analyst", "specialist", "consultant"}
        sig_tokens = [t for t in sig.split("_") if t]
        is_generic = len(sig_tokens) <= 1 or all(t in generic for t in sig_tokens)
        base = 0.55 + min(0.30, (weight_count - min_cluster_size) * 0.03)
        conf = max(0.0, base - (0.12 if is_generic else 0.0))
        if conf >= min_confidence:
            fam = top_family if _is_closed_family(top_family) else _infer_role_family_from_text(_pick_title_for_row(rows[0]) if rows else "")
            if not _is_closed_family(fam):
                fam = "other"
            return ClusterDecision(
                cluster_key=cluster_key,
                sample_titles=_sample_titles(rows),
                count=weight_count,
                proposed_action="extend_taxonomy",
                proposed_normalized_title=sig,
                proposed_role_family=fam,
                confidence_score=round(conf, 4),
                rationale=(
                    f"signature-based extension '{sig}' from repeated cluster; "
                    f"cluster_size={weight_count}; generic={int(is_generic)}"
                ),
            )

    # 3) keep_other: rare/ambiguous/noisy
    amb = max(title_share, ext_share, pred_share)
    reason = "rare_or_ambiguous"
    if weight_count < min_cluster_size:
        reason = "cluster_too_small"
    elif amb < min_confidence:
        reason = "low_agreement"

    return ClusterDecision(
        cluster_key=cluster_key,
        sample_titles=_sample_titles(rows),
        count=weight_count,
        proposed_action="keep_other",
        proposed_normalized_title="other",
        proposed_role_family="other",
        confidence_score=round(amb, 4),
        rationale=f"{reason}; best_agreement={amb:.2f}; cluster_size={weight_count}",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def _patch_regex_from_cluster_titles(sample_titles: str) -> str:
    parts = [_s(p) for p in sample_titles.split("|") if _s(p)]
    frags: list[str] = []
    for p in parts[:3]:
        fg = _title_to_regex_fragment(p)
        if fg and fg not in frags:
            frags.append(fg)
    return "|".join(frags) if frags else r"\bTODO_REVIEW_ME\b"


def _write_patch_py(path: Path, decisions: list[ClusterDecision], max_suggestions: int) -> None:
    candidates = [d for d in decisions if d.proposed_action == "extend_taxonomy"]
    candidates = sorted(candidates, key=lambda d: (-d.confidence_score, -d.count, d.cluster_key))[: max(1, max_suggestions)]

    lines: list[str] = []
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("# Auto-generated candidate TITLE_RULES patches.")
    lines.append("# Review manually before merging into title_normalization.py")
    lines.append("TITLE_RULES_CANDIDATES: list[tuple[str, str, str, str]] = [")
    for d in candidates:
        og = ROLE_FAMILY_TO_GROUP.get(d.proposed_role_family, "business")
        regex = _patch_regex_from_cluster_titles(d.sample_titles)
        lines.append(
            f"    ({regex!r}, {d.proposed_normalized_title!r}, {d.proposed_role_family!r}, {og!r}),  # {d.cluster_key} conf={d.confidence_score:.2f} n={d.count}"
        )
    lines.append("]")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary_md(path: Path, decisions: list[ClusterDecision], total_rows: int, total_clusters: int) -> None:
    c = Counter(d.proposed_action for d in decisions)
    top_extend = sorted(
        [d for d in decisions if d.proposed_action == "extend_taxonomy"],
        key=lambda x: (-x.confidence_score, -x.count),
    )[:10]
    top_map = sorted(
        [d for d in decisions if d.proposed_action == "map_existing"],
        key=lambda x: (-x.confidence_score, -x.count),
    )[:10]

    lines = [
        "# Taxonomy Expansion Summary",
        "",
        f"- rows_processed: {total_rows}",
        f"- clusters: {total_clusters}",
        f"- map_existing: {c.get('map_existing', 0)}",
        f"- extend_taxonomy: {c.get('extend_taxonomy', 0)}",
        f"- keep_other: {c.get('keep_other', 0)}",
        "",
        "## Top map_existing",
    ]
    for d in top_map:
        lines.append(
            f"- `{d.cluster_key}` -> `{d.proposed_normalized_title}` / `{d.proposed_role_family}` (n={d.count}, conf={d.confidence_score:.2f})"
        )

    lines.append("")
    lines.append("## Top extend_taxonomy")
    for d in top_extend:
        lines.append(
            f"- `{d.cluster_key}` -> `{d.proposed_normalized_title}` / `{d.proposed_role_family}` (n={d.count}, conf={d.confidence_score:.2f})"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _iter_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.input_csv:
        p = Path(args.input_csv)
        if not p.exists():
            raise RuntimeError(f"input csv not found: {p}")
        return _read_csv_rows(p)
    if args.db:
        p = Path(args.db)
        if not p.exists():
            raise RuntimeError(f"db not found: {p}")
        return _read_sqlite_rows(p, args.table, args.where)
    raise RuntimeError("Provide either --input-csv or --db")


def main() -> None:
    ap = argparse.ArgumentParser(description="Auto-propose taxonomy handling for 'other' titles.")
    ap.add_argument("--input-csv", default="", help="Input CSV (optional, alternative to --db)")
    ap.add_argument("--db", default="", help="Input SQLite DB (optional, alternative to --input-csv)")
    ap.add_argument("--table", default="jobs_indexed", help="DB table name when using --db")
    ap.add_argument(
        "--where",
        default="",
        help="Optional SQL WHERE clause when using --db (e.g. normalized_title='other')",
    )
    ap.add_argument("--only-other", action="store_true", help="Process only rows considered 'other'")
    ap.add_argument("--min-cluster-size", type=int, default=5)
    ap.add_argument("--min-confidence", type=float, default=0.7)
    ap.add_argument("--allow-extend", action="store_true")
    ap.add_argument("--max-suggestions", type=int, default=25)
    ap.add_argument("--out-expansion-csv", default="docs/taxonomy_expansion_candidates.csv")
    ap.add_argument("--out-map-csv", default="docs/taxonomy_map_existing_candidates.csv")
    ap.add_argument("--out-patch-py", default="docs/taxonomy_patch_candidates.py")
    ap.add_argument("--out-summary-md", default="docs/taxonomy_expansion_summary.md")
    args = ap.parse_args()

    rows = _iter_rows(args)
    if not rows:
        raise RuntimeError("No rows loaded")

    if args.only_other:
        rows = [r for r in rows if _is_other_row(r)]
        if not rows:
            raise RuntimeError("No 'other' rows found after filtering")

    clusters, evidence_by_idx = _build_clusters(rows)

    decisions: list[ClusterDecision] = []
    for ck, crows in clusters.items():
        decisions.append(
            _decide_cluster(
                ck,
                crows,
                evidence_by_idx,
                min_cluster_size=max(1, args.min_cluster_size),
                min_confidence=min(1.0, max(0.0, args.min_confidence)),
                allow_extend=bool(args.allow_extend),
            )
        )

    decisions_sorted = sorted(decisions, key=lambda d: (-d.count, -d.confidence_score, d.cluster_key))

    expansion_rows = [
        {
            "cluster_key": d.cluster_key,
            "sample_titles": d.sample_titles,
            "count": d.count,
            "proposed_action": d.proposed_action,
            "proposed_normalized_title": d.proposed_normalized_title,
            "proposed_role_family": d.proposed_role_family,
            "confidence_score": f"{d.confidence_score:.4f}",
            "rationale": d.rationale,
        }
        for d in decisions_sorted
    ]

    map_rows = [r for r in expansion_rows if r["proposed_action"] == "map_existing"]

    _write_csv(
        Path(args.out_expansion_csv),
        expansion_rows,
        [
            "cluster_key",
            "sample_titles",
            "count",
            "proposed_action",
            "proposed_normalized_title",
            "proposed_role_family",
            "confidence_score",
            "rationale",
        ],
    )

    _write_csv(
        Path(args.out_map_csv),
        map_rows,
        [
            "cluster_key",
            "sample_titles",
            "count",
            "proposed_action",
            "proposed_normalized_title",
            "proposed_role_family",
            "confidence_score",
            "rationale",
        ],
    )

    _write_patch_py(Path(args.out_patch_py), decisions_sorted, args.max_suggestions)
    _write_summary_md(Path(args.out_summary_md), decisions_sorted, len(rows), len(clusters))

    summary = {
        "rows_processed": len(rows),
        "clusters": len(clusters),
        "actions": dict(Counter(d.proposed_action for d in decisions_sorted)),
        "outputs": {
            "expansion_csv": args.out_expansion_csv,
            "map_existing_csv": args.out_map_csv,
            "patch_py": args.out_patch_py,
            "summary_md": args.out_summary_md,
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
