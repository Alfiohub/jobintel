from __future__ import annotations

import json
import os
import sqlite3
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

try:
    from automation.microsaas.ranking import rank_jobs
except ModuleNotFoundError:
    from ranking import rank_jobs


app = FastAPI(title="microsaas-search-mvp")

DEFAULT_DB_PATH = os.getenv("JOBINTEL_DB_PATH", "data/jobintel_microsaas.sqlite")


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def _to_job_dict(row: sqlite3.Row) -> dict[str, Any]:
    out = dict(row)
    skills_json = out.get("skills_json")
    if isinstance(skills_json, str):
        try:
            out["skills"] = json.loads(skills_json)
        except Exception:
            out["skills"] = []
    else:
        out["skills"] = []
    return out


def _skills_from_param(skills: str | None) -> list[str]:
    if not skills:
        return []
    return [s.strip().lower() for s in skills.split(",") if s.strip()]


def _e(value: Any) -> str:
    s = str(value or "")
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _render_home_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>opus.est</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root{
      --offwhite:#f3f2ee;
      --panel:#f8f7f4;
      --line:#d6d4cd;
      --ink:#1f1f1d;
      --muted:#66655f;
      --accent:#2c2c29;
    }
    *{box-sizing:border-box}
    html,body{margin:0;padding:0}
    body{font-family:"Source Sans 3",sans-serif;background:var(--offwhite);color:var(--ink)}
    .container{max-width:1180px;margin:0 auto;padding:0 20px}
    .topbar{position:sticky;top:0;background:rgba(243,242,238,.95);border-bottom:1px solid var(--line);z-index:8}
    .topbar .container{height:64px;display:flex;justify-content:space-between;align-items:center}
    .brand{font-weight:700;letter-spacing:.02em;text-decoration:none;color:var(--ink)}
    .btn{display:inline-flex;align-items:center;justify-content:center;height:40px;padding:0 14px;border-radius:8px;border:1px solid var(--line);background:#fff;color:var(--ink);text-decoration:none;font-weight:600}
    .btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
    .hero{padding:58px 0 44px;display:grid;grid-template-columns:1.35fr .65fr;gap:18px}
    h1{margin:0 0 12px;font-size:clamp(2rem,4vw,3.2rem);line-height:1.05}
    p{margin:0;color:var(--muted)}
    .kpi{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:24px}
    .kpi .box{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:12px}
    .kpi strong{display:block;font-size:1.2rem}
    .hero-card{border:1px solid var(--line);border-radius:12px;background:#fff;padding:16px}
    .hero-card h3{margin:0 0 8px;font-size:1.04rem}
    .hero-card ul{margin:0;padding-left:18px;color:var(--muted)}
    .hero-actions{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}
    .section{padding:18px 0 40px}
    .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .tile{border:1px solid var(--line);border-radius:10px;background:#fff;padding:14px}
    .tile h3{margin:0 0 6px;font-size:1rem}
    .tile p{font-size:.95rem}
    .footer{border-top:1px solid var(--line);padding:16px 0;color:var(--muted);font-size:.9rem}
    .footer .container{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
    @media (max-width:900px){.hero{grid-template-columns:1fr}.kpi,.grid{grid-template-columns:1fr 1fr}}
    @media (max-width:640px){.kpi,.grid{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="container">
      <a class="brand" href="/">opus.est</a>
      <div style="display:flex;gap:8px;">
        <a class="btn" href="/docs">API Docs</a>
        <a class="btn primary" href="/browse">Browse Jobs</a>
      </div>
    </div>
  </header>
  <main class="container">
    <section class="hero">
      <div>
        <h1>Be the first to discover relevant jobs.</h1>
        <p>Search with normalized taxonomy and clean location signals across role family, country, and location type.</p>
        <div class="hero-actions">
          <a class="btn primary" href="/browse">Start Browsing</a>
        </div>
        <div class="kpi">
          <div class="box"><strong>Fast</strong><span class="muted">Query-ready index</span></div>
          <div class="box"><strong>Clean</strong><span class="muted">Normalized country / location type</span></div>
          <div class="box"><strong>MVP</strong><span class="muted">Client-testable UI</span></div>
        </div>
      </div>
      <aside class="hero-card">
        <h3>What this MVP gives you</h3>
        <ul>
          <li>Role family filter for high-signal matching</li>
          <li>Country and city normalization for reliable geo search</li>
          <li>Location type filtering: remote, hybrid, onsite</li>
        </ul>
      </aside>
    </section>
    <section class="section">
      <div class="grid">
        <article class="tile"><h3>Role Family</h3><p>Filter jobs by consistent taxonomy instead of noisy raw titles.</p></article>
        <article class="tile"><h3>Luogo</h3><p>Country/city parsing reduces mismatch errors and missing geography.</p></article>
        <article class="tile"><h3>Location Type</h3><p>Remote, hybrid, onsite split makes shortlist quality much higher.</p></article>
      </div>
    </section>
  </main>
  <footer class="footer"><div class="container"><span>© opus.est</span><span>MVP search experience</span></div></footer>
</body>
</html>"""


def _render_browse_html(results: dict[str, Any], params: dict[str, Any], db_path: str) -> str:
    items: list[str] = []
    first_detail: dict[str, str] | None = None

    for idx, r in enumerate(results["results"]):
        company = _e(r.get("company_name") or "Company")
        title = _e(r.get("title_clean") or r.get("title_raw") or "Role")
        role_family = _e(r.get("role_family") or "unspecified")
        location_type = _e(r.get("location_type") or "unspecified")
        city = _e(r.get("city") or "")
        country = _e(r.get("country") or "")
        place = ", ".join([x for x in [city, country] if x]).strip(", ")
        if not place:
            place = "unspecified"
        salary = ""
        if r.get("salary_min") or r.get("salary_max"):
            salary = f"{r.get('salary_min') or ''} - {r.get('salary_max') or ''} {r.get('salary_currency') or ''}".strip()
        url = _e(r.get("url") or "#")

        if idx == 0:
            first_detail = {
                "title": title,
                "company": company,
                "role_family": role_family,
                "location_type": location_type,
                "place": _e(place),
                "salary": _e(salary or "not specified"),
                "url": url,
            }

        items.append(
            (
                f'<button class="job-item{" active" if idx == 0 else ""}" type="button" '
                f'data-title="{title}" data-company="{company}" data-role-family="{role_family}" '
                f'data-location-type="{location_type}" data-place="{_e(place)}" '
                f'data-salary="{_e(salary or "not specified")}" data-url="{url}">'
                f'<h3>{title}</h3>'
                f'<p class="company">{company}</p>'
                f'<p class="meta"><span>{role_family}</span> · <span>{_e(place)}</span> · <span>{location_type}</span></p>'
                "</button>"
            )
        )

    for k in ("normalized_title", "role_family", "country", "city", "location_type", "limit"):
        if params.get(k) is None:
            params[k] = ""

    list_html = "".join(items) or '<p class="muted">No roles matched. Try broader filters.</p>'
    if not first_detail:
        first_detail = {
            "title": "No job selected",
            "company": "",
            "role_family": "-",
            "location_type": "-",
            "place": "-",
            "salary": "-",
            "url": "#",
        }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>opus.est | Browse</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --offwhite:#f3f2ee;
      --panel:#f8f7f4;
      --line:#d6d4cd;
      --ink:#1f1f1d;
      --muted:#66655f;
      --accent:#2c2c29;
      --focus:#0a66c2;
    }}
    * {{ box-sizing:border-box; }}
    html, body {{ margin:0; padding:0; }}
    body {{ font-family:"Source Sans 3",sans-serif; background:var(--offwhite); color:var(--ink); }}
    .topbar {{ position:sticky; top:0; z-index:10; background:rgba(243,242,238,.95); border-bottom:1px solid var(--line); }}
    .topbar-inner {{ max-width:1300px; margin:0 auto; padding:14px 20px; display:flex; align-items:center; justify-content:space-between; }}
    .brand {{ font-weight:700; letter-spacing:.02em; text-decoration:none; color:var(--ink); font-size:1.12rem; }}
    .meta {{ color:var(--muted); font-size:.92rem; }}
    .layout {{ max-width:1300px; margin:0 auto; padding:18px 20px 28px; display:grid; grid-template-columns:280px 1fr 390px; gap:16px; min-height:calc(100vh - 66px); }}
    .panel {{ border:1px solid var(--line); border-radius:12px; background:var(--panel); }}
    .filters {{ padding:14px; position:sticky; top:80px; height:fit-content; }}
    .filters h2 {{ margin:0 0 12px; font-size:1.05rem; }}
    .field {{ margin-bottom:11px; }}
    .field label {{ display:block; font-size:.8rem; color:var(--muted); margin-bottom:4px; text-transform:uppercase; letter-spacing:.04em; }}
    .field input {{ width:100%; height:40px; padding:0 10px; border:1px solid var(--line); border-radius:8px; background:#fff; color:var(--ink); }}
    .field input:focus {{ outline:2px solid var(--focus); outline-offset:1px; border-color:var(--focus); }}
    .actions {{ display:flex; gap:8px; margin-top:6px; }}
    .btn {{ display:inline-flex; align-items:center; justify-content:center; height:38px; padding:0 12px; border-radius:8px; border:1px solid var(--line); text-decoration:none; color:var(--ink); background:#fff; font-weight:600; }}
    .btn.primary {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
    .list-wrap {{ padding:12px; }}
    .list-head {{ padding:2px 4px 12px; color:var(--muted); font-size:.94rem; border-bottom:1px solid var(--line); margin-bottom:10px; }}
    .jobs {{ display:flex; flex-direction:column; gap:8px; max-height:calc(100vh - 145px); overflow:auto; padding-right:4px; }}
    .job-item {{ width:100%; text-align:left; border:1px solid var(--line); border-radius:10px; background:#fff; padding:12px; cursor:pointer; }}
    .job-item:hover {{ border-color:#bcbab1; }}
    .job-item.active {{ border-color:#9d9a90; background:#fcfcfa; }}
    .job-item h3 {{ margin:0 0 4px; font-size:1.04rem; line-height:1.24; color:var(--ink); }}
    .company {{ margin:0 0 4px; color:#2f2f2b; font-weight:600; }}
    .job-item .meta {{ margin:0; font-size:.88rem; color:var(--muted); }}
    .detail {{ padding:16px; position:sticky; top:80px; height:fit-content; }}
    .detail h2 {{ margin:0 0 8px; line-height:1.2; font-size:1.28rem; }}
    .kv {{ margin:8px 0; display:grid; grid-template-columns:112px 1fr; gap:8px; font-size:.95rem; }}
    .k {{ color:var(--muted); text-transform:uppercase; letter-spacing:.04em; font-size:.75rem; }}
    .open-link {{ margin-top:14px; }}
    .muted {{ color:var(--muted); }}
    @media (max-width:1100px) {{ .layout {{ grid-template-columns:260px 1fr; }} .detail {{ grid-column:1 / -1; position:static; }} }}
    @media (max-width:760px) {{ .layout {{ grid-template-columns:1fr; padding:12px; }} .filters {{ position:static; }} .jobs {{ max-height:none; }} .detail {{ position:static; }} }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="/">opus.est</a>
      <div class="meta">Matched: <strong>{results["total_matched"]}</strong> · Showing: <strong>{results["returned_count"]}</strong></div>
    </div>
  </header>
  <main class="layout">
    <aside class="panel filters">
      <h2>Filters</h2>
      <form method="get" action="/browse">
        <div class="field"><label>Lavoro (title)</label><input name="normalized_title" value="{_e(params['normalized_title'])}" placeholder="es. data_analyst"></div>
        <div class="field"><label>Role family</label><input name="role_family" value="{_e(params['role_family'])}" placeholder="es. analytics"></div>
        <div class="field"><label>Luogo (country)</label><input name="country" value="{_e(params['country'])}" placeholder="es. SG / Singapore"></div>
        <div class="field"><label>Citta</label><input name="city" value="{_e(params['city'])}" placeholder="es. Singapore"></div>
        <div class="field"><label>Tipo location</label><input name="location_type" value="{_e(params['location_type'])}" placeholder="remote / hybrid / onsite"></div>
        <div class="field"><label>Limit</label><input name="limit" value="{_e(params['limit'])}" placeholder="30"></div>
        <div class="actions">
          <button class="btn primary" type="submit">Apply</button>
          <a class="btn" href="/browse">Reset</a>
        </div>
      </form>
    </aside>

    <section class="panel list-wrap">
      <div class="list-head">Role family · Luogo · Tipo location</div>
      <div class="jobs">{list_html}</div>
    </section>

    <aside class="panel detail" id="detail">
      <h2 id="d-title">{first_detail['title']}</h2>
      <p id="d-company" class="muted">{first_detail['company']}</p>
      <div class="kv"><div class="k">Role Family</div><div id="d-role-family">{first_detail['role_family']}</div></div>
      <div class="kv"><div class="k">Luogo</div><div id="d-place">{first_detail['place']}</div></div>
      <div class="kv"><div class="k">Location Type</div><div id="d-location-type">{first_detail['location_type']}</div></div>
      <div class="kv"><div class="k">Salary</div><div id="d-salary">{first_detail['salary']}</div></div>
      <div class="open-link"><a id="d-url" class="btn primary" href="{first_detail['url']}" target="_blank" rel="noopener">Open Job</a></div>
      <p class="muted" style="margin-top:12px;font-size:.82rem;">DB: <code>{_e(db_path)}</code></p>
    </aside>
  </main>
  <script>
    const items = document.querySelectorAll('.job-item');
    const dTitle = document.getElementById('d-title');
    const dCompany = document.getElementById('d-company');
    const dRoleFamily = document.getElementById('d-role-family');
    const dPlace = document.getElementById('d-place');
    const dLocationType = document.getElementById('d-location-type');
    const dSalary = document.getElementById('d-salary');
    const dUrl = document.getElementById('d-url');
    for (const item of items) {{
      item.addEventListener('click', () => {{
        for (const other of items) other.classList.remove('active');
        item.classList.add('active');
        dTitle.textContent = item.dataset.title || '';
        dCompany.textContent = item.dataset.company || '';
        dRoleFamily.textContent = item.dataset.roleFamily || '';
        dPlace.textContent = item.dataset.place || '';
        dLocationType.textContent = item.dataset.locationType || '';
        dSalary.textContent = item.dataset.salary || '';
        dUrl.href = item.dataset.url || '#';
      }});
    }}
  </script>
</body>
</html>"""


def search_jobs(
    *,
    db_path: str,
    normalized_title: str | None = None,
    role_family: str | None = None,
    country: str | None = None,
    city: str | None = None,
    location_type: str | None = None,
    seniority: str | None = None,
    employment_type: str | None = None,
    min_salary: int | None = None,
    skills: str | None = None,
    limit: int = 20,
    use_ranking: bool = True,
) -> dict[str, Any]:
    where: list[str] = []
    params: list[Any] = []

    if normalized_title:
        where.append("LOWER(normalized_title) = LOWER(?)")
        params.append(normalized_title)
    if role_family:
        where.append("LOWER(role_family) = LOWER(?)")
        params.append(role_family)
    if country:
        where.append("LOWER(country) = LOWER(?)")
        params.append(country)
    if city:
        where.append("LOWER(city) LIKE LOWER(?)")
        params.append(f"%{city.strip()}%")
    if location_type:
        where.append("LOWER(location_type) = LOWER(?)")
        params.append(location_type)
    if seniority:
        where.append("LOWER(seniority) = LOWER(?)")
        params.append(seniority)
    if employment_type:
        where.append("LOWER(employment_type) = LOWER(?)")
        params.append(employment_type)
    if min_salary is not None:
        where.append("salary_max IS NOT NULL AND salary_max >= ?")
        params.append(int(min_salary))

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with _connect(db_path) as con:
        count_row = con.execute(f"SELECT COUNT(*) AS c FROM jobs_indexed {where_sql}", params).fetchone()
        total_matched = int(count_row["c"]) if count_row else 0

        sql = (
            "SELECT id, url, company_name, title_raw, title_clean, normalized_title, role_family, occupation_group, "
            "seniority, employment_type, location_type, city, region, country, salary_min, salary_max, salary_currency, "
            "skills_json, indexed_at "
            f"FROM jobs_indexed {where_sql} "
            "ORDER BY indexed_at DESC "
            "LIMIT ?"
        )
        query_params = [*params, max(1, min(200, int(limit)))]
        rows = con.execute(sql, query_params).fetchall()

    jobs = [_to_job_dict(r) for r in rows]
    requested_skills = _skills_from_param(skills)

    if use_ranking:
        user_query = {
            "hard": {
                "country": country,
                "location_type": location_type,
                "employment_type": employment_type,
            },
            "preferred": {
                "normalized_title": normalized_title,
                "role_family": role_family,
                "country": country,
                "city": city,
                "location_type": location_type,
                "seniority": seniority,
                "employment_type": employment_type,
                "salary_min": min_salary,
                "skills": requested_skills,
            },
        }
        jobs = rank_jobs(jobs, user_query)
    else:
        for job in jobs:
            job["total_score"] = 0.0
            job["score_breakdown"] = {}
            job["hard_filter_passed"] = True

    return {
        "total_matched": total_matched,
        "returned_count": len(jobs),
        "results": jobs,
    }


@app.get("/search")
def search(
    normalized_title: str | None = Query(default=None),
    role_family: str | None = Query(default=None),
    country: str | None = Query(default=None),
    city: str | None = Query(default=None),
    location_type: str | None = Query(default=None),
    seniority: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    min_salary: int | None = Query(default=None, ge=0),
    skills: str | None = Query(default=None, description="Comma-separated, e.g. python,sql,aws"),
    limit: int = Query(default=20, ge=1, le=200),
    use_ranking: bool = Query(default=True),
    db_path: str = Query(default=DEFAULT_DB_PATH),
) -> dict[str, Any]:
    return search_jobs(
        db_path=db_path,
        normalized_title=normalized_title,
        role_family=role_family,
        country=country,
        city=city,
        location_type=location_type,
        seniority=seniority,
        employment_type=employment_type,
        min_salary=min_salary,
        skills=skills,
        limit=limit,
        use_ranking=use_ranking,
    )


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return _render_home_html()


@app.get("/browse", response_class=HTMLResponse)
def browse(
    normalized_title: str | None = Query(default=None),
    role_family: str | None = Query(default=None),
    country: str | None = Query(default=None),
    city: str | None = Query(default=None),
    location_type: str | None = Query(default=None),
    seniority: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    min_salary: int | None = Query(default=None, ge=0),
    skills: str | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=200),
    use_ranking: bool = Query(default=True),
    db_path: str = Query(default=DEFAULT_DB_PATH),
) -> HTMLResponse:
    results = search_jobs(
        db_path=db_path,
        normalized_title=normalized_title,
        role_family=role_family,
        country=country,
        city=city,
        location_type=location_type,
        seniority=seniority,
        employment_type=employment_type,
        min_salary=min_salary,
        skills=skills,
        limit=limit,
        use_ranking=use_ranking,
    )
    params = {
        "normalized_title": normalized_title,
        "role_family": role_family,
        "country": country,
        "city": city,
        "location_type": location_type,
        "seniority": seniority,
        "employment_type": employment_type,
        "min_salary": min_salary,
        "skills": skills,
        "limit": limit,
    }
    return HTMLResponse(_render_browse_html(results, params, db_path))
