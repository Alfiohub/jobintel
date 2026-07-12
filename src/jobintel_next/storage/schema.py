from __future__ import annotations


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS jobs_indexed (
    url TEXT PRIMARY KEY,
    source TEXT,
    source_org TEXT,
    company_name TEXT,
    title_raw TEXT,
    title_clean TEXT,
    normalized_title TEXT,
    role_family TEXT,
    classification_status TEXT,
    match_method TEXT,
    confidence REAL,
    language_bucket TEXT,
    language_reason TEXT,
    language_code TEXT,
    language_confidence REAL,
    published_at TEXT,
    updated_at TEXT,
    seniority TEXT,
    employment_type TEXT,
    location_type TEXT,
    city TEXT,
    region TEXT,
    country TEXT,
    salary_min REAL,
    salary_max REAL,
    salary_currency TEXT,
    salary_period TEXT,
    has_salary INTEGER NOT NULL DEFAULT 0,
    has_skills INTEGER NOT NULL DEFAULT 0,
    has_location INTEGER NOT NULL DEFAULT 0,
    title_is_other INTEGER NOT NULL DEFAULT 0,
    skills_json TEXT NOT NULL DEFAULT '[]'
);
"""


INDEX_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_jobs_normalized_title ON jobs_indexed(normalized_title);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_role_family ON jobs_indexed(role_family);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_language_bucket ON jobs_indexed(language_bucket);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_location_type ON jobs_indexed(location_type);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_employment_type ON jobs_indexed(employment_type);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_has_salary ON jobs_indexed(has_salary);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_has_skills ON jobs_indexed(has_skills);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_title_is_other ON jobs_indexed(title_is_other);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_salary_currency ON jobs_indexed(salary_currency);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_published_at ON jobs_indexed(published_at);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_updated_at ON jobs_indexed(updated_at);",
]


def create_schema_sql() -> list[str]:
    return [CREATE_TABLE_SQL, *INDEX_SQL]
