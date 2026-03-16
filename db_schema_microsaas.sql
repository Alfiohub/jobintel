PRAGMA foreign_keys = ON;

-- 1) Raw ingestion: source payload as-is
CREATE TABLE IF NOT EXISTS raw_jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,                -- greenhouse | lever | smartrecruiters | ...
  source_job_id TEXT,                  -- provider-native id
  source_org TEXT,                     -- board/company slug
  url TEXT NOT NULL,
  title_raw TEXT,
  company_raw TEXT,
  location_raw TEXT,
  description_raw TEXT,
  language_hint TEXT,
  payload_json TEXT NOT NULL,          -- untouched source payload
  fetched_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_raw_jobs_source_url
  ON raw_jobs(source, url);
CREATE INDEX IF NOT EXISTS ix_raw_jobs_source_job_id
  ON raw_jobs(source, source_job_id);

-- 2) Cleaned text + dedup hash
CREATE TABLE IF NOT EXISTS jobs_clean (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  raw_job_id INTEGER NOT NULL,
  title_clean TEXT NOT NULL,
  description_clean TEXT NOT NULL,
  requirements_clean TEXT,
  responsibilities_clean TEXT,
  location_clean TEXT,
  language TEXT,
  content_hash TEXT NOT NULL,          -- sha256(title+core text)
  content_fingerprint TEXT,            -- optional near-dup (simhash/minhash)
  cleaned_at TEXT NOT NULL,
  FOREIGN KEY (raw_job_id) REFERENCES raw_jobs(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_jobs_clean_raw_job_id
  ON jobs_clean(raw_job_id);
CREATE INDEX IF NOT EXISTS ix_jobs_clean_content_hash
  ON jobs_clean(content_hash);

-- 3) Indexed records consumed by search API
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
  taxonomy_source TEXT,
  taxonomy_code TEXT,
  taxonomy_label TEXT,
  taxonomy_match_confidence REAL,
  seniority TEXT,
  employment_type TEXT,
  location_type TEXT,                  -- remote | hybrid | onsite
  city TEXT,
  region TEXT,
  country TEXT,
  salary_min INTEGER,
  salary_max INTEGER,
  salary_currency TEXT,
  experience_years_min INTEGER,
  experience_years_max INTEGER,
  experience_required INTEGER,         -- 0/1
  experience_text_raw TEXT,
  education_level TEXT,                -- none | high_school | bachelor | master | phd | unspecified
  degree_required INTEGER,             -- 0/1
  education_text_raw TEXT,
  skills_json TEXT NOT NULL DEFAULT '[]',
  tags_json TEXT NOT NULL DEFAULT '{}',
  embedding_json TEXT,                 -- keep JSON array in SQLite prototype
  embedding_model TEXT,
  content_hash TEXT,
  processing_state TEXT,               -- new | processed | updated | skipped | failed
  first_seen_at TEXT,
  last_seen_at TEXT,
  processing_version TEXT,
  extraction_version TEXT,
  tagger_version TEXT,
  title_confidence REAL,
  location_confidence REAL,
  salary_confidence REAL,
  experience_confidence REAL,
  education_confidence REAL,
  tag_confidence REAL,
  indexed_at TEXT NOT NULL,
  FOREIGN KEY (clean_job_id) REFERENCES jobs_clean(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_jobs_indexed_clean_job_id
  ON jobs_indexed(clean_job_id);
CREATE INDEX IF NOT EXISTS ix_jobs_indexed_normalized_title
  ON jobs_indexed(normalized_title);
CREATE INDEX IF NOT EXISTS ix_jobs_indexed_role_family
  ON jobs_indexed(role_family);
CREATE INDEX IF NOT EXISTS ix_jobs_indexed_location_type
  ON jobs_indexed(location_type);
CREATE INDEX IF NOT EXISTS ix_jobs_indexed_seniority
  ON jobs_indexed(seniority);
CREATE INDEX IF NOT EXISTS ix_jobs_indexed_employment_type
  ON jobs_indexed(employment_type);

-- 4) Cache by content hash to avoid re-calling expensive stages
CREATE TABLE IF NOT EXISTS extraction_cache (
  content_hash TEXT PRIMARY KEY,
  normalized_title TEXT,
  role_family TEXT,
  occupation_group TEXT,
  taxonomy_source TEXT,
  taxonomy_code TEXT,
  taxonomy_label TEXT,
  taxonomy_match_confidence REAL,
  seniority TEXT,
  employment_type TEXT,
  location_type TEXT,
  city TEXT,
  region TEXT,
  country TEXT,
  salary_min INTEGER,
  salary_max INTEGER,
  salary_currency TEXT,
  experience_years_min INTEGER,
  experience_years_max INTEGER,
  experience_required INTEGER,         -- 0/1
  experience_text_raw TEXT,
  education_level TEXT,                -- none | high_school | bachelor | master | phd | unspecified
  degree_required INTEGER,             -- 0/1
  education_text_raw TEXT,
  skills_json TEXT NOT NULL DEFAULT '[]',
  tags_json TEXT NOT NULL DEFAULT '{}',
  embedding_json TEXT,
  embedding_model TEXT,
  tagger_version TEXT,
  title_confidence REAL,
  location_confidence REAL,
  salary_confidence REAL,
  experience_confidence REAL,
  education_confidence REAL,
  tag_confidence REAL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- 5) Pipeline run history (incremental observability)
CREATE TABLE IF NOT EXISTS pipeline_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL UNIQUE,
  input_path TEXT NOT NULL,
  output_dir TEXT NOT NULL,
  db_path TEXT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  duration_seconds REAL,
  total_rows INTEGER NOT NULL DEFAULT 0,
  processed INTEGER NOT NULL DEFAULT 0,
  skipped INTEGER NOT NULL DEFAULT 0,
  updated INTEGER NOT NULL DEFAULT 0,
  failed INTEGER NOT NULL DEFAULT 0,
  cache_hits INTEGER NOT NULL DEFAULT 0,
  pipeline_version TEXT,
  extraction_version TEXT
);
