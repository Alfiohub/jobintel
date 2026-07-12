PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS seen_jobs (
  fingerprint TEXT PRIMARY KEY,
  dedup_key TEXT,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  score INTEGER NOT NULL,
  source TEXT NOT NULL,
  company TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  location TEXT,
  remote INTEGER,
  published_at TEXT,
  notified INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS jobs_enriched (
  fingerprint TEXT PRIMARY KEY,
  role_family TEXT,
  seniority TEXT,
  location_type TEXT,
  country TEXT,
  skills_json TEXT NOT NULL,
  normalized_title TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (fingerprint) REFERENCES seen_jobs(fingerprint) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS saved_filters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  criteria_json TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS filter_matches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filter_id INTEGER NOT NULL,
  fingerprint TEXT NOT NULL,
  score INTEGER NOT NULL,
  reasons_json TEXT NOT NULL,
  matched_at TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  is_new INTEGER NOT NULL DEFAULT 1,
  notified INTEGER NOT NULL DEFAULT 0,
  UNIQUE(filter_id, fingerprint)
);

CREATE TABLE IF NOT EXISTS job_actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  action TEXT NOT NULL,
  filter_id INTEGER,
  metadata_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_targets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filter_id INTEGER NOT NULL,
  webhook_url TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(filter_id, webhook_url)
);

CREATE TABLE IF NOT EXISTS notification_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filter_id INTEGER NOT NULL,
  webhook_url TEXT NOT NULL,
  status TEXT NOT NULL,
  http_status INTEGER,
  sent_count INTEGER NOT NULL DEFAULT 0,
  error TEXT,
  created_at TEXT NOT NULL
);
