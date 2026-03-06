from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = """
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
CREATE INDEX IF NOT EXISTS idx_jobs_enriched_role_family ON jobs_enriched(role_family);
CREATE INDEX IF NOT EXISTS idx_jobs_enriched_seniority ON jobs_enriched(seniority);
CREATE INDEX IF NOT EXISTS idx_jobs_enriched_location_type ON jobs_enriched(location_type);
CREATE INDEX IF NOT EXISTS idx_jobs_enriched_country ON jobs_enriched(country);
"""


SKILL_PATTERNS: dict[str, str] = {
    r"\bpython\b": "python",
    r"\bsql\b": "sql",
    r"\bpostgres(ql)?\b": "postgresql",
    r"\bjava(script)?\b": "javascript",
    r"\btypescript\b": "typescript",
    r"\breact\b": "react",
    r"\bnode(\.js)?\b": "nodejs",
    r"\baws\b": "aws",
    r"\bazure\b": "azure",
    r"\bgcp\b|\bgoogle cloud\b": "gcp",
    r"\bdocker\b": "docker",
    r"\bkubernetes\b|\bk8s\b": "kubernetes",
    r"\bmachine learning\b|\bml\b": "machine_learning",
    r"\bai\b|\bartificial intelligence\b|\bartificialintelligence\b": "ai",
    r"\bdevops\b": "devops",
    r"\bdata\b": "data",
    r"\bsecurity\b": "security",
    r"\bbackend\b": "backend",
    r"\bfrontend\b|\bfront end\b": "frontend",
    r"\bandroid\b": "android",
    r"\bios\b": "ios",
}

ROLE_FAMILY_PATTERNS: list[tuple[str, str]] = [
    (r"\bdata\b|\banalyst\b|\bscientist\b|\banalytics\b", "data"),
    (r"\bsoftware\b|\bengineer\b|\bdeveloper\b|\bdevops\b|\bsre\b", "engineering"),
    (r"\bproduct\b", "product"),
    (r"\bdesign(er)?\b|\bux\b|\bui\b", "design"),
    (r"\bsales\b|\baccount executive\b|\bbdr\b|\bsdr\b", "sales"),
    (r"\bmarketing\b|\bgrowth\b", "marketing"),
    (r"\boperations\b|\bprogram\b|\bproject\b", "operations"),
    (r"\bfinance\b|\baccounting\b|\bfp&a\b", "finance"),
    (r"\brecruit(er|ing)\b|\bhr\b|\bpeople\b|\btalent\b", "people"),
    (r"\bcustomer success\b|\bcsm\b|\bsupport\b", "customer"),
    (r"\bdoctor\b|\bnurse\b|\btherapist\b|\bclinical\b", "healthcare"),
    (r"\blegal\b|\bcounsel\b|\bcompliance\b", "legal"),
]

SENIORITY_PATTERNS: list[tuple[str, str]] = [
    (r"\bintern(ship)?\b", "intern"),
    (r"\bjunior\b|\bjr\b", "junior"),
    (r"\bassociate\b", "associate"),
    (r"\bsenior\b|\bsr\b", "senior"),
    (r"\bstaff\b", "staff"),
    (r"\bprincipal\b", "principal"),
    (r"\blead\b", "lead"),
    (r"\bmanager\b", "manager"),
    (r"\bdirector\b", "director"),
    (r"\bhead\b", "head"),
    (r"\bvp\b|\bvice president\b", "vp"),
    (r"\bchief\b|\bcxo\b|\bceo\b|\bcto\b|\bcfo\b", "executive"),
]

COUNTRY_PATTERNS: list[tuple[str, str]] = [
    (r"\bunited states\b|\busa\b|\bus\b", "US"),
    (r"\bunited kingdom\b|\buk\b", "GB"),
    (r"\bcanada\b", "CA"),
    (r"\bindia\b", "IN"),
    (r"\bgermany\b", "DE"),
    (r"\bfrance\b", "FR"),
    (r"\bitaly\b", "IT"),
    (r"\bspain\b", "ES"),
    (r"\bireland\b", "IE"),
    (r"\bnetherlands\b", "NL"),
    (r"\bpoland\b", "PL"),
    (r"\bbrazil\b|\bbrasil\b", "BR"),
    (r"\bmexico\b", "MX"),
    (r"\bjapan\b", "JP"),
    (r"\bsingapore\b", "SG"),
    (r"\baustralia\b", "AU"),
]


def _norm_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip().lower()


def _extract_skills(text: str) -> list[str]:
    out: set[str] = set()
    for pattern, label in SKILL_PATTERNS.items():
        if re.search(pattern, text):
            out.add(label)
    return sorted(out)


def _extract_first(text: str, rules: list[tuple[str, str]], default: str | None = None) -> str | None:
    for pattern, label in rules:
        if re.search(pattern, text):
            return label
    return default


def _location_type(location_text: str, remote: int | None) -> str:
    if remote == 1 or re.search(r"\bremote\b|\bhome based\b|\bwork from home\b|\banywhere\b", location_text):
        return "remote"
    if re.search(r"\bhybrid\b", location_text):
        return "hybrid"
    return "onsite"


def enrich(db_path: Path, batch_size: int) -> tuple[int, int]:
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")

    updated = 0
    scanned = 0
    now = datetime.now(timezone.utc).isoformat()

    con = sqlite3.connect(str(db_path))
    try:
        con.executescript(SCHEMA)

        rows = con.execute("SELECT fingerprint, title, location, remote FROM seen_jobs")

        payload: list[tuple[str, str | None, str | None, str, str | None, str, str, str]] = []
        for fp, title, location, remote in rows:
            scanned += 1
            title_n = _norm_text(title)
            location_n = _norm_text(location)
            merged = f"{title_n} {location_n}".strip()

            role_family = _extract_first(merged, ROLE_FAMILY_PATTERNS, default="other")
            seniority = _extract_first(title_n, SENIORITY_PATTERNS, default="unknown")
            country = _extract_first(location_n, COUNTRY_PATTERNS)
            location_type = _location_type(location_n, remote)
            skills = _extract_skills(merged)

            payload.append(
                (
                    fp,
                    role_family,
                    seniority,
                    location_type,
                    country,
                    json.dumps(skills, ensure_ascii=True),
                    title_n,
                    now,
                )
            )

            if len(payload) >= batch_size:
                con.executemany(
                    "INSERT OR REPLACE INTO jobs_enriched"
                    "(fingerprint, role_family, seniority, location_type, country, skills_json, normalized_title, updated_at) "
                    "VALUES(?,?,?,?,?,?,?,?)",
                    payload,
                )
                updated += len(payload)
                payload.clear()

        if payload:
            con.executemany(
                "INSERT OR REPLACE INTO jobs_enriched"
                "(fingerprint, role_family, seniority, location_type, country, skills_json, normalized_title, updated_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                payload,
            )
            updated += len(payload)

        con.commit()
    finally:
        con.close()

    return scanned, updated


def main() -> None:
    ap = argparse.ArgumentParser(description="Build jobs_enriched table from seen_jobs.")
    ap.add_argument("--db", default="data/jobintel.sqlite")
    ap.add_argument("--batch-size", type=int, default=2000)
    args = ap.parse_args()

    scanned, updated = enrich(Path(args.db), batch_size=max(1, args.batch_size))
    print(f"DB: {args.db}")
    print(f"Rows scanned: {scanned}")
    print(f"Rows upserted: {updated}")


if __name__ == "__main__":
    main()
