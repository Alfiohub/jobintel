from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3

import yaml


ROLE_HINTS = {
    "engineer",
    "developer",
    "analyst",
    "architect",
    "designer",
    "manager",
    "director",
    "consultant",
    "specialist",
    "scientist",
    "technician",
    "coordinator",
    "executive",
    "associate",
    "representative",
}

SKILL_HINTS = {
    "python",
    "sql",
    "postgres",
    "postgresql",
    "javascript",
    "typescript",
    "android",
    "ios",
    "backend",
    "frontend",
    "devops",
    "cloud",
    "security",
    "infrastructure",
    "machine learning",
    "artificialintelligence",
    "site reliability",
    "full stack",
}

LOCATION_HINTS = {
    "united",
    "states",
    "usa",
    "us",
    "uk",
    "canada",
    "india",
    "london",
    "berlin",
    "paris",
    "tokyo",
    "singapore",
    "austin",
    "seattle",
    "boston",
    "chicago",
    "toronto",
    "amsterdam",
    "emea",
    "california",
    "texas",
    "florida",
    "washington",
    "ny",
    "ca",
    "tx",
    "wa",
    "ma",
    "nc",
}

NOISE_HINTS = {
    "of",
    "or",
    "in",
    "de",
    "co",
    "it",
    "ii",
    "sr.",
    "2026",
    "based",
    "city",
    "area",
    "global",
}


def _load_keywords(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    unigrams = (((data.get("keywords") or {}).get("top_unigrams")) or [])
    bigrams = (((data.get("keywords") or {}).get("top_bigrams")) or [])
    out: list[dict] = []
    for x in unigrams + bigrams:
        if isinstance(x, dict) and isinstance(x.get("keyword"), str):
            out.append({"keyword": x["keyword"].strip().lower(), "count": int(x.get("count") or 0)})
    return out


def _load_company_tokens(db_path: Path) -> set[str]:
    if not db_path.exists():
        return set()

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute("select distinct lower(company) from seen_jobs where company is not null and company != ''")
        return {str(r[0]).strip() for r in cur.fetchall() if isinstance(r[0], str) and r[0].strip()}
    finally:
        conn.close()


def _classify(keyword: str, company_tokens: set[str]) -> str:
    if keyword in company_tokens:
        return "company_tokens"
    if keyword in NOISE_HINTS:
        return "noise"
    if keyword in SKILL_HINTS:
        return "skills"
    if keyword in LOCATION_HINTS:
        return "locations"
    if keyword in ROLE_HINTS:
        return "roles"

    # Phrase heuristics
    if any(h in keyword for h in ("engineer", "analyst", "architect", "designer", "manager", "consultant")):
        return "roles"
    if any(h in keyword for h in ("python", "sql", "android", "ios", "machine learning", "site reliability")):
        return "skills"
    if any(h in keyword for h in ("united", "usa", "uk", "london", "berlin", "tokyo", "city", "california", "texas")):
        return "locations"

    return "noise"


def _dedup_keep_max(items: list[dict]) -> list[dict]:
    best: dict[str, int] = {}
    for x in items:
        k = x["keyword"]
        c = int(x["count"])
        best[k] = max(best.get(k, 0), c)
    return [{"keyword": k, "count": c} for k, c in sorted(best.items(), key=lambda kv: (-kv[1], kv[0]))]


def main() -> None:
    ap = argparse.ArgumentParser(description="Classify extracted keywords into roles/skills/locations/company_tokens/noise.")
    ap.add_argument("--input", default="config/generated/keywords.yml")
    ap.add_argument("--output", default="config/generated/keyword_groups.yml")
    ap.add_argument("--db", default="data/jobintel.sqlite")
    args = ap.parse_args()

    rows = _load_keywords(Path(args.input))
    company_tokens = _load_company_tokens(Path(args.db))
    groups = {"roles": [], "skills": [], "locations": [], "company_tokens": [], "noise": []}

    for row in rows:
        grp = _classify(row["keyword"], company_tokens)
        groups[grp].append(row)

    for k in groups:
        groups[k] = _dedup_keep_max(groups[k])

    payload = {
        "meta": {
            "input": args.input,
            "total_keywords": len(rows),
        },
        "groups": groups,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"Wrote {out}")
    print(f"roles: {len(groups['roles'])}")
    print(f"skills: {len(groups['skills'])}")
    print(f"locations: {len(groups['locations'])}")
    print(f"company_tokens: {len(groups['company_tokens'])}")
    print(f"noise: {len(groups['noise'])}")


if __name__ == "__main__":
    main()
