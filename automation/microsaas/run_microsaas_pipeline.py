from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

try:
    from automation.microsaas.title_normalization import normalize_title as _normalize_title
except ModuleNotFoundError:
    from title_normalization import normalize_title as _normalize_title

try:
    from automation.microsaas.tag_extraction import (
        extract_location_type as _extract_location_type_mod,
        extract_salary as _extract_salary_mod,
        extract_tags as _extract_tags_mod,
    )
except ModuleNotFoundError:
    from tag_extraction import (
        extract_location_type as _extract_location_type_mod,
        extract_salary as _extract_salary_mod,
        extract_tags as _extract_tags_mod,
    )


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_BR_RE = re.compile(r"(?i)<br\s*/?>")
_BLOCK_CLOSE_RE = re.compile(r"(?i)</p>|</div>|</li>|</h[1-6]>")

SKILL_PATTERNS: dict[str, str] = {
    r"\bpython\b": "python",
    r"\bsql\b": "sql",
    r"\bpostgres(?:ql)?\b": "postgresql",
    r"\bmysql\b": "mysql",
    r"\bsnowflake\b": "snowflake",
    r"\bbigquery\b": "bigquery",
    r"\bdbt\b": "dbt",
    r"\bspark\b": "spark",
    r"\bairflow\b": "airflow",
    r"\bdatabricks\b": "databricks",
    r"\baws\b": "aws",
    r"\bazure\b": "azure",
    r"\bgcp\b|\bgoogle cloud\b": "gcp",
    r"\bdocker\b": "docker",
    r"\bkubernetes\b|\bk8s\b": "kubernetes",
    r"\bterraform\b": "terraform",
    r"\bexcel\b": "excel",
    r"\btableau\b": "tableau",
    r"\bpower\s?bi\b": "power_bi",
    r"\breact\b": "react",
    r"\bnode(?:\.js)?\b": "nodejs",
    r"\btypescript\b": "typescript",
    r"\bjavascript\b": "javascript",
    r"\bjava\b": "java",
    r"\bmachine learning\b": "machine_learning",
    r"\bllm\b|\blarge language model": "llm",
}

SENIORITY_PATTERNS: list[tuple[str, str]] = [
    (r"\bintern(?:ship)?\b", "intern"),
    (r"\bjunior\b|\bjr\.?\b", "junior"),
    (r"\bassociate\b", "associate"),
    (r"\bsenior\b|\bsr\.?\b", "senior"),
    (r"\bstaff\b", "staff"),
    (r"\bprincipal\b", "principal"),
    (r"\blead\b", "lead"),
    (r"\bmanager\b", "manager"),
    (r"\bdirector\b", "director"),
    (r"\bhead\b", "head"),
    (r"\bvp\b|\bvice president\b", "vp"),
]

TITLE_RULES: list[tuple[str, str, str, str]] = [
    (r"\binterested in joining our team\b|\bgeneral application\b", "general_application", "recruiting", "hr"),
    (r"\bfield cto\b|\bchief technology officer\b|\bcto\b", "chief_technology_officer", "executive_leadership", "business"),
    (r"\bprincipal enterprise architect\b|\benterprise architect\b", "enterprise_architect", "architecture", "engineering"),
    (r"\bsolutions architect\b", "solutions_architect", "architecture", "engineering"),
    (r"\baccount executive\b", "account_executive", "sales", "business"),
    (r"\bstrategic accounts?\b|\bclient value partner\b", "account_manager", "sales", "business"),
    (r"\baccount management\b|\baccount manager\b", "account_manager", "sales", "business"),
    (r"\bbusiness development representative\b|\bbdr\b", "business_development_representative", "sales", "business"),
    (r"\bsales development representative\b|\bsdr\b", "business_development_representative", "sales", "business"),
    (r"\bchief revenue officer\b|\bcro\b", "chief_revenue_officer", "executive_leadership", "business"),
    (r"\bhead of industry\b|\bindustry lead\b", "industry_lead", "sales", "business"),
    (r"\bsales\b", "sales_representative", "sales", "business"),
    (r"\bbusiness analyst\b|\bba\s*-", "business_analyst", "business_analysis", "business"),
    (r"\bcorporate development\b", "corporate_development", "strategy", "business"),
    (r"\btechnical recruiter\b", "technical_recruiter", "recruiting", "hr"),
    (r"\bexecutive search lead\b", "technical_recruiter", "recruiting", "hr"),
    (r"\bhr business partner\b|\bpeople business partner\b|\bhrbp\b", "hr_business_partner", "hr", "hr"),
    (r"\bhr generalist\b", "hr_generalist", "hr", "hr"),
    (r"\bimplementation consultant\b", "implementation_consultant", "consulting", "business"),
    (r"\bmanagement consultant\b|\bsenior consultant\b|\blead consultant\b|\bconsultant\b", "consultant", "consulting", "business"),
    (r"\binstallations specialist\b", "implementation_consultant", "consulting", "business"),
    (r"\binstall coordinator\b", "implementation_coordinator", "consulting", "business"),
    (r"\bai coach\b|\bagile coach\b", "consultant", "consulting", "business"),
    (r"\bai governance\b|\bai transformation\b|\bai delivery lead\b|\bmanaging principal\b", "consultant", "consulting", "business"),
    (r"\binvestment analyst\b", "investment_analyst", "finance", "finance"),
    (r"\baccountant\b|\bcontroller\b|\bauditor\b", "accountant", "finance", "finance"),
    (r"\bcommissions analyst\b|\bpricing analyst\b", "financial_analyst", "finance", "finance"),
    (r"\bstrategic finance\b|\bfinancial analyst\b|\bfinance analyst\b", "financial_analyst", "finance", "finance"),
    (r"\bcounsel\b|\battorney\b|\blegal\b", "legal_counsel", "legal", "business"),
    (r"\bcustomer success\b", "customer_success_manager", "customer_success", "business"),
    (r"\brole readiness specialist\b|\bwinback specialist\b", "customer_success_manager", "customer_success", "business"),
    (r"\bclient services?\b|\btechnical account management\b", "customer_success_manager", "customer_success", "business"),
    (r"\bdata analytics director\b|\bdirector of data analytics\b", "analytics_director", "data_analytics", "data"),
    (r"\banalytics director\b", "analytics_director", "data_analytics", "data"),
    (r"\bdata analytics manager\b|\banalytics manager\b", "analytics_manager", "data_analytics", "data"),
    (r"\banalytics engineer\b", "analytics_engineer", "data_analytics", "data"),
    (r"\bbusiness intelligence analyst\b|\bbi analyst\b", "business_intelligence_analyst", "data_analytics", "data"),
    (r"\bbusiness intelligence engineer\b|\bbi engineer\b", "business_intelligence_engineer", "data_analytics", "data"),
    (r"\bdata analyst\b|\banalyst, data\b", "data_analyst", "data_analytics", "data"),
    (r"\bdata engineer\b", "data_engineer", "data_engineering", "data"),
    (r"\bdata scientist\b", "data_scientist", "data_science", "data"),
    (r"\bmachine learning scientist\b|\bml scientist\b", "ml_scientist", "machine_learning", "data"),
    (r"\bmachine learning engineer\b|\bml engineer\b", "ml_engineer", "machine_learning", "data"),
    (r"\bai (technical )?architect\b|\bai deployment architect\b", "enterprise_architect", "architecture", "engineering"),
    (r"\bbackend engineer\b|\bbackend developer\b", "backend_engineer", "backend", "engineering"),
    (r"\bfrontend engineer\b|\bfrontend developer\b", "frontend_engineer", "frontend", "engineering"),
    (r"\bfull[ -]?stack engineer\b|\bfull[ -]?stack developer\b", "fullstack_engineer", "fullstack", "engineering"),
    (r"\bdevops\b", "devops_engineer", "devops", "engineering"),
    (r"\bsite reliability\b|\bsre\b", "site_reliability_engineer", "sre", "engineering"),
    (r"\bsoftware engineer\b|\bsoftware developer\b", "software_engineer", "software_engineering", "engineering"),
    (r"\bproduct manager\b|\bproduct management\b", "product_manager", "product_management", "product"),
    (r"\btpm\b|\btechnical program manager\b", "technical_program_manager", "program_management", "product"),
    (r"\btechnology program analyst\b", "program_analyst", "program_management", "product"),
    (r"\bux designer\b|\bui designer\b|\bproduct designer\b|\bproduct design\b", "product_designer", "design", "design"),
    (r"\bcontent designer\b|\blearning designer\b", "content_designer", "design", "design"),
    (r"\bsalesforce administrator\b|\bnetsuite administrator\b|\bsystems administrator\b", "systems_administrator", "it_operations", "engineering"),
    (r"\boffice administrator\b|\bworkplace experience specialist\b", "office_administrator", "operations", "business"),
    (r"\bnetsuite analyst\b", "business_systems_analyst", "business_analysis", "business"),
    (r"\bworkforce management analyst\b", "operations_analyst", "operations", "business"),
    (r"\btalent development partner\b|\bpeople business partnerships?\b", "hr_business_partner", "hr", "hr"),
    (r"\btalent scientist\b|\btalent science\b", "talent_analytics_specialist", "hr", "hr"),
    (r"\bhead of talent development\b", "hr_manager", "hr", "hr"),
    (r"\btelehealth provider\b", "healthcare_provider", "healthcare", "business"),
    (r"\bsecurity .*systems specialist\b|\bdesktop systems specialist\b|\bit support specialist\b", "it_support_specialist", "it_operations", "engineering"),
    (r"\btechnical support\b", "it_support_specialist", "it_operations", "engineering"),
    (r"\balliances?\b", "alliance_manager", "partnerships", "business"),
    (r"\btechnical lead\b", "software_engineer", "software_engineering", "engineering"),
    (r"\btraining localization intern\b", "localization_intern", "operations", "business"),
    (r"\bseo\b", "seo_specialist", "marketing", "business"),
    (r"\bmarketing\b", "marketing_specialist", "marketing", "business"),
    (r"\brecruiter\b|\btalent acquisition\b", "technical_recruiter", "recruiting", "hr"),
    (r"\boperations specialist\b|\boperations coordinator\b", "operations_specialist", "operations", "business"),
]

SALARY_PATTERNS: list[str] = [
    r"(?:\$|EUR|GBP|CAD|AUD)\s?\d[\d,]*(?:\.\d+)?\s*[kmb]?\s?(?:-|to|–|—)\s?(?:\$|EUR|GBP|CAD|AUD)?\s?\d[\d,]*(?:\.\d+)?\s*[kmb]?(?:\s?(?:/|per)\s?(?:year|yr|hour|hr))?",
    r"\b\d[\d,]*(?:\.\d+)?\s*[kmb]?\s?(?:-|to|–|—)\s?\d[\d,]*(?:\.\d+)?\s*[kmb]?\s?(?:USD|EUR|GBP|CAD|AUD)\b",
]
_SALARY_POSITIVE_CONTEXT_RE = re.compile(
    r"\bsalary\b|\bcompensation\b|\bpay range\b|\bbase pay\b|\bbase salary\b|\bote\b|\bannual(?:ly)?\b|\bper year\b|\byearly\b|\bper hour\b|\bhourly\b",
    flags=re.IGNORECASE,
)
_SALARY_NEGATIVE_CONTEXT_RE = re.compile(
    r"\bbacked by\b|\braised\b|\bfunding\b|\bseries [a-z]\b|\bvaluation\b|\bpatients?\b|\bcustomers?\b|\busers?\b|\bemployees?\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class CleanRow:
    title_clean: str
    description_clean: str
    requirements_clean: str
    responsibilities_clean: str
    location_clean: str
    language: str
    content_hash: str
    content_fingerprint: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path, max_rows: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError as e:
                raise ValueError(f"invalid JSON at {path}:{line_no}: {e}") from e
            if isinstance(obj, dict):
                rows.append(obj)
                if max_rows is not None and len(rows) >= max_rows:
                    break
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _strip_html(text: str) -> str:
    plain = unescape(text)
    plain = _BR_RE.sub("\n", plain)
    plain = _BLOCK_CLOSE_RE.sub("\n", plain)
    plain = _HTML_TAG_RE.sub(" ", plain)
    plain = _WS_RE.sub(" ", plain)
    return plain.strip()


def _extract_description(row: dict[str, Any]) -> str:
    desc = str(row.get("description_text") or "").strip()
    if desc:
        return desc
    raw = row.get("raw_payload")
    if isinstance(raw, dict):
        content = raw.get("content")
        if isinstance(content, str) and content.strip():
            return _strip_html(content)
    return ""


def _extract_sections(text: str) -> tuple[str, str]:
    lowered = text.lower()
    req = ""
    resp = ""
    req_m = re.search(r"(requirements?|qualifications?)\s*:", lowered)
    resp_m = re.search(r"(responsibilities?|what you[’']?ll do)\s*:", lowered)
    if req_m:
        end = resp_m.start() if resp_m and resp_m.start() > req_m.start() else min(len(text), req_m.start() + 1800)
        req = text[req_m.start():end].strip()
    if resp_m:
        end = req_m.start() if req_m and req_m.start() > resp_m.start() else min(len(text), resp_m.start() + 1800)
        resp = text[resp_m.start():end].strip()
    return req, resp


def clean_row(row: dict[str, Any]) -> CleanRow:
    title_raw = str(row.get("title") or "").strip()
    location_raw = str(row.get("location_raw") or "").strip()
    description = _extract_description(row)
    req, resp = _extract_sections(description)
    language = str(row.get("language") or "").strip().lower() or "en"
    title_clean = _WS_RE.sub(" ", title_raw).strip()
    location_clean = _WS_RE.sub(" ", location_raw).strip()
    description_clean = _WS_RE.sub(" ", description).strip()
    hash_payload = f"{title_clean}|{location_clean}|{description_clean[:5000]}".lower()
    content_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()
    fingerprint_payload = f"{title_clean}|{description_clean[:800]}".lower()
    content_fingerprint = hashlib.sha1(fingerprint_payload.encode("utf-8")).hexdigest()[:20]
    return CleanRow(
        title_clean=title_clean,
        description_clean=description_clean,
        requirements_clean=req,
        responsibilities_clean=resp,
        location_clean=location_clean,
        language=language,
        content_hash=content_hash,
        content_fingerprint=content_fingerprint,
    )


def normalize_title(title_clean: str) -> tuple[str, str, str]:
    return _normalize_title(title_clean)


def _extract_seniority(text: str) -> str | None:
    for pattern, value in SENIORITY_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return value
    return None


def _extract_employment_type(text: str) -> str | None:
    if re.search(r"\bfull[ -]?time\b", text, flags=re.IGNORECASE):
        return "full_time"
    if re.search(r"\bpart[ -]?time\b", text, flags=re.IGNORECASE):
        return "part_time"
    if re.search(r"\bcontract(?:or)?\b|\bfreelance\b", text, flags=re.IGNORECASE):
        return "contract"
    if re.search(r"\bintern(?:ship)?\b", text, flags=re.IGNORECASE):
        return "internship"
    if re.search(r"\btemporary\b|\btemp\b", text, flags=re.IGNORECASE):
        return "temporary"
    return None


def _extract_location_type(text: str) -> str | None:
    return _extract_location_type_mod(text)


def _parse_salary_number(num_text: str) -> int | None:
    m = re.match(r"(?i)^\s*(\d[\d,]*(?:\.\d+)?)\s*([kmb])?\s*$", num_text)
    if not m:
        return None
    base = float(m.group(1).replace(",", ""))
    mult = (m.group(2) or "").lower()
    if mult == "k":
        base *= 1_000
    elif mult == "m":
        base *= 1_000_000
    elif mult == "b":
        base *= 1_000_000_000
    return int(base)


def _extract_salary(text: str) -> tuple[int | None, int | None, str | None]:
    return _extract_salary_mod(text)


def _extract_skills(text: str) -> list[str]:
    found: list[str] = []
    for pattern, skill in SKILL_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(skill)
    return sorted(set(found))


def _split_location(location_clean: str) -> tuple[str | None, str | None]:
    if not location_clean:
        return None, None
    parts = [p.strip() for p in location_clean.split(",") if p.strip()]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return parts[0], None


def extract_tags(clean: CleanRow, normalized_title: str) -> dict[str, Any]:
    return _extract_tags_mod(clean, normalized_title=normalized_title)


def fake_embedding(text: str, dim: int = 24) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    out: list[float] = []
    for i in range(dim):
        b = digest[i % len(digest)]
        out.append(round((float(b) / 127.5) - 1.0, 6))
    return out


def _embed_openai(text: str, model: str, timeout_s: int) -> list[float]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for --embedding-mode openai")
    payload = {
        "model": model,
        "input": text,
    }
    req = urlrequest.Request(
        "https://api.openai.com/v1/embeddings",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
    obj = json.loads(body)
    data = obj.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("OpenAI embeddings: invalid response data")
    embedding = data[0].get("embedding")
    if not isinstance(embedding, list):
        raise RuntimeError("OpenAI embeddings: missing embedding vector")
    return [float(x) for x in embedding]


def _embed_gemini(text: str, model: str, timeout_s: int) -> list[float]:
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is required for --embedding-mode gemini")
    payload = {
        "content": {
            "parts": [{"text": text}],
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={api_key}"
    req = urlrequest.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
    obj = json.loads(body)
    emb_obj = obj.get("embedding")
    if not isinstance(emb_obj, dict):
        raise RuntimeError("Gemini embeddings: invalid response embedding")
    values = emb_obj.get("values")
    if not isinstance(values, list):
        raise RuntimeError("Gemini embeddings: missing values vector")
    return [float(x) for x in values]


def compute_embedding(
    text: str,
    *,
    mode: str,
    openai_model: str,
    gemini_model: str,
    timeout_s: int,
) -> tuple[list[float] | None, str | None]:
    if mode == "none":
        return None, None
    if mode == "hash":
        return fake_embedding(text), "hash_v1"
    if mode == "openai":
        return _embed_openai(text, model=openai_model, timeout_s=timeout_s), openai_model
    if mode == "gemini":
        return _embed_gemini(text, model=gemini_model, timeout_s=timeout_s), gemini_model
    raise ValueError(f"unsupported embedding mode: {mode}")


def ensure_microsaas_schema(con: sqlite3.Connection) -> None:
    schema_path = Path("db_schema_microsaas.sql")
    con.executescript(schema_path.read_text(encoding="utf-8"))


def save_to_db(
    con: sqlite3.Connection,
    *,
    raw_row: dict[str, Any],
    clean: CleanRow,
    normalized_title: str,
    role_family: str,
    occupation_group: str,
    tags: dict[str, Any],
    embedding: list[float] | None,
    embedding_model: str | None,
) -> None:
    now = now_iso()
    con.execute(
        """
        INSERT OR IGNORE INTO raw_jobs(
          source, source_job_id, source_org, url, title_raw, company_raw, location_raw,
          description_raw, language_hint, payload_json, fetched_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            str(raw_row.get("source") or ""),
            str(raw_row.get("external_id") or raw_row.get("source_job_id") or ""),
            str(raw_row.get("source_org") or ""),
            str(raw_row.get("url") or ""),
            str(raw_row.get("title") or ""),
            str(raw_row.get("company_name") or ""),
            str(raw_row.get("location_raw") or ""),
            str(raw_row.get("description_text") or ""),
            clean.language,
            json.dumps(raw_row, ensure_ascii=False),
            now,
        ),
    )
    raw_id_row = con.execute(
        "SELECT id FROM raw_jobs WHERE source=? AND url=?",
        (str(raw_row.get("source") or ""), str(raw_row.get("url") or "")),
    ).fetchone()
    if raw_id_row is None:
        return
    raw_job_id = int(raw_id_row[0])

    con.execute(
        """
        INSERT INTO jobs_clean(
          raw_job_id, title_clean, description_clean, requirements_clean, responsibilities_clean,
          location_clean, language, content_hash, content_fingerprint, cleaned_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(raw_job_id) DO UPDATE SET
          title_clean=excluded.title_clean,
          description_clean=excluded.description_clean,
          requirements_clean=excluded.requirements_clean,
          responsibilities_clean=excluded.responsibilities_clean,
          location_clean=excluded.location_clean,
          language=excluded.language,
          content_hash=excluded.content_hash,
          content_fingerprint=excluded.content_fingerprint,
          cleaned_at=excluded.cleaned_at
        """,
        (
            raw_job_id,
            clean.title_clean,
            clean.description_clean,
            clean.requirements_clean,
            clean.responsibilities_clean,
            clean.location_clean,
            clean.language,
            clean.content_hash,
            clean.content_fingerprint,
            now,
        ),
    )
    clean_id_row = con.execute("SELECT id FROM jobs_clean WHERE raw_job_id=?", (raw_job_id,)).fetchone()
    if clean_id_row is None:
        return
    clean_job_id = int(clean_id_row[0])

    con.execute(
        """
        INSERT INTO extraction_cache(
          content_hash, normalized_title, role_family, occupation_group, seniority, employment_type,
          location_type, city, region, country, salary_min, salary_max, salary_currency,
          skills_json, tags_json, embedding_json, embedding_model, tagger_version, tag_confidence,
          created_at, updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(content_hash) DO UPDATE SET
          normalized_title=excluded.normalized_title,
          role_family=excluded.role_family,
          occupation_group=excluded.occupation_group,
          seniority=excluded.seniority,
          employment_type=excluded.employment_type,
          location_type=excluded.location_type,
          city=excluded.city,
          region=excluded.region,
          country=excluded.country,
          salary_min=excluded.salary_min,
          salary_max=excluded.salary_max,
          salary_currency=excluded.salary_currency,
          skills_json=excluded.skills_json,
          tags_json=excluded.tags_json,
          embedding_json=excluded.embedding_json,
          embedding_model=excluded.embedding_model,
          tagger_version=excluded.tagger_version,
          tag_confidence=excluded.tag_confidence,
          updated_at=excluded.updated_at
        """,
        (
            clean.content_hash,
            normalized_title,
            role_family,
            occupation_group,
            tags.get("seniority"),
            tags.get("employment_type"),
            tags.get("location_type"),
            tags.get("city"),
            tags.get("region"),
            tags.get("country"),
            tags.get("salary_min"),
            tags.get("salary_max"),
            tags.get("salary_currency"),
            json.dumps(tags.get("skills") or [], ensure_ascii=False),
            json.dumps(tags.get("tags") or {}, ensure_ascii=False),
            json.dumps(embedding or [], ensure_ascii=False) if embedding is not None else None,
            embedding_model,
            str(tags.get("tagger_version") or ""),
            float(tags.get("tag_confidence") or 0.0),
            now,
            now,
        ),
    )

    con.execute(
        """
        INSERT INTO jobs_indexed(
          clean_job_id, source, source_job_id, source_org, url, company_name, title_raw, title_clean,
          normalized_title, role_family, occupation_group, seniority, employment_type, location_type,
          city, region, country, salary_min, salary_max, salary_currency, skills_json, tags_json,
          embedding_json, embedding_model, tagger_version, tag_confidence, indexed_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(clean_job_id) DO UPDATE SET
          source=excluded.source,
          source_job_id=excluded.source_job_id,
          source_org=excluded.source_org,
          url=excluded.url,
          company_name=excluded.company_name,
          title_raw=excluded.title_raw,
          title_clean=excluded.title_clean,
          normalized_title=excluded.normalized_title,
          role_family=excluded.role_family,
          occupation_group=excluded.occupation_group,
          seniority=excluded.seniority,
          employment_type=excluded.employment_type,
          location_type=excluded.location_type,
          city=excluded.city,
          region=excluded.region,
          country=excluded.country,
          salary_min=excluded.salary_min,
          salary_max=excluded.salary_max,
          salary_currency=excluded.salary_currency,
          skills_json=excluded.skills_json,
          tags_json=excluded.tags_json,
          embedding_json=excluded.embedding_json,
          embedding_model=excluded.embedding_model,
          tagger_version=excluded.tagger_version,
          tag_confidence=excluded.tag_confidence,
          indexed_at=excluded.indexed_at
        """,
        (
            clean_job_id,
            str(raw_row.get("source") or ""),
            str(raw_row.get("external_id") or raw_row.get("source_job_id") or ""),
            str(raw_row.get("source_org") or ""),
            str(raw_row.get("url") or ""),
            str(raw_row.get("company_name") or ""),
            str(raw_row.get("title") or ""),
            clean.title_clean,
            normalized_title,
            role_family,
            occupation_group,
            tags.get("seniority"),
            tags.get("employment_type"),
            tags.get("location_type"),
            tags.get("city"),
            tags.get("region"),
            tags.get("country"),
            tags.get("salary_min"),
            tags.get("salary_max"),
            tags.get("salary_currency"),
            json.dumps(tags.get("skills") or [], ensure_ascii=False),
            json.dumps(tags.get("tags") or {}, ensure_ascii=False),
            json.dumps(embedding or [], ensure_ascii=False) if embedding is not None else None,
            embedding_model,
            str(tags.get("tagger_version") or ""),
            float(tags.get("tag_confidence") or 0.0),
            now,
        ),
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Run micro-SaaS indexing pipeline on local JSONL jobs.")
    ap.add_argument("--input", required=True, help="Input canonical jobs JSONL")
    ap.add_argument("--output-dir", required=True, help="Output directory for stage JSONL files")
    ap.add_argument("--db", default="data/jobintel_microsaas.sqlite")
    ap.add_argument("--max-rows", type=int, default=None)
    ap.add_argument("--no-db", action="store_true", help="Do not write to SQLite DB")
    ap.add_argument(
        "--embedding-mode",
        choices=["none", "hash", "openai", "gemini"],
        default="none",
        help="none=skip embeddings, hash=deterministic local vectors, openai/gemini=real API embeddings",
    )
    ap.add_argument("--openai-embedding-model", default="text-embedding-3-small")
    ap.add_argument("--gemini-embedding-model", default="text-embedding-004")
    ap.add_argument("--embedding-timeout-sec", type=int, default=30)
    ap.add_argument("--embedding-max-chars", type=int, default=4000)
    args = ap.parse_args()

    inp = Path(args.input)
    out_dir = Path(args.output_dir)
    rows = read_jsonl(inp, max_rows=args.max_rows)

    raw_out: list[dict[str, Any]] = []
    clean_out: list[dict[str, Any]] = []
    indexed_out: list[dict[str, Any]] = []
    cache: dict[str, dict[str, Any]] = {}

    con = None
    if not args.no_db:
        Path(args.db).parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(args.db)
        ensure_microsaas_schema(con)
        for row in con.execute("SELECT content_hash, normalized_title, role_family, occupation_group, seniority, employment_type, location_type, city, region, country, salary_min, salary_max, salary_currency, skills_json, tags_json, embedding_json, embedding_model, tagger_version, tag_confidence FROM extraction_cache"):
            cache[row[0]] = {
                "normalized_title": row[1],
                "role_family": row[2],
                "occupation_group": row[3],
                "seniority": row[4],
                "employment_type": row[5],
                "location_type": row[6],
                "city": row[7],
                "region": row[8],
                "country": row[9],
                "salary_min": row[10],
                "salary_max": row[11],
                "salary_currency": row[12],
                "skills": json.loads(row[13] or "[]"),
                "tags": json.loads(row[14] or "{}"),
                "embedding": json.loads(row[15]) if row[15] else None,
                "embedding_model": row[16],
                "tagger_version": row[17],
                "tag_confidence": row[18],
            }

    now = now_iso()
    cache_hits = 0
    for row in rows:
        source = str(row.get("source") or "greenhouse")
        source_job_id = str(row.get("external_id") or row.get("source_job_id") or "")
        raw_row = {
            "source": source,
            "source_job_id": source_job_id,
            "source_org": str(row.get("source_org") or ""),
            "url": str(row.get("url") or ""),
            "title_raw": str(row.get("title") or ""),
            "company_raw": str(row.get("company_name") or ""),
            "location_raw": str(row.get("location_raw") or ""),
            "description_raw": str(row.get("description_text") or ""),
            "language_hint": str(row.get("language") or ""),
            "payload_json": row,
            "fetched_at": now,
        }
        clean = clean_row(row)
        clean_row_out = {
            "source": source,
            "source_job_id": source_job_id,
            "url": raw_row["url"],
            "title_clean": clean.title_clean,
            "description_clean": clean.description_clean,
            "requirements_clean": clean.requirements_clean,
            "responsibilities_clean": clean.responsibilities_clean,
            "location_clean": clean.location_clean,
            "language": clean.language,
            "content_hash": clean.content_hash,
            "content_fingerprint": clean.content_fingerprint,
            "cleaned_at": now,
        }

        cached = cache.get(clean.content_hash)
        if cached is not None:
            cache_hits += 1
            normalized_title = str(cached.get("normalized_title") or "other")
            role_family = str(cached.get("role_family") or "other")
            occupation_group = str(cached.get("occupation_group") or "other")
            tags = {
                "normalized_title": normalized_title,
                "seniority": cached.get("seniority"),
                "employment_type": cached.get("employment_type"),
                "location_type": cached.get("location_type"),
                "city": cached.get("city"),
                "region": cached.get("region"),
                "country": cached.get("country"),
                "salary_min": cached.get("salary_min"),
                "salary_max": cached.get("salary_max"),
                "salary_currency": cached.get("salary_currency"),
                "skills": list(cached.get("skills") or []),
                "tags": dict(cached.get("tags") or {}),
                "tagger_version": str(cached.get("tagger_version") or "cache_v1"),
                "tag_confidence": float(cached.get("tag_confidence") or 0.5),
            }
            embedding = cached.get("embedding")
            embedding_model = cached.get("embedding_model")
        else:
            normalized_title, role_family, occupation_group = normalize_title(clean.title_clean)
            tags = extract_tags(clean, normalized_title=normalized_title)
            embedding_text = f"{clean.title_clean}\n{clean.requirements_clean}\n{clean.responsibilities_clean}\n{clean.description_clean}"
            embedding_text = embedding_text[: max(200, args.embedding_max_chars)]
            try:
                embedding, embedding_model = compute_embedding(
                    embedding_text,
                    mode=args.embedding_mode,
                    openai_model=args.openai_embedding_model,
                    gemini_model=args.gemini_embedding_model,
                    timeout_s=max(5, args.embedding_timeout_sec),
                )
            except urlerror.HTTPError as e:
                raise RuntimeError(f"embedding API HTTP error ({args.embedding_mode}): {e.code}") from e
            except urlerror.URLError as e:
                raise RuntimeError(f"embedding API network error ({args.embedding_mode}): {e}") from e

        indexed_row = {
            "source": source,
            "source_job_id": source_job_id,
            "source_org": raw_row["source_org"],
            "url": raw_row["url"],
            "company_name": str(row.get("company_name") or ""),
            "title_raw": raw_row["title_raw"],
            "title_clean": clean.title_clean,
            "normalized_title": normalized_title,
            "role_family": role_family,
            "occupation_group": occupation_group,
            "seniority": tags.get("seniority"),
            "employment_type": tags.get("employment_type"),
            "location_type": tags.get("location_type"),
            "city": tags.get("city"),
            "region": tags.get("region"),
            "country": tags.get("country"),
            "salary_min": tags.get("salary_min"),
            "salary_max": tags.get("salary_max"),
            "salary_currency": tags.get("salary_currency"),
            "skills": tags.get("skills") or [],
            "tags": tags.get("tags") or {},
            "embedding": embedding,
            "embedding_model": embedding_model,
            "tagger_version": tags.get("tagger_version"),
            "tag_confidence": tags.get("tag_confidence"),
            "indexed_at": now,
            "content_hash": clean.content_hash,
        }

        raw_out.append(raw_row)
        clean_out.append(clean_row_out)
        indexed_out.append(indexed_row)

        if con is not None:
            save_to_db(
                con,
                raw_row=row,
                clean=clean,
                normalized_title=normalized_title,
                role_family=role_family,
                occupation_group=occupation_group,
                tags=tags,
                embedding=embedding,
                embedding_model=embedding_model,
            )

    if con is not None:
        con.commit()
        con.close()

    write_jsonl(out_dir / "raw_jobs.jsonl", raw_out)
    write_jsonl(out_dir / "jobs_clean.jsonl", clean_out)
    write_jsonl(out_dir / "jobs_indexed.jsonl", indexed_out)

    print(f"Input rows: {len(rows)}")
    print(f"Cache hits: {cache_hits}")
    print(f"Wrote: {out_dir / 'raw_jobs.jsonl'}")
    print(f"Wrote: {out_dir / 'jobs_clean.jsonl'}")
    print(f"Wrote: {out_dir / 'jobs_indexed.jsonl'}")
    if args.no_db:
        print("DB: skipped (--no-db)")
    else:
        print(f"DB updated: {args.db}")


if __name__ == "__main__":
    main()
