from __future__ import annotations

import argparse
import difflib
import json
import re
import sqlite3
from dataclasses import dataclass
from typing import Any


_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^a-z0-9\s]")
_LEVEL_TOKEN_RE = re.compile(
    r"\b(senior|sr|junior|jr|lead|principal|staff|head|vp|vice president|director|manager)\b"
)
_MIN_TOKEN_OVERLAP = 0.25


@dataclass
class _Candidate:
    onet_soc_code: str
    onet_title: str
    candidate: str
    source: str
    candidate_norm: str
    candidate_norm_no_level: str
    token_set: set[str]


@dataclass
class _CandidateCache:
    candidates: list[_Candidate]
    by_norm_no_level: dict[str, _Candidate]


_CONN_CACHE: dict[int, _CandidateCache] = {}


def _s(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: str) -> str:
    s = _s(value).lower()
    if not s:
        return ""
    s = _PUNCT_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def _normalize_light(value: str) -> str:
    return _s(value).lower()


def _normalize_for_match(value: str) -> str:
    s = _normalize_text(value)
    if not s:
        return ""
    s = _LEVEL_TOKEN_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def _token_set(value: str) -> set[str]:
    s = _normalize_for_match(value)
    if not s:
        return set()
    return {tok for tok in s.split(" ") if tok}


def _safe_fetchall(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[sqlite3.Row]:
    try:
        cur = conn.execute(sql, params)
        return cur.fetchall()
    except sqlite3.OperationalError:
        return []


def _result(
    onet_soc_code: str | None,
    onet_title: str | None,
    onet_match_type: str,
    onet_match_score: float,
    onet_source_table: str | None,
    onet_matched_candidate: str | None = None,
) -> dict[str, Any]:
    return {
        "onet_soc_code": onet_soc_code,
        "onet_title": onet_title,
        "onet_match_type": onet_match_type,
        "onet_match_score": round(float(onet_match_score), 4),
        "onet_source_table": onet_source_table,
        "onet_matched_candidate": onet_matched_candidate,
    }


def _try_exact(conn: sqlite3.Connection, query: str, *, source_weight: float) -> dict[str, Any] | None:
    q = _normalize_light(query)
    if not q:
        return None

    checks = [
        (
            "occupation_data",
            "SELECT onetsoc_code, title, title FROM occupation_data WHERE lower(trim(title))=? LIMIT 1",
            (q,),
            1.00,
        ),
        (
            "alternate_titles",
            "SELECT a.onetsoc_code, o.title, a.alternate_title FROM alternate_titles a "
            "LEFT JOIN occupation_data o ON o.onetsoc_code=a.onetsoc_code "
            "WHERE lower(trim(a.alternate_title))=? LIMIT 1",
            (q,),
            0.99,
        ),
        (
            "sample_of_reported_titles",
            "SELECT s.onetsoc_code, o.title, s.reported_job_title FROM sample_of_reported_titles s "
            "LEFT JOIN occupation_data o ON o.onetsoc_code=s.onetsoc_code "
            "WHERE lower(trim(s.reported_job_title))=? LIMIT 1",
            (q,),
            0.98,
        ),
    ]

    for source, sql, params, score in checks:
        rows = _safe_fetchall(conn, sql, params)
        if rows:
            soc, title, matched_candidate = rows[0][0], rows[0][1], rows[0][2]
            return _result(
                soc,
                title,
                "exact",
                min(score, source_weight),
                source,
                _s(matched_candidate),
            )
    return None


def _try_manual_crosswalk(conn: sqlite3.Connection, normalized_title: str) -> dict[str, Any] | None:
    nt = _normalize_light(normalized_title)
    if not nt:
        return None
    rows = _safe_fetchall(
        conn,
        "SELECT onet_soc_code, onet_title, mapping_confidence "
        "FROM title_onet_crosswalk WHERE lower(trim(normalized_title))=? LIMIT 1",
        (nt,),
    )
    if not rows:
        return None
    soc, title, conf = rows[0][0], rows[0][1], rows[0][2]
    score = float(conf) if conf is not None else 1.0
    return _result(
        _s(soc) or None,
        _s(title) or None,
        "manual_crosswalk",
        max(0.0, min(1.0, score)),
        "title_onet_crosswalk",
        _s(normalized_title),
    )


def _iter_titles(conn: sqlite3.Connection) -> list[tuple[str, str, str, str]]:
    out: list[tuple[str, str, str, str]] = []

    occ_rows = _safe_fetchall(conn, "SELECT onetsoc_code, title FROM occupation_data", ())
    for soc, label in occ_rows:
        out.append((_s(soc), _s(label), _s(label), "occupation_data"))

    alt_rows = _safe_fetchall(
        conn,
        "SELECT a.onetsoc_code, COALESCE(o.title,''), a.alternate_title "
        "FROM alternate_titles a "
        "LEFT JOIN occupation_data o ON o.onetsoc_code=a.onetsoc_code",
        (),
    )
    for soc, occ_title, alt in alt_rows:
        out.append((_s(soc), _s(occ_title), _s(alt), "alternate_titles"))

    rep_rows = _safe_fetchall(
        conn,
        "SELECT s.onetsoc_code, COALESCE(o.title,''), s.reported_job_title "
        "FROM sample_of_reported_titles s "
        "LEFT JOIN occupation_data o ON o.onetsoc_code=s.onetsoc_code",
        (),
    )
    for soc, occ_title, rep in rep_rows:
        out.append((_s(soc), _s(occ_title), _s(rep), "sample_of_reported_titles"))

    return out


def _build_candidate_cache(conn: sqlite3.Connection) -> _CandidateCache:
    candidates: list[_Candidate] = []
    by_norm_no_level: dict[str, _Candidate] = {}
    rows = _iter_titles(conn)
    for soc, onet_title, cand, source in rows:
        candidate_norm = _normalize_text(cand)
        candidate_norm_no_level = _normalize_for_match(cand)
        entry = _Candidate(
            onet_soc_code=soc,
            onet_title=onet_title,
            candidate=cand,
            source=source,
            candidate_norm=candidate_norm,
            candidate_norm_no_level=candidate_norm_no_level,
            token_set=_token_set(cand),
        )
        candidates.append(entry)

        if candidate_norm_no_level and candidate_norm_no_level not in by_norm_no_level:
            by_norm_no_level[candidate_norm_no_level] = entry
        elif candidate_norm_no_level:
            cur = by_norm_no_level[candidate_norm_no_level]
            if _source_score(entry.source) > _source_score(cur.source):
                by_norm_no_level[candidate_norm_no_level] = entry

    return _CandidateCache(candidates=candidates, by_norm_no_level=by_norm_no_level)


def _get_candidate_cache(conn: sqlite3.Connection) -> _CandidateCache:
    key = id(conn)
    cached = _CONN_CACHE.get(key)
    if cached is not None:
        return cached
    fresh = _build_candidate_cache(conn)
    _CONN_CACHE[key] = fresh
    return fresh


def _source_score(source: str) -> float:
    if source == "occupation_data":
        return 1.0
    if source == "alternate_titles":
        return 0.98
    return 0.96


def _try_normalized_exact(
    cache: _CandidateCache, query: str, *, source_weight: float
) -> dict[str, Any] | None:
    qn = _normalize_for_match(query)
    if not qn:
        return None

    row = cache.by_norm_no_level.get(qn)
    if row is not None:
        score = min(0.95 * _source_score(row.source), source_weight)
        return _result(
            row.onet_soc_code,
            row.onet_title or row.candidate,
            "normalized_exact",
            score,
            row.source,
            row.candidate,
        )
    return None


def _token_overlap_ratio(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / float(max(len(a), len(b)))


def _try_fuzzy(cache: _CandidateCache, query: str, *, source_weight: float) -> dict[str, Any] | None:
    qn = _normalize_for_match(query)
    if not qn:
        return None

    qtokens = _token_set(query)
    best: dict[str, Any] | None = None
    best_score = 0.0

    for row in cache.candidates:
        cand = row.candidate_norm_no_level
        if not cand:
            continue
        ratio = difflib.SequenceMatcher(None, qn, cand).ratio()
        if ratio < 0.74:
            continue
        overlap = _token_overlap_ratio(qtokens, row.token_set)
        if overlap < _MIN_TOKEN_OVERLAP:
            continue

        blended = (ratio * 0.8) + (overlap * 0.2)
        score = blended * 0.9 * _source_score(row.source)
        score = min(score, source_weight)
        if score > best_score:
            best_score = score
            best = _result(
                row.onet_soc_code,
                row.onet_title or row.candidate,
                "fuzzy",
                score,
                row.source,
                row.candidate,
            )

    return best


def map_onet_title(
    conn: sqlite3.Connection,
    title_clean: str,
    normalized_title: str | None = None,
) -> dict[str, Any]:
    title_q = _s(title_clean)
    norm_q = _s(normalized_title)

    if not title_q and not norm_q:
        return _result(None, None, "no_match", 0.0, None)

    if norm_q:
        manual = _try_manual_crosswalk(conn, norm_q)
        if manual:
            return manual

    query_candidates: list[tuple[str, float]] = []
    if title_q:
        query_candidates.append((title_q, 1.0))
    if norm_q and _normalize_text(norm_q) != _normalize_text(title_q):
        query_candidates.append((norm_q, 0.92))

    for query, weight in query_candidates:
        r = _try_exact(conn, query, source_weight=weight)
        if r:
            return r

    cache = _get_candidate_cache(conn)

    for query, weight in query_candidates:
        r = _try_normalized_exact(cache, query, source_weight=weight)
        if r:
            return r

    best_fuzzy: dict[str, Any] | None = None
    for query, weight in query_candidates:
        r = _try_fuzzy(cache, query, source_weight=weight)
        if r and (best_fuzzy is None or r["onet_match_score"] > best_fuzzy["onet_match_score"]):
            best_fuzzy = r

    if best_fuzzy:
        return best_fuzzy

    return _result(None, None, "no_match", 0.0, None)


def main() -> None:
    ap = argparse.ArgumentParser(description="Map a title to O*NET SOC using local SQLite tables.")
    ap.add_argument("--db", required=True, help="Path to SQLite DB")
    ap.add_argument("--title", required=True, help="Clean title to map")
    ap.add_argument("--normalized-title", default="", help="Optional normalized title fallback")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        result = map_onet_title(conn, title_clean=args.title, normalized_title=args.normalized_title or None)
    finally:
        conn.close()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
