from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from .schema import create_schema_sql


INSERT_SQL = """
INSERT OR REPLACE INTO jobs_indexed (
    url, source, source_org, company_name, title_raw, title_clean,
    normalized_title, role_family, classification_status, match_method, confidence,
    language_bucket, language_reason, language_code, language_confidence,
    published_at, updated_at, seniority, employment_type, location_type,
    city, region, country, salary_min, salary_max, salary_currency, salary_period,
    has_salary, has_skills, has_location, title_is_other, skills_json
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
);
"""


def _bool_int(value: Any) -> int:
    return 1 if bool(value) else 0


def _skills_json(value: Any) -> str:
    if isinstance(value, list):
        cleaned = sorted({str(x).strip().lower() for x in value if str(x).strip()})
        return json.dumps(cleaned, ensure_ascii=False)
    return "[]"


def _row_tuple(obj: dict[str, Any]) -> tuple:
    return (
        obj.get("url"),
        obj.get("source"),
        obj.get("source_org"),
        obj.get("company_name"),
        obj.get("title_raw"),
        obj.get("title_clean"),
        obj.get("normalized_title"),
        obj.get("role_family"),
        obj.get("classification_status"),
        obj.get("match_method"),
        obj.get("confidence"),
        obj.get("language_bucket"),
        obj.get("language_reason"),
        obj.get("language_code"),
        obj.get("language_confidence"),
        obj.get("published_at"),
        obj.get("updated_at"),
        obj.get("seniority"),
        obj.get("employment_type"),
        obj.get("location_type"),
        obj.get("city"),
        obj.get("region"),
        obj.get("country"),
        obj.get("salary_min"),
        obj.get("salary_max"),
        obj.get("salary_currency"),
        obj.get("salary_period"),
        _bool_int(obj.get("has_salary")),
        _bool_int(obj.get("has_skills")),
        _bool_int(obj.get("has_location")),
        _bool_int(obj.get("title_is_other")),
        _skills_json(obj.get("skills")),
    )


def build_sqlite_index(
    *,
    input_path: str | Path,
    sqlite_path: str | Path,
    batch_size: int = 2000,
) -> dict[str, Any]:
    in_path = Path(input_path)
    db_path = Path(sqlite_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    rows_total = 0
    invalid_rows = 0
    inserted_rows = 0

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("DROP TABLE IF EXISTS jobs_indexed;")
        for sql in create_schema_sql():
            conn.execute(sql)

        batch: list[tuple] = []
        with in_path.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    obj = json.loads(s)
                except json.JSONDecodeError:
                    invalid_rows += 1
                    continue
                if not isinstance(obj, dict) or not str(obj.get("url") or "").strip():
                    invalid_rows += 1
                    continue
                rows_total += 1
                batch.append(_row_tuple(obj))
                if len(batch) >= batch_size:
                    conn.executemany(INSERT_SQL, batch)
                    inserted_rows += len(batch)
                    batch = []
        if batch:
            conn.executemany(INSERT_SQL, batch)
            inserted_rows += len(batch)

        conn.commit()
    finally:
        conn.close()

    return {
        "input_path": str(in_path),
        "sqlite_path": str(db_path),
        "rows_total": rows_total,
        "invalid_rows": invalid_rows,
        "inserted_rows": inserted_rows,
    }
