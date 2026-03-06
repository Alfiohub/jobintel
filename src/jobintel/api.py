from __future__ import annotations

from datetime import datetime
from typing import Any
import sqlite3
import json
from datetime import timedelta
import hashlib
import math
import os
import re
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


app = FastAPI(title="jobintel")
_UI_DIR = Path(__file__).resolve().parent / "ui"
if _UI_DIR.exists():
    app.mount("/ui-assets", StaticFiles(directory=_UI_DIR), name="ui-assets")


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def _ensure_columns(con: sqlite3.Connection) -> None:
    existing = {row[1] for row in con.execute("PRAGMA table_info(seen_jobs)")}
    cols = {
        "location": "TEXT",
        "remote": "INTEGER",
        "published_at": "TEXT",
    }
    for name, typ in cols.items():
        if name not in existing:
            con.execute(f"ALTER TABLE seen_jobs ADD COLUMN {name} {typ}")


def _ensure_enriched_table(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS jobs_enriched (
          fingerprint   TEXT PRIMARY KEY,
          role_family   TEXT,
          seniority     TEXT,
          location_type TEXT,
          country       TEXT,
          skills_json   TEXT NOT NULL,
          normalized_title TEXT NOT NULL,
          updated_at    TEXT NOT NULL
        );
        """
    )


def _ensure_saved_filters_table(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS saved_filters (
          id           INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id      TEXT NOT NULL,
          name         TEXT NOT NULL,
          criteria_json TEXT NOT NULL,
          is_active    INTEGER NOT NULL DEFAULT 1,
          created_at   TEXT NOT NULL,
          updated_at   TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_saved_filters_user_id ON saved_filters(user_id);
        """
    )


def _ensure_filter_matches_table(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS filter_matches (
          id          INTEGER PRIMARY KEY AUTOINCREMENT,
          filter_id   INTEGER NOT NULL,
          fingerprint TEXT NOT NULL,
          score       INTEGER NOT NULL,
          reasons_json TEXT NOT NULL,
          matched_at  TEXT NOT NULL,
          last_seen   TEXT NOT NULL,
          is_new      INTEGER NOT NULL DEFAULT 1,
          notified    INTEGER NOT NULL DEFAULT 0,
          UNIQUE(filter_id, fingerprint)
        );
        CREATE INDEX IF NOT EXISTS idx_filter_matches_filter_new ON filter_matches(filter_id, is_new, matched_at);
        """
    )


def _ensure_job_actions_table(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS job_actions (
          id           INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id      TEXT NOT NULL,
          fingerprint  TEXT NOT NULL,
          action       TEXT NOT NULL,
          filter_id    INTEGER,
          metadata_json TEXT NOT NULL,
          created_at   TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_job_actions_user_fp ON job_actions(user_id, fingerprint, created_at);
        CREATE INDEX IF NOT EXISTS idx_job_actions_action ON job_actions(action, created_at);
        """
    )


def _ensure_notification_attempts_table(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS notification_attempts (
          id            INTEGER PRIMARY KEY AUTOINCREMENT,
          filter_id     INTEGER NOT NULL,
          webhook_url   TEXT NOT NULL,
          status        TEXT NOT NULL,
          http_status   INTEGER,
          sent_count    INTEGER NOT NULL DEFAULT 0,
          error         TEXT,
          created_at    TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_notification_attempts_created_at ON notification_attempts(created_at);
        CREATE INDEX IF NOT EXISTS idx_notification_attempts_filter_id ON notification_attempts(filter_id, created_at);
        """
    )


def _ensure_notification_targets_table(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS notification_targets (
          id            INTEGER PRIMARY KEY AUTOINCREMENT,
          filter_id     INTEGER NOT NULL,
          webhook_url   TEXT NOT NULL,
          is_active     INTEGER NOT NULL DEFAULT 1,
          created_at    TEXT NOT NULL,
          updated_at    TEXT NOT NULL,
          UNIQUE(filter_id, webhook_url)
        );
        CREATE INDEX IF NOT EXISTS idx_notification_targets_filter_id ON notification_targets(filter_id, is_active);
        """
    )


def _ensure_microsaas_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS jobs_indexed (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          clean_job_id INTEGER NOT NULL,
          source TEXT NOT NULL,
          source_job_id TEXT,
          source_org TEXT,
          url TEXT NOT NULL,
          company_name TEXT NOT NULL,
          title_raw TEXT NOT NULL,
          title_clean TEXT NOT NULL,
          normalized_title TEXT,
          role_family TEXT,
          occupation_group TEXT,
          seniority TEXT,
          employment_type TEXT,
          location_type TEXT,
          city TEXT,
          region TEXT,
          country TEXT,
          salary_min INTEGER,
          salary_max INTEGER,
          salary_currency TEXT,
          skills_json TEXT NOT NULL DEFAULT '[]',
          tags_json TEXT NOT NULL DEFAULT '{}',
          embedding_json TEXT,
          embedding_model TEXT,
          tagger_version TEXT,
          tag_confidence REAL,
          indexed_at TEXT NOT NULL
        );
        """
    )


def _to_float_list(value: str | None) -> list[float]:
    if not value:
        return []
    try:
        obj = json.loads(value)
    except Exception:
        return []
    if not isinstance(obj, list):
        return []
    out: list[float] = []
    for x in obj:
        try:
            out.append(float(x))
        except Exception:
            continue
    return out


def _hash_embedding(text: str, dim: int) -> list[float]:
    if dim <= 0:
        return []
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    out: list[float] = []
    for i in range(dim):
        b = digest[i % len(digest)]
        out.append((float(b) / 127.5) - 1.0)
    return out


def _embed_openai(text: str, model: str, timeout_sec: int) -> list[float]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for semantic_provider=openai")
    payload = {"model": model, "input": text}
    req = urlrequest.Request(
        "https://api.openai.com/v1/embeddings",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout_sec) as resp:
        body = resp.read().decode("utf-8")
    obj = json.loads(body)
    data = obj.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("OpenAI embeddings: invalid response data")
    emb = data[0].get("embedding")
    if not isinstance(emb, list):
        raise RuntimeError("OpenAI embeddings: missing embedding vector")
    return [float(x) for x in emb]


def _embed_gemini(text: str, model: str, timeout_sec: int) -> list[float]:
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is required for semantic_provider=gemini")
    payload = {"content": {"parts": [{"text": text}]}}
    req = urlrequest.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={api_key}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout_sec) as resp:
        body = resp.read().decode("utf-8")
    obj = json.loads(body)
    emb_obj = obj.get("embedding")
    if not isinstance(emb_obj, dict):
        raise RuntimeError("Gemini embeddings: invalid response embedding")
    values = emb_obj.get("values")
    if not isinstance(values, list):
        raise RuntimeError("Gemini embeddings: missing values vector")
    return [float(x) for x in values]


def _compute_query_embedding(
    query: str,
    *,
    semantic_provider: str,
    semantic_model: str | None,
    timeout_sec: int,
    hash_dim: int,
) -> tuple[list[float], str]:
    provider = semantic_provider.strip().lower()
    if provider == "hash":
        return (_hash_embedding(query, hash_dim) if hash_dim > 0 else []), "hash_v1"
    if provider == "openai":
        model = (semantic_model or "text-embedding-3-small").strip()
        return _embed_openai(query, model=model, timeout_sec=timeout_sec), model
    if provider == "gemini":
        model = (semantic_model or "text-embedding-004").strip()
        return _embed_gemini(query, model=model, timeout_sec=timeout_sec), model
    raise RuntimeError(f"Unsupported semantic_provider: {semantic_provider}")


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    aa = a[:n]
    bb = b[:n]
    dot = sum(x * y for x, y in zip(aa, bb))
    na = math.sqrt(sum(x * x for x in aa))
    nb = math.sqrt(sum(y * y for y in bb))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


_QUERY_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "for",
    "of",
    "in",
    "to",
    "with",
    "senior",
    "junior",
    "staff",
    "principal",
    "lead",
    "head",
}
_CRITICAL_QUERY_TOKENS = {
    "ml",
    "llm",
    "recruiter",
    "frontend",
    "react",
    "typescript",
    "devops",
    "kubernetes",
    "terraform",
    "architect",
    "analyst",
}


def _query_tokens(query: str) -> list[str]:
    out: list[str] = []
    for tok in re.findall(r"[a-z0-9+#]+", query.lower()):
        if tok in _QUERY_STOPWORDS or len(tok) <= 1:
            continue
        out.append(tok)
    return out


def _count_hits(tokens: list[str], text: str) -> int:
    if not tokens or not text:
        return 0
    return sum(1 for tok in tokens if tok in text)


def _hybrid_semantic_score(item: dict[str, Any], *, query_tokens: list[str], semantic_score: float) -> tuple[float, float]:
    if not query_tokens:
        return semantic_score, 0.0
    title_text = " ".join(
        [
            str(item.get("title_clean") or ""),
            str(item.get("normalized_title") or ""),
            str(item.get("role_family") or ""),
        ]
    ).lower()
    skills_text = " ".join(str(s) for s in (item.get("skills") or [])).lower()
    all_text = " ".join(
        [
            title_text,
            skills_text,
            str(item.get("employment_type") or ""),
            str(item.get("location_type") or ""),
        ]
    ).lower()

    all_hits = _count_hits(query_tokens, all_text)
    title_hits = _count_hits(query_tokens, title_text)
    skills_hits = _count_hits(query_tokens, skills_text)
    lexical_score = (
        0.50 * (all_hits / len(query_tokens))
        + 0.30 * (title_hits / len(query_tokens))
        + 0.20 * (skills_hits / len(query_tokens))
    )

    # Penalize critical token misses (e.g. "ml", "frontend", "recruiter").
    critical = [tok for tok in query_tokens if tok in _CRITICAL_QUERY_TOKENS]
    miss_count = sum(1 for tok in critical if tok not in all_text)
    mismatch_penalty = min(0.45, miss_count * 0.15)

    hybrid = (0.65 * semantic_score) + (0.35 * lexical_score) - mismatch_penalty
    return hybrid, mismatch_penalty


def _to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(x) for x in value if x is not None and str(x).strip()]
    return [str(value)]


def _criteria_lists(criteria: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for key in ("role_family", "seniority", "location_type", "country", "skills", "source"):
        out[key] = [x.strip().lower() for x in _to_list(criteria.get(key)) if x.strip()]
    return out


class SavedFilterIn(BaseModel):
    user_id: str = "demo"
    name: str
    criteria: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class WebhookNotificationIn(BaseModel):
    webhook_url: str
    limit: int = Field(default=50, ge=1, le=200)
    dry_run: bool = False
    mark_notified: bool = True
    max_retries: int = Field(default=1, ge=0, le=5)
    timeout_sec: int = Field(default=10, ge=3, le=30)


class NotificationTargetIn(BaseModel):
    webhook_url: str
    is_active: bool = True


class JobActionIn(BaseModel):
    user_id: str = "demo"
    action: str
    filter_id: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _since_iso(days: int) -> str:
    return (datetime.utcnow() - timedelta(days=days)).isoformat()


def _build_user_weights(con: sqlite3.Connection, user_id: str) -> dict[str, dict[str, int]]:
    weights: dict[str, dict[str, int]] = {
        "company": {},
        "role_family": {},
        "seniority": {},
        "location_type": {},
        "country": {},
        "skill": {},
    }
    try:
        rows = con.execute(
            "SELECT ja.action, s.company, e.role_family, e.seniority, e.location_type, e.country, e.skills_json "
            "FROM job_actions ja "
            "JOIN seen_jobs s ON s.fingerprint=ja.fingerprint "
            "JOIN jobs_enriched e ON e.fingerprint=ja.fingerprint "
            "WHERE ja.user_id=? "
            "ORDER BY ja.created_at DESC "
            "LIMIT 3000",
            (user_id,),
        ).fetchall()
    except sqlite3.OperationalError:
        return weights

    action_points = {"save": 2, "apply": 4, "dismiss": -3}

    def add(bucket: str, key: str | None, points: int) -> None:
        if not key:
            return
        k = key.strip().lower()
        if not k:
            return
        prev = weights[bucket].get(k, 0)
        weights[bucket][k] = _clamp(prev + points, -20, 20)

    for r in rows:
        points = action_points.get((r["action"] or "").strip().lower(), 0)
        if points == 0:
            continue
        add("company", r["company"], points)
        add("role_family", r["role_family"], points)
        add("seniority", r["seniority"], points)
        add("location_type", r["location_type"], points)
        add("country", r["country"], points)
        for skill in json.loads(r["skills_json"] or "[]"):
            add("skill", str(skill), points)

    return weights


def _personalization_delta(
    weights: dict[str, dict[str, int]],
    company: str | None,
    role_family: str | None,
    seniority: str | None,
    location_type: str | None,
    country: str | None,
    skills: list[str],
) -> int:
    delta = 0
    if company:
        delta += weights["company"].get(company.lower(), 0)
    if role_family:
        delta += int(round(weights["role_family"].get(role_family.lower(), 0) * 0.8))
    if seniority:
        delta += int(round(weights["seniority"].get(seniority.lower(), 0) * 0.5))
    if location_type:
        delta += int(round(weights["location_type"].get(location_type.lower(), 0) * 0.6))
    if country:
        delta += int(round(weights["country"].get(country.lower(), 0) * 0.4))
    for skill in set(skills):
        delta += int(round(weights["skill"].get(skill.lower(), 0) * 0.5))
    return _clamp(delta, -30, 30)


def _build_recommendations(
    con: sqlite3.Connection,
    filter_id: int,
    max_scan: int = 1000,
) -> list[dict[str, Any]]:
    fr = con.execute(
        "SELECT id, user_id, name, criteria_json, is_active FROM saved_filters WHERE id=?",
        (filter_id,),
    ).fetchone()
    if fr is None or int(fr["is_active"]) == 0:
        return []
    user_id = (fr["user_id"] or "demo").strip() or "demo"
    weights = _build_user_weights(con, user_id=user_id)

    criteria = json.loads(fr["criteria_json"] or "{}")
    c = _criteria_lists(criteria)
    where = []
    params: list[Any] = []

    if c["role_family"]:
        where.append("e.role_family IN (" + ",".join("?" for _ in c["role_family"]) + ")")
        params.extend(c["role_family"])
    if c["seniority"]:
        where.append("e.seniority IN (" + ",".join("?" for _ in c["seniority"]) + ")")
        params.extend(c["seniority"])
    if c["location_type"]:
        where.append("e.location_type IN (" + ",".join("?" for _ in c["location_type"]) + ")")
        params.extend(c["location_type"])
    if c["country"]:
        where.append("LOWER(e.country) IN (" + ",".join("?" for _ in c["country"]) + ")")
        params.extend(c["country"])
    if c["source"]:
        where.append("LOWER(s.source) IN (" + ",".join("?" for _ in c["source"]) + ")")
        params.extend(c["source"])

    sql = (
        "SELECT s.fingerprint, s.company, s.title, s.url, s.source, s.location, s.remote, s.published_at, "
        "e.role_family, e.seniority, e.location_type, e.country, e.skills_json "
        "FROM seen_jobs s "
        "JOIN jobs_enriched e ON e.fingerprint = s.fingerprint"
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY s.first_seen DESC LIMIT ?"
    rows = con.execute(sql, [*params, max_scan]).fetchall()

    scored: list[dict[str, Any]] = []
    for r in rows:
        base_score = 0
        reasons: list[str] = []
        skills = [str(x).lower() for x in json.loads(r["skills_json"] or "[]")]

        if c["role_family"] and (r["role_family"] or "").lower() in c["role_family"]:
            base_score += 40
            reasons.append("role_family")
        if c["seniority"] and (r["seniority"] or "").lower() in c["seniority"]:
            base_score += 20
            reasons.append("seniority")
        if c["location_type"] and (r["location_type"] or "").lower() in c["location_type"]:
            base_score += 15
            reasons.append("location_type")
        if c["country"] and (r["country"] or "").lower() in c["country"]:
            base_score += 10
            reasons.append("country")
        if c["source"] and (r["source"] or "").lower() in c["source"]:
            base_score += 5
            reasons.append("source")
        if c["skills"]:
            overlap = sorted(set(c["skills"]).intersection(skills))
            if overlap:
                base_score += min(30, 10 * len(overlap))
                reasons.append("skills:" + ",".join(overlap))

        has_criteria = any(c[k] for k in c)
        if has_criteria and base_score == 0:
            continue

        personal_delta = _personalization_delta(
            weights=weights,
            company=r["company"],
            role_family=r["role_family"],
            seniority=r["seniority"],
            location_type=r["location_type"],
            country=r["country"],
            skills=skills,
        )
        score = _clamp(base_score + personal_delta, 0, 100)
        if personal_delta != 0:
            sign = "+" if personal_delta > 0 else ""
            reasons.append(f"personalization:{sign}{personal_delta}")

        scored.append(
            {
                "fingerprint": r["fingerprint"],
                "company": r["company"],
                "title": r["title"],
                "url": r["url"],
                "source": r["source"],
                "location": r["location"],
                "remote": None if r["remote"] is None else bool(r["remote"]),
                "published_at": r["published_at"],
                "role_family": r["role_family"],
                "seniority": r["seniority"],
                "location_type": r["location_type"],
                "country": r["country"],
                "skills": skills,
                "base_score": base_score,
                "score": score,
                "reasons": reasons,
            }
        )
    scored.sort(key=lambda x: (x["score"], x["published_at"] or ""), reverse=True)
    return scored


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        return dt.isoformat()
    except Exception:
        return None


@app.get("/v1/indexed/jobs")
def list_indexed_jobs(
    db_path: str = Query("data/jobintel_microsaas.sqlite"),
    q: str | None = None,
    company: str | None = None,
    source: str | None = None,
    normalized_title: str | None = None,
    role_family: str | None = None,
    seniority: str | None = None,
    location_type: str | None = None,
    employment_type: str | None = None,
    country: str | None = None,
    city: str | None = None,
    skill: str | None = None,
    semantic_query: str | None = None,
    semantic_provider: str = Query("hash"),
    semantic_model: str | None = None,
    semantic_timeout_sec: int = Query(20, ge=5, le=60),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []

    if q:
        where.append("(title_raw LIKE ? OR title_clean LIKE ? OR company_name LIKE ? OR url LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like, like, like])
    if company:
        where.append("company_name = ?")
        params.append(company)
    if source:
        where.append("source = ?")
        params.append(source)
    if normalized_title:
        where.append("normalized_title = ?")
        params.append(normalized_title)
    if role_family:
        where.append("role_family = ?")
        params.append(role_family)
    if seniority:
        where.append("seniority = ?")
        params.append(seniority)
    if location_type:
        where.append("location_type = ?")
        params.append(location_type)
    if employment_type:
        where.append("employment_type = ?")
        params.append(employment_type)
    if country:
        where.append("country = ?")
        params.append(country)
    if city:
        where.append("city = ?")
        params.append(city)

    sql = (
        "SELECT id, source, source_job_id, source_org, url, company_name, title_raw, title_clean, "
        "normalized_title, role_family, occupation_group, seniority, employment_type, location_type, "
        "city, region, country, salary_min, salary_max, salary_currency, skills_json, tags_json, "
        "embedding_json, embedding_model, tagger_version, tag_confidence, indexed_at "
        "FROM jobs_indexed"
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY indexed_at DESC LIMIT ? OFFSET ?"
    params.extend([limit * (5 if semantic_query else 1), offset])

    with _connect(db_path) as con:
        _ensure_microsaas_tables(con)
        rows = con.execute(sql, params).fetchall()

    items: list[dict[str, Any]] = []
    skill_filter = skill.strip().lower() if skill else None
    for r in rows:
        skills = [str(x) for x in json.loads(r["skills_json"] or "[]")]
        if skill_filter and skill_filter not in {s.lower() for s in skills}:
            continue
        items.append(
            {
                "id": r["id"],
                "source": r["source"],
                "source_job_id": r["source_job_id"],
                "source_org": r["source_org"],
                "url": r["url"],
                "company_name": r["company_name"],
                "title_raw": r["title_raw"],
                "title_clean": r["title_clean"],
                "normalized_title": r["normalized_title"],
                "role_family": r["role_family"],
                "occupation_group": r["occupation_group"],
                "seniority": r["seniority"],
                "employment_type": r["employment_type"],
                "location_type": r["location_type"],
                "city": r["city"],
                "region": r["region"],
                "country": r["country"],
                "salary_min": r["salary_min"],
                "salary_max": r["salary_max"],
                "salary_currency": r["salary_currency"],
                "skills": skills,
                "tags": json.loads(r["tags_json"] or "{}"),
                "embedding_model": r["embedding_model"],
                "tagger_version": r["tagger_version"],
                "tag_confidence": r["tag_confidence"],
                "indexed_at": r["indexed_at"],
                "_embedding": _to_float_list(r["embedding_json"]),
            }
        )

    if semantic_query:
        q_tokens = _query_tokens(semantic_query)
        dim = 0
        for item in items:
            if item["_embedding"]:
                dim = len(item["_embedding"])
                break
        try:
            q_emb, q_model = _compute_query_embedding(
                semantic_query,
                semantic_provider=semantic_provider,
                semantic_model=semantic_model,
                timeout_sec=semantic_timeout_sec,
                hash_dim=dim,
            )
        except urlerror.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"semantic embedding HTTP error: {e.code}") from e
        except urlerror.URLError as e:
            raise HTTPException(status_code=502, detail=f"semantic embedding network error: {e}") from e
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        for item in items:
            sem = _cosine(q_emb, item["_embedding"])
            hybrid, penalty = _hybrid_semantic_score(item, query_tokens=q_tokens, semantic_score=sem)
            item["semantic_score"] = round(sem, 6)
            item["hybrid_score"] = round(hybrid, 6)
            item["mismatch_penalty"] = round(penalty, 6)
            item["semantic_query_model"] = q_model
        items.sort(key=lambda item: item.get("hybrid_score", item.get("semantic_score", 0.0)), reverse=True)

    out: list[dict[str, Any]] = []
    for item in items[:limit]:
        item.pop("_embedding", None)
        out.append(item)
    return out


@app.get("/v1/indexed/filters/options")
def list_indexed_filter_options(
    db_path: str = Query("data/jobintel_microsaas.sqlite"),
    top_skills: int = Query(200, ge=20, le=1000),
) -> dict[str, list[str]]:
    with _connect(db_path) as con:
        _ensure_microsaas_tables(con)
        normalized_title = [
            row["v"]
            for row in con.execute(
                "SELECT normalized_title AS v, COUNT(*) AS c FROM jobs_indexed "
                "WHERE normalized_title IS NOT NULL AND normalized_title <> '' "
                "GROUP BY normalized_title ORDER BY c DESC, v ASC"
            )
        ]
        role_family = [
            row["v"]
            for row in con.execute(
                "SELECT role_family AS v, COUNT(*) AS c FROM jobs_indexed "
                "WHERE role_family IS NOT NULL AND role_family <> '' "
                "GROUP BY role_family ORDER BY c DESC, v ASC"
            )
        ]
        seniority = [
            row["v"]
            for row in con.execute(
                "SELECT seniority AS v, COUNT(*) AS c FROM jobs_indexed "
                "WHERE seniority IS NOT NULL AND seniority <> '' "
                "GROUP BY seniority ORDER BY c DESC, v ASC"
            )
        ]
        location_type = [
            row["v"]
            for row in con.execute(
                "SELECT location_type AS v, COUNT(*) AS c FROM jobs_indexed "
                "WHERE location_type IS NOT NULL AND location_type <> '' "
                "GROUP BY location_type ORDER BY c DESC, v ASC"
            )
        ]
        employment_type = [
            row["v"]
            for row in con.execute(
                "SELECT employment_type AS v, COUNT(*) AS c FROM jobs_indexed "
                "WHERE employment_type IS NOT NULL AND employment_type <> '' "
                "GROUP BY employment_type ORDER BY c DESC, v ASC"
            )
        ]
        countries = [
            row["v"]
            for row in con.execute(
                "SELECT country AS v, COUNT(*) AS c FROM jobs_indexed "
                "WHERE country IS NOT NULL AND country <> '' "
                "GROUP BY country ORDER BY c DESC, v ASC"
            )
        ]
        sources = [
            row["v"]
            for row in con.execute(
                "SELECT source AS v, COUNT(*) AS c FROM jobs_indexed "
                "WHERE source IS NOT NULL AND source <> '' "
                "GROUP BY source ORDER BY c DESC, v ASC"
            )
        ]

        try:
            skills = [
                row["v"]
                for row in con.execute(
                    "SELECT LOWER(j.value) AS v, COUNT(*) AS c "
                    "FROM jobs_indexed e, json_each(e.skills_json) j "
                    "WHERE j.value IS NOT NULL AND j.value <> '' "
                    "GROUP BY LOWER(j.value) ORDER BY c DESC, v ASC LIMIT ?",
                    (top_skills,),
                )
            ]
        except sqlite3.OperationalError:
            skill_counts: dict[str, int] = {}
            for row in con.execute("SELECT skills_json FROM jobs_indexed"):
                for s in json.loads(row["skills_json"] or "[]"):
                    k = str(s).strip().lower()
                    if not k:
                        continue
                    skill_counts[k] = skill_counts.get(k, 0) + 1
            skills = [k for k, _ in sorted(skill_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top_skills]]

    return {
        "normalized_title": normalized_title,
        "role_family": role_family,
        "seniority": seniority,
        "location_type": location_type,
        "employment_type": employment_type,
        "country": countries,
        "source": sources,
        "skills": skills,
    }


@app.get("/ui", include_in_schema=False)
def ui_page() -> FileResponse:
    page = _UI_DIR / "index.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="UI not found")
    return FileResponse(page)


@app.get("/jobs")
def list_jobs(
    db_path: str = Query("data/jobintel.sqlite"),
    q: str | None = None,
    company: str | None = None,
    source: str | None = None,
    remote: bool | None = None,
    location: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    return _list_jobs_common(
        db_path=db_path,
        q=q,
        company=company,
        source=source,
        remote=remote,
        location=location,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
        include_score=False,
        min_score=None,
    )


@app.get("/jobs/scored")
def list_scored_jobs(
    db_path: str = Query("data/jobintel.sqlite"),
    min_score: int | None = Query(None, ge=0, le=100),
    q: str | None = None,
    company: str | None = None,
    source: str | None = None,
    remote: bool | None = None,
    location: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    return _list_jobs_common(
        db_path=db_path,
        q=q,
        company=company,
        source=source,
        remote=remote,
        location=location,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
        include_score=True,
        min_score=min_score,
    )


def _list_jobs_common(
    *,
    db_path: str,
    q: str | None,
    company: str | None,
    source: str | None,
    remote: bool | None,
    location: str | None,
    date_from: str | None,
    date_to: str | None,
    limit: int,
    offset: int,
    include_score: bool,
    min_score: int | None,
) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []

    if min_score is not None:
        where.append("score >= ?")
        params.append(min_score)
    if q:
        where.append("(title LIKE ? OR company LIKE ? OR location LIKE ? OR url LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like, like, like])
    if company:
        where.append("company = ?")
        params.append(company)
    if source:
        where.append("source = ?")
        params.append(source)
    if remote is not None:
        where.append("remote = ?")
        params.append(1 if remote else 0)
    if location:
        where.append("location LIKE ?")
        params.append(f"%{location}%")

    df = _parse_date(date_from)
    if df:
        where.append("published_at >= ?")
        params.append(df)
    dt = _parse_date(date_to)
    if dt:
        where.append("published_at <= ?")
        params.append(dt)

    if include_score:
        sql = "SELECT score, company, title, url, source, location, remote, published_at FROM seen_jobs"
    else:
        sql = "SELECT company, title, url, source, location, remote, published_at FROM seen_jobs"

    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY first_seen DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with _connect(db_path) as con:
        _ensure_columns(con)
        rows = con.execute(sql, params).fetchall()

    out: list[dict[str, Any]] = []
    for r in rows:
        item = {
            "company": r["company"],
            "title": r["title"],
            "url": r["url"],
            "source": r["source"],
            "location": r["location"],
            "remote": None if r["remote"] is None else bool(r["remote"]),
            "published_at": r["published_at"],
        }
        if include_score:
            item["score"] = r["score"]
        out.append(item)
    return out


@app.get("/filters")
def list_filters(
    db_path: str = Query("data/jobintel.sqlite"),
    top_companies: int = Query(50, ge=1, le=200),
    top_locations: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    with _connect(db_path) as con:
        _ensure_columns(con)
        total_jobs = con.execute("SELECT COUNT(*) AS c FROM seen_jobs").fetchone()["c"]
        sources = [row["source"] for row in con.execute("SELECT DISTINCT source FROM seen_jobs ORDER BY source")]
        companies = [
            {"company": row["company"], "count": row["count"]}
            for row in con.execute(
                "SELECT company, COUNT(*) AS count FROM seen_jobs GROUP BY company ORDER BY count DESC, company ASC LIMIT ?",
                (top_companies,),
            )
        ]
        locations = [
            {"location": row["location"], "count": row["count"]}
            for row in con.execute(
                "SELECT location, COUNT(*) AS count FROM seen_jobs "
                "WHERE location IS NOT NULL AND location <> '' "
                "GROUP BY location ORDER BY count DESC, location ASC LIMIT ?",
                (top_locations,),
            )
        ]
        remote_counts = {
            str(row["remote"]): row["count"]
            for row in con.execute("SELECT remote, COUNT(*) AS count FROM seen_jobs GROUP BY remote")
        }

    return {
        "total_jobs": total_jobs,
        "sources": sources,
        "top_companies": companies,
        "top_locations": locations,
        "remote_counts": remote_counts,
    }


@app.get("/filters/options")
def list_filter_options(
    db_path: str = Query("data/jobintel.sqlite"),
    top_skills: int = Query(200, ge=20, le=1000),
    top_countries: int = Query(120, ge=20, le=400),
) -> dict[str, list[str]]:
    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_enriched_table(con)

        role_family = [
            row["v"]
            for row in con.execute(
                "SELECT role_family AS v, COUNT(*) AS c FROM jobs_enriched "
                "WHERE role_family IS NOT NULL AND role_family <> '' "
                "GROUP BY role_family ORDER BY c DESC, v ASC"
            )
        ]
        seniority = [
            row["v"]
            for row in con.execute(
                "SELECT seniority AS v, COUNT(*) AS c FROM jobs_enriched "
                "WHERE seniority IS NOT NULL AND seniority <> '' "
                "GROUP BY seniority ORDER BY c DESC, v ASC"
            )
        ]
        location_type = [
            row["v"]
            for row in con.execute(
                "SELECT location_type AS v, COUNT(*) AS c FROM jobs_enriched "
                "WHERE location_type IS NOT NULL AND location_type <> '' "
                "GROUP BY location_type ORDER BY c DESC, v ASC"
            )
        ]
        country = [
            row["v"]
            for row in con.execute(
                "SELECT LOWER(country) AS v, COUNT(*) AS c FROM jobs_enriched "
                "WHERE country IS NOT NULL AND country <> '' "
                "GROUP BY LOWER(country) ORDER BY c DESC, v ASC LIMIT ?",
                (top_countries,),
            )
        ]
        source = [
            row["v"]
            for row in con.execute(
                "SELECT LOWER(source) AS v, COUNT(*) AS c FROM seen_jobs "
                "WHERE source IS NOT NULL AND source <> '' "
                "GROUP BY LOWER(source) ORDER BY c DESC, v ASC"
            )
        ]

        # Expand skills_json in SQLite using json_each; fallback to empty on DBs without json1.
        try:
            skills = [
                row["v"]
                for row in con.execute(
                    "SELECT LOWER(j.value) AS v, COUNT(*) AS c "
                    "FROM jobs_enriched e, json_each(e.skills_json) j "
                    "WHERE j.value IS NOT NULL AND j.value <> '' "
                    "GROUP BY LOWER(j.value) ORDER BY c DESC, v ASC LIMIT ?",
                    (top_skills,),
                )
            ]
        except sqlite3.OperationalError:
            skills = []

    return {
        "role_family": role_family,
        "seniority": seniority,
        "location_type": location_type,
        "country": country,
        "source": source,
        "skills": skills,
    }


@app.get("/saved-filters")
def list_saved_filters(
    db_path: str = Query("data/jobintel.sqlite"),
    user_id: str = Query("demo"),
) -> list[dict[str, Any]]:
    with _connect(db_path) as con:
        _ensure_saved_filters_table(con)
        rows = con.execute(
            "SELECT id, user_id, name, criteria_json, is_active, created_at, updated_at "
            "FROM saved_filters WHERE user_id=? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "name": r["name"],
            "criteria": json.loads(r["criteria_json"] or "{}"),
            "is_active": bool(r["is_active"]),
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]


@app.post("/saved-filters")
def create_saved_filter(
    payload: SavedFilterIn,
    db_path: str = Query("data/jobintel.sqlite"),
) -> dict[str, Any]:
    now = datetime.utcnow().isoformat()
    criteria_norm = _criteria_lists(payload.criteria)
    with _connect(db_path) as con:
        _ensure_saved_filters_table(con)
        cur = con.execute(
            "INSERT INTO saved_filters(user_id, name, criteria_json, is_active, created_at, updated_at) "
            "VALUES(?,?,?,?,?,?)",
            (
                payload.user_id,
                payload.name.strip(),
                json.dumps(criteria_norm, ensure_ascii=True),
                1 if payload.is_active else 0,
                now,
                now,
            ),
        )
        new_id = cur.lastrowid
    return {"id": new_id, "status": "created"}


@app.put("/saved-filters/{filter_id}")
def update_saved_filter(
    filter_id: int,
    payload: SavedFilterIn,
    db_path: str = Query("data/jobintel.sqlite"),
) -> dict[str, Any]:
    now = datetime.utcnow().isoformat()
    criteria_norm = _criteria_lists(payload.criteria)
    with _connect(db_path) as con:
        _ensure_saved_filters_table(con)
        cur = con.execute(
            "UPDATE saved_filters "
            "SET user_id=?, name=?, criteria_json=?, is_active=?, updated_at=? "
            "WHERE id=?",
            (
                payload.user_id,
                payload.name.strip(),
                json.dumps(criteria_norm, ensure_ascii=True),
                1 if payload.is_active else 0,
                now,
                filter_id,
            ),
        )
        if cur.rowcount == 0:
            return {"status": "not_found", "id": filter_id}
    return {"status": "updated", "id": filter_id}


@app.delete("/saved-filters/{filter_id}")
def delete_saved_filter(
    filter_id: int,
    db_path: str = Query("data/jobintel.sqlite"),
) -> dict[str, Any]:
    with _connect(db_path) as con:
        _ensure_saved_filters_table(con)
        cur = con.execute("DELETE FROM saved_filters WHERE id=?", (filter_id,))
        if cur.rowcount == 0:
            return {"status": "not_found", "id": filter_id}
    return {"status": "deleted", "id": filter_id}


@app.get("/recommendations/{filter_id}")
def list_recommendations(
    filter_id: int,
    db_path: str = Query("data/jobintel.sqlite"),
    max_scan: int = Query(1000, ge=100, le=5000),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_enriched_table(con)
        _ensure_saved_filters_table(con)
        scored = _build_recommendations(con, filter_id=filter_id, max_scan=max_scan)

    out = []
    for row in scored[offset : offset + limit]:
        item = dict(row)
        item.pop("fingerprint", None)
        out.append(item)
    return out


@app.post("/matches/refresh/{filter_id}")
def refresh_filter_matches(
    filter_id: int,
    db_path: str = Query("data/jobintel.sqlite"),
    max_scan: int = Query(1000, ge=100, le=5000),
) -> dict[str, Any]:
    now = datetime.utcnow().isoformat()
    inserted = 0
    updated = 0

    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_enriched_table(con)
        _ensure_saved_filters_table(con)
        _ensure_filter_matches_table(con)

        scored = _build_recommendations(con, filter_id=filter_id, max_scan=max_scan)
        for row in scored:
            fp = row["fingerprint"]
            exists = con.execute(
                "SELECT id FROM filter_matches WHERE filter_id=? AND fingerprint=?",
                (filter_id, fp),
            ).fetchone()
            if exists:
                con.execute(
                    "UPDATE filter_matches SET score=?, reasons_json=?, last_seen=? "
                    "WHERE filter_id=? AND fingerprint=?",
                    (int(row["score"]), json.dumps(row["reasons"], ensure_ascii=True), now, filter_id, fp),
                )
                updated += 1
            else:
                con.execute(
                    "INSERT INTO filter_matches(filter_id, fingerprint, score, reasons_json, matched_at, last_seen, is_new, notified) "
                    "VALUES(?,?,?,?,?,?,1,0)",
                    (
                        filter_id,
                        fp,
                        int(row["score"]),
                        json.dumps(row["reasons"], ensure_ascii=True),
                        now,
                        now,
                    ),
                )
                inserted += 1

    return {"filter_id": filter_id, "inserted": inserted, "updated": updated, "scanned": len(scored)}


@app.get("/matches/new/{filter_id}")
def list_new_matches(
    filter_id: int,
    db_path: str = Query("data/jobintel.sqlite"),
    mark_seen: bool = False,
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_enriched_table(con)
        _ensure_saved_filters_table(con)
        _ensure_filter_matches_table(con)

        rows = con.execute(
            "SELECT fm.id, fm.fingerprint, fm.score, fm.reasons_json, fm.matched_at, "
            "s.company, s.title, s.url, s.source, s.location, s.remote, s.published_at, "
            "e.role_family, e.seniority, e.location_type, e.country, e.skills_json "
            "FROM filter_matches fm "
            "JOIN seen_jobs s ON s.fingerprint=fm.fingerprint "
            "JOIN jobs_enriched e ON e.fingerprint=fm.fingerprint "
            "WHERE fm.filter_id=? AND fm.is_new=1 "
            "ORDER BY fm.matched_at DESC LIMIT ?",
            (filter_id, limit),
        ).fetchall()

        if mark_seen and rows:
            con.executemany(
                "UPDATE filter_matches SET is_new=0 WHERE id=?",
                [(r["id"],) for r in rows],
            )

    out = []
    for r in rows:
        out.append(
            {
                "fingerprint": r["fingerprint"],
                "company": r["company"],
                "title": r["title"],
                "url": r["url"],
                "source": r["source"],
                "location": r["location"],
                "remote": None if r["remote"] is None else bool(r["remote"]),
                "published_at": r["published_at"],
                "role_family": r["role_family"],
                "seniority": r["seniority"],
                "location_type": r["location_type"],
                "country": r["country"],
                "skills": json.loads(r["skills_json"] or "[]"),
                "score": int(r["score"]),
                "reasons": json.loads(r["reasons_json"] or "[]"),
                "matched_at": r["matched_at"],
            }
        )
    return out


@app.get("/notifications/pending/{filter_id}")
def list_pending_notifications(
    filter_id: int,
    db_path: str = Query("data/jobintel.sqlite"),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_enriched_table(con)
        _ensure_saved_filters_table(con)
        _ensure_filter_matches_table(con)

        rows = con.execute(
            "SELECT fm.id, fm.fingerprint, fm.score, fm.reasons_json, fm.matched_at, fm.notified, "
            "s.company, s.title, s.url, s.source, s.location, s.remote, s.published_at, "
            "e.role_family, e.seniority, e.location_type, e.country, e.skills_json "
            "FROM filter_matches fm "
            "JOIN seen_jobs s ON s.fingerprint=fm.fingerprint "
            "JOIN jobs_enriched e ON e.fingerprint=fm.fingerprint "
            "WHERE fm.filter_id=? AND fm.notified=0 "
            "ORDER BY fm.matched_at DESC LIMIT ?",
            (filter_id, limit),
        ).fetchall()

    out = []
    for r in rows:
        out.append(
            {
                "fingerprint": r["fingerprint"],
                "company": r["company"],
                "title": r["title"],
                "url": r["url"],
                "source": r["source"],
                "location": r["location"],
                "remote": None if r["remote"] is None else bool(r["remote"]),
                "published_at": r["published_at"],
                "role_family": r["role_family"],
                "seniority": r["seniority"],
                "location_type": r["location_type"],
                "country": r["country"],
                "skills": json.loads(r["skills_json"] or "[]"),
                "score": int(r["score"]),
                "reasons": json.loads(r["reasons_json"] or "[]"),
                "matched_at": r["matched_at"],
                "notified": bool(r["notified"]),
            }
        )
    return out


@app.get("/notifications/targets/{filter_id}")
def list_notification_targets(
    filter_id: int,
    db_path: str = Query("data/jobintel.sqlite"),
) -> list[dict[str, Any]]:
    with _connect(db_path) as con:
        _ensure_notification_targets_table(con)
        rows = con.execute(
            "SELECT id, filter_id, webhook_url, is_active, created_at, updated_at "
            "FROM notification_targets WHERE filter_id=? ORDER BY updated_at DESC",
            (filter_id,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "filter_id": r["filter_id"],
            "webhook_url": r["webhook_url"],
            "is_active": bool(r["is_active"]),
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]


@app.post("/notifications/targets/{filter_id}")
def upsert_notification_target(
    filter_id: int,
    payload: NotificationTargetIn,
    db_path: str = Query("data/jobintel.sqlite"),
) -> dict[str, Any]:
    now = datetime.utcnow().isoformat()
    webhook_url = payload.webhook_url.strip()
    with _connect(db_path) as con:
        _ensure_saved_filters_table(con)
        _ensure_notification_targets_table(con)
        fr = con.execute("SELECT id FROM saved_filters WHERE id=?", (filter_id,)).fetchone()
        if fr is None:
            return {"status": "not_found", "filter_id": filter_id}
        con.execute(
            "INSERT INTO notification_targets(filter_id, webhook_url, is_active, created_at, updated_at) "
            "VALUES(?,?,?,?,?) "
            "ON CONFLICT(filter_id, webhook_url) DO UPDATE SET is_active=excluded.is_active, updated_at=excluded.updated_at",
            (filter_id, webhook_url, 1 if payload.is_active else 0, now, now),
        )
    return {"status": "upserted", "filter_id": filter_id, "webhook_url": webhook_url, "is_active": payload.is_active}


@app.delete("/notifications/targets/{filter_id}")
def delete_notification_target(
    filter_id: int,
    webhook_url: str = Query(...),
    db_path: str = Query("data/jobintel.sqlite"),
) -> dict[str, Any]:
    with _connect(db_path) as con:
        _ensure_notification_targets_table(con)
        cur = con.execute(
            "DELETE FROM notification_targets WHERE filter_id=? AND webhook_url=?",
            (filter_id, webhook_url.strip()),
        )
        if cur.rowcount == 0:
            return {"status": "not_found", "filter_id": filter_id, "webhook_url": webhook_url.strip()}
    return {"status": "deleted", "filter_id": filter_id, "webhook_url": webhook_url.strip()}


@app.post("/notifications/webhook/{filter_id}")
def send_webhook_notifications(
    filter_id: int,
    payload: WebhookNotificationIn,
    db_path: str = Query("data/jobintel.sqlite"),
) -> dict[str, Any]:
    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_enriched_table(con)
        _ensure_saved_filters_table(con)
        _ensure_filter_matches_table(con)
        _ensure_notification_attempts_table(con)
        _ensure_notification_targets_table(con)

        fr = con.execute("SELECT id, user_id, name FROM saved_filters WHERE id=?", (filter_id,)).fetchone()
        if fr is None:
            return {"status": "not_found", "filter_id": filter_id}

        rows = con.execute(
            "SELECT fm.id, fm.fingerprint, fm.score, fm.reasons_json, fm.matched_at, "
            "s.company, s.title, s.url, s.source, s.location, s.remote, s.published_at, "
            "e.role_family, e.seniority, e.location_type, e.country, e.skills_json "
            "FROM filter_matches fm "
            "JOIN seen_jobs s ON s.fingerprint=fm.fingerprint "
            "JOIN jobs_enriched e ON e.fingerprint=fm.fingerprint "
            "WHERE fm.filter_id=? AND fm.notified=0 "
            "ORDER BY fm.matched_at DESC LIMIT ?",
            (filter_id, payload.limit),
        ).fetchall()

        if not rows:
            return {"status": "no_pending", "filter_id": filter_id, "sent": 0}

        matches = []
        for r in rows:
            matches.append(
                {
                    "fingerprint": r["fingerprint"],
                    "company": r["company"],
                    "title": r["title"],
                    "url": r["url"],
                    "source": r["source"],
                    "location": r["location"],
                    "remote": None if r["remote"] is None else bool(r["remote"]),
                    "published_at": r["published_at"],
                    "role_family": r["role_family"],
                    "seniority": r["seniority"],
                    "location_type": r["location_type"],
                    "country": r["country"],
                    "skills": json.loads(r["skills_json"] or "[]"),
                    "score": int(r["score"]),
                    "reasons": json.loads(r["reasons_json"] or "[]"),
                    "matched_at": r["matched_at"],
                }
            )

        event = {
            "event": "new_matches",
            "sent_at": datetime.utcnow().isoformat(),
            "filter": {"id": fr["id"], "user_id": fr["user_id"], "name": fr["name"]},
            "count": len(matches),
            "matches": matches,
        }

        if payload.dry_run:
            con.execute(
                "INSERT INTO notification_attempts(filter_id, webhook_url, status, http_status, sent_count, error, created_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (filter_id, payload.webhook_url.strip(), "dry_run", None, 0, None, datetime.utcnow().isoformat()),
            )
            return {"status": "dry_run", "filter_id": filter_id, "sent": 0, "preview_count": len(matches), "event": event}

        status_code: int | None = None
        response_body = ""
        last_error: str | None = None
        for _ in range(payload.max_retries + 1):
            body = json.dumps(event, ensure_ascii=True).encode("utf-8")
            req = urlrequest.Request(
                payload.webhook_url.strip(),
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urlrequest.urlopen(req, timeout=payload.timeout_sec) as resp:
                    status_code = int(resp.getcode())
                    response_body = resp.read().decode("utf-8", errors="replace")
                if 200 <= status_code < 300:
                    last_error = None
                    break
                last_error = response_body[:1000]
            except urlerror.HTTPError as exc:
                status_code = int(exc.code)
                response_body = exc.read().decode("utf-8", errors="replace")
                last_error = response_body[:1000]
            except urlerror.URLError as exc:
                status_code = None
                last_error = str(exc.reason)

        if last_error is not None:
            con.execute(
                "INSERT INTO notification_attempts(filter_id, webhook_url, status, http_status, sent_count, error, created_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    filter_id,
                    payload.webhook_url.strip(),
                    "error",
                    status_code,
                    0,
                    last_error[:1000],
                    datetime.utcnow().isoformat(),
                ),
            )
            out: dict[str, Any] = {"status": "webhook_error", "filter_id": filter_id, "sent": 0}
            if status_code is not None:
                out["http_status"] = status_code
            out["error"] = last_error[:1000]
            return out

        updated = 0
        if payload.mark_notified:
            con.executemany(
                "UPDATE filter_matches SET notified=1 WHERE id=?",
                [(r["id"],) for r in rows],
            )
            updated = len(rows)
        con.execute(
            "INSERT INTO notification_attempts(filter_id, webhook_url, status, http_status, sent_count, error, created_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (
                filter_id,
                payload.webhook_url.strip(),
                "sent",
                int(status_code or 200),
                len(rows),
                None,
                datetime.utcnow().isoformat(),
            ),
        )

    return {
        "status": "sent",
        "filter_id": filter_id,
        "sent": len(rows),
        "marked_notified": updated,
        "webhook_status": status_code,
    }


@app.post("/jobs/{fingerprint}/actions")
def create_job_action(
    fingerprint: str,
    payload: JobActionIn,
    db_path: str = Query("data/jobintel.sqlite"),
) -> dict[str, Any]:
    action = payload.action.strip().lower()
    allowed = {"save", "dismiss", "apply"}
    if action not in allowed:
        raise HTTPException(status_code=422, detail=f"invalid action '{action}', allowed: save,dismiss,apply")

    now = datetime.utcnow().isoformat()
    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_filter_matches_table(con)
        _ensure_job_actions_table(con)

        exists = con.execute("SELECT 1 FROM seen_jobs WHERE fingerprint=?", (fingerprint,)).fetchone()
        if exists is None:
            return {"status": "not_found", "fingerprint": fingerprint}

        cur = con.execute(
            "INSERT INTO job_actions(user_id, fingerprint, action, filter_id, metadata_json, created_at) "
            "VALUES(?,?,?,?,?,?)",
            (
                payload.user_id.strip() or "demo",
                fingerprint,
                action,
                payload.filter_id,
                json.dumps(payload.metadata, ensure_ascii=True),
                now,
            ),
        )

        if payload.filter_id is not None:
            con.execute(
                "UPDATE filter_matches SET is_new=0 WHERE filter_id=? AND fingerprint=?",
                (payload.filter_id, fingerprint),
            )

    return {"status": "created", "id": cur.lastrowid, "fingerprint": fingerprint, "action": action}


@app.get("/jobs/{fingerprint}/actions")
def list_job_actions(
    fingerprint: str,
    db_path: str = Query("data/jobintel.sqlite"),
    user_id: str = Query("demo"),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_job_actions_table(con)
        rows = con.execute(
            "SELECT id, user_id, fingerprint, action, filter_id, metadata_json, created_at "
            "FROM job_actions "
            "WHERE fingerprint=? AND user_id=? "
            "ORDER BY created_at DESC LIMIT ?",
            (fingerprint, user_id, limit),
        ).fetchall()

    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "fingerprint": r["fingerprint"],
                "action": r["action"],
                "filter_id": r["filter_id"],
                "metadata": json.loads(r["metadata_json"] or "{}"),
                "created_at": r["created_at"],
            }
        )
    return out


@app.post("/ops/run-once")
def run_ops_once(
    db_path: str = Query("data/jobintel.sqlite"),
    max_scan: int = Query(1000, ge=100, le=5000),
    notify_limit: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    refreshed_filters = 0
    notifications_sent = 0
    notifications_errors = 0
    with _connect(db_path) as con:
        _ensure_saved_filters_table(con)
        _ensure_notification_targets_table(con)
        active_filters = con.execute(
            "SELECT id FROM saved_filters WHERE is_active=1 ORDER BY id ASC"
        ).fetchall()
        targets_by_filter: dict[int, list[str]] = {}
        for row in con.execute(
            "SELECT filter_id, webhook_url FROM notification_targets WHERE is_active=1 ORDER BY id ASC"
        ).fetchall():
            targets_by_filter.setdefault(int(row["filter_id"]), []).append(row["webhook_url"])

    details: list[dict[str, Any]] = []
    for row in active_filters:
        filter_id = int(row["id"])
        refresh_out = refresh_filter_matches(filter_id=filter_id, db_path=db_path, max_scan=max_scan)
        refreshed_filters += 1
        notif_results: list[dict[str, Any]] = []
        for webhook_url in targets_by_filter.get(filter_id, []):
            out = send_webhook_notifications(
                filter_id=filter_id,
                payload=WebhookNotificationIn(
                    webhook_url=webhook_url,
                    limit=notify_limit,
                    dry_run=False,
                    mark_notified=True,
                    max_retries=1,
                    timeout_sec=10,
                ),
                db_path=db_path,
            )
            notif_results.append(out)
            if out.get("status") == "sent":
                notifications_sent += int(out.get("sent", 0))
            elif out.get("status") == "webhook_error":
                notifications_errors += 1
        details.append({"filter_id": filter_id, "refresh": refresh_out, "notifications": notif_results})

    return {
        "status": "ok",
        "refreshed_filters": refreshed_filters,
        "notifications_sent_jobs": notifications_sent,
        "notifications_error_count": notifications_errors,
        "details": details,
    }


@app.get("/ops/metrics")
def get_ops_metrics(
    db_path: str = Query("data/jobintel.sqlite"),
    days: int = Query(7, ge=1, le=90),
) -> dict[str, Any]:
    since = _since_iso(days)
    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_saved_filters_table(con)
        _ensure_filter_matches_table(con)
        _ensure_job_actions_table(con)
        _ensure_notification_attempts_table(con)

        jobs_new = con.execute(
            "SELECT COUNT(*) AS c FROM seen_jobs WHERE first_seen >= ?",
            (since,),
        ).fetchone()["c"]
        filters_total = con.execute("SELECT COUNT(*) AS c FROM saved_filters").fetchone()["c"]
        filters_active = con.execute("SELECT COUNT(*) AS c FROM saved_filters WHERE is_active=1").fetchone()["c"]

        matches_new = con.execute(
            "SELECT COUNT(*) AS c FROM filter_matches WHERE matched_at >= ? AND is_new=1",
            (since,),
        ).fetchone()["c"]
        matches_notified = con.execute(
            "SELECT COUNT(*) AS c FROM filter_matches WHERE last_seen >= ? AND notified=1",
            (since,),
        ).fetchone()["c"]
        matches_pending = con.execute(
            "SELECT COUNT(*) AS c FROM filter_matches WHERE is_new=1 OR notified=0",
        ).fetchone()["c"]

        attempts = con.execute(
            "SELECT status, COUNT(*) AS c, COALESCE(SUM(sent_count), 0) AS sent_total "
            "FROM notification_attempts WHERE created_at >= ? GROUP BY status",
            (since,),
        ).fetchall()
        notifications_by_status = {row["status"]: int(row["c"]) for row in attempts}
        notifications_sent_total = sum(int(row["sent_total"]) for row in attempts)

        actions_rows = con.execute(
            "SELECT action, COUNT(*) AS c FROM job_actions WHERE created_at >= ? GROUP BY action",
            (since,),
        ).fetchall()
        actions_by_type = {row["action"]: int(row["c"]) for row in actions_rows}

        per_filter_rows = con.execute(
            "SELECT sf.id AS filter_id, sf.name AS filter_name, "
            "SUM(CASE WHEN fm.is_new=1 THEN 1 ELSE 0 END) AS new_count, "
            "SUM(CASE WHEN fm.notified=0 THEN 1 ELSE 0 END) AS pending_notify_count, "
            "SUM(CASE WHEN fm.notified=1 THEN 1 ELSE 0 END) AS notified_count "
            "FROM saved_filters sf "
            "LEFT JOIN filter_matches fm ON fm.filter_id=sf.id "
            "GROUP BY sf.id, sf.name "
            "ORDER BY sf.id ASC"
        ).fetchall()

    return {
        "window_days": days,
        "since": since,
        "jobs_new": int(jobs_new),
        "saved_filters_total": int(filters_total),
        "saved_filters_active": int(filters_active),
        "matches_new": int(matches_new),
        "matches_notified": int(matches_notified),
        "matches_pending": int(matches_pending),
        "notifications": {
            "attempts_by_status": notifications_by_status,
            "sent_jobs_total": int(notifications_sent_total),
        },
        "actions_by_type": actions_by_type,
        "matches_per_filter": [
            {
                "filter_id": int(r["filter_id"]),
                "filter_name": r["filter_name"],
                "new_count": int(r["new_count"] or 0),
                "pending_notify_count": int(r["pending_notify_count"] or 0),
                "notified_count": int(r["notified_count"] or 0),
            }
            for r in per_filter_rows
        ],
    }


@app.get("/jobs/enriched")
def list_enriched_jobs(
    db_path: str = Query("data/jobintel.sqlite"),
    role_family: str | None = None,
    seniority: str | None = None,
    location_type: str | None = None,
    country: str | None = None,
    skill: str | None = None,
    source: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []

    if role_family:
        where.append("e.role_family = ?")
        params.append(role_family)
    if seniority:
        where.append("e.seniority = ?")
        params.append(seniority)
    if location_type:
        where.append("e.location_type = ?")
        params.append(location_type)
    if country:
        where.append("e.country = ?")
        params.append(country)
    if source:
        where.append("s.source = ?")
        params.append(source)
    if skill:
        where.append("e.skills_json LIKE ?")
        params.append(f'%"{skill.lower()}"%')

    sql = (
        "SELECT s.company, s.title, s.url, s.source, s.location, s.remote, s.published_at, "
        "e.role_family, e.seniority, e.location_type, e.country, e.skills_json "
        "FROM seen_jobs s "
        "JOIN jobs_enriched e ON e.fingerprint = s.fingerprint"
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY s.first_seen DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with _connect(db_path) as con:
        _ensure_columns(con)
        _ensure_enriched_table(con)
        rows = con.execute(sql, params).fetchall()

    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "company": r["company"],
                "title": r["title"],
                "url": r["url"],
                "source": r["source"],
                "location": r["location"],
                "remote": None if r["remote"] is None else bool(r["remote"]),
                "published_at": r["published_at"],
                "role_family": r["role_family"],
                "seniority": r["seniority"],
                "location_type": r["location_type"],
                "country": r["country"],
                "skills": json.loads(r["skills_json"] or "[]"),
            }
        )
    return out
