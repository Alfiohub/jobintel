from __future__ import annotations

import json
import sqlite3
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

try:
    from automation.microsaas.ranking import rank_jobs
except ModuleNotFoundError:
    from ranking import rank_jobs


app = FastAPI(title="microsaas-search-mvp")


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
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;600&family=Manrope:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root{
      --canvas:#F6F4EF;--stone:#E7E2D8;--line:#D5CEC2;--graphite:#2B2A28;--ink:#171816;--muted:#7A7770;--accent:#2F5D5A;
      --r-sm:8px;--r-md:12px;--s1:8px;--s2:16px;--s3:24px;--s4:32px;--s5:48px;--s6:64px;--s7:96px;
    }
    *{box-sizing:border-box}html,body{margin:0;padding:0}
    body{font-family:Manrope,system-ui,sans-serif;background:var(--canvas);color:var(--graphite);line-height:1.5}
    .container{width:min(1140px,calc(100% - 48px));margin:0 auto}
    .topbar{position:sticky;top:0;background:rgba(246,244,239,.93);backdrop-filter:blur(4px);border-bottom:1px solid var(--line)}
    .topbar .container{height:74px;display:flex;justify-content:space-between;align-items:center}
    .wordmark{font-family:Fraunces,serif;font-size:1.5rem;color:var(--ink);text-decoration:none}
    .btn{display:inline-flex;align-items:center;gap:8px;padding:11px 16px;border-radius:8px;border:1px solid var(--line);text-decoration:none;color:var(--graphite);font-weight:600;transition:.2s ease}
    .btn:hover{transform:translateY(-2px)}
    .btn.primary{background:var(--accent);border-color:var(--accent);color:#f4f5f3}
    .hero{padding:var(--s7) 0 var(--s6);display:grid;grid-template-columns:1.2fr .8fr;gap:var(--s6);align-items:end}
    h1,h2,h3{font-family:Fraunces,serif;color:var(--ink);line-height:1.1;margin:0 0 var(--s3)}
    h1{font-size:clamp(2.2rem,6vw,4.9rem)}h2{font-size:clamp(1.6rem,3vw,2.5rem)}h3{font-size:1.25rem}
    p{margin:0 0 var(--s2);color:var(--muted);max-width:64ch}
    .hero-actions{display:flex;gap:var(--s2);flex-wrap:wrap;margin-top:var(--s4)}
    .panel{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,#faf9f6,#f1ede4);padding:var(--s4)}
    .label{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
    .panel .big{font-family:Fraunces,serif;color:var(--ink);font-size:clamp(1.6rem,2.7vw,2.4rem);margin:14px 0 10px}
    .trust{border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:#f9f7f2}
    .trust .container{display:grid;grid-template-columns:repeat(4,1fr);min-height:104px;align-items:center;gap:var(--s4)}
    .trust strong{display:block;color:var(--ink);font-size:1.2rem}.trust span{color:var(--muted);font-size:.9rem}
    .section{padding:var(--s7) 0}
    .jobs-head{display:flex;justify-content:space-between;align-items:end;gap:var(--s4);margin-bottom:var(--s5)}
    .jobs{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s3)}
    .card{border:1px solid var(--line);border-radius:8px;background:#fbfaf7;padding:28px;transition:.2s ease}
    .card:hover{transform:translateY(-3px);border-color:#c5bcaf}
    .chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:var(--s3)}
    .chip{border:1px solid var(--line);border-radius:6px;padding:4px 8px;font-size:.78rem;color:var(--muted);background:#f5f2ec}
    .footrow{margin-top:var(--s4);padding-top:var(--s3);border-top:1px solid var(--line);display:flex;justify-content:space-between;color:var(--muted);font-size:.88rem}
    .line-top{border-top:1px solid var(--line)} .value{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s3)}
    .value article{border-top:1px solid var(--line);padding-top:var(--s3)}
    .quote{border:1px solid var(--line);border-radius:12px;padding:var(--s6);background:#faf8f3}
    blockquote{margin:0;font-family:Fraunces,serif;color:var(--ink);font-size:clamp(1.2rem,2.2vw,1.8rem);max-width:40ch}
    .cta{border:1px solid var(--line);border-radius:12px;background:var(--stone);padding:var(--s6);display:flex;justify-content:space-between;align-items:center;gap:var(--s4)}
    footer{border-top:1px solid var(--line);padding:var(--s5) 0;color:var(--muted);font-size:.9rem}
    footer .container{display:flex;justify-content:space-between;gap:var(--s2);flex-wrap:wrap}
    @media (max-width:980px){.hero{grid-template-columns:1fr}.trust .container,.jobs,.value{grid-template-columns:1fr 1fr}.cta{flex-direction:column;align-items:flex-start}}
    @media (max-width:680px){.container{width:min(1140px,calc(100% - 32px))}.jobs,.value,.trust .container{grid-template-columns:1fr}.hero-actions .btn{width:100%;justify-content:center}}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="container">
      <a class="wordmark" href="/">opus.est</a>
      <a class="btn primary" href="/browse">Browse Roles</a>
    </div>
  </header>
  <main>
    <section class="container hero">
      <div>
        <h1>Work, with precision and purpose.</h1>
        <p>opus.est is a refined job platform for professionals who value clarity, craft, and long-term trajectory.</p>
        <div class="hero-actions">
          <a class="btn primary" href="/browse">Explore Opportunities</a>
          <a class="btn" href="/docs">API Docs</a>
        </div>
      </div>
      <aside class="panel">
        <span class="label">This week</span>
        <div class="big">Selected roles in product, data, and responsible AI.</div>
        <p>Curated listings with normalized titles, location context, and comparable salary signal.</p>
      </aside>
    </section>
    <section class="trust"><div class="container">
      <div><strong>12k+</strong><span>Professionals in network</span></div>
      <div><strong>430</strong><span>Curated roles this month</span></div>
      <div><strong>91%</strong><span>Profiles with verified context</span></div>
      <div><strong>27</strong><span>Countries represented</span></div>
    </div></section>
    <section class="section container">
      <div class="jobs-head"><div><h2>Featured opportunities</h2><p>Elegant, comparable, and decision-ready role snapshots.</p></div></div>
      <div class="jobs">
        <article class="card"><div class="chips"><span class="chip">Product</span><span class="chip">Hybrid · Berlin</span><span class="chip">€90k–120k</span></div><h3>Senior Product Strategist</h3><p>Guide cross-functional direction for a platform focused on financial resilience.</p><div class="footrow"><span>Northline</span><span>3 days ago</span></div></article>
        <article class="card"><div class="chips"><span class="chip">Data</span><span class="chip">Remote · EU</span><span class="chip">€80k–105k</span></div><h3>Analytics Engineer</h3><p>Build reliable semantic layers connecting product judgment and operational truth.</p><div class="footrow"><span>Aster Labs</span><span>2 days ago</span></div></article>
        <article class="card"><div class="chips"><span class="chip">Engineering</span><span class="chip">Onsite · Paris</span><span class="chip">€95k–130k</span></div><h3>Backend Engineer, Platform</h3><p>Design resilient systems and clean interfaces for mission-critical workflows.</p><div class="footrow"><span>Maison Compute</span><span>Today</span></div></article>
      </div>
    </section>
    <section class="section line-top"><div class="container value">
      <article><h3>Curated with intent</h3><p>Listings are normalized so your energy goes to meaningful decisions, not cleanup.</p></article>
      <article><h3>Signal over noise</h3><p>We surface context that matters: title precision, location realism, and salary quality.</p></article>
      <article><h3>Built for trajectories</h3><p>A calmer interface for professionals optimizing for substance, growth, and fit.</p></article>
    </div></section>
    <section class="section container"><div class="quote"><blockquote>“For the first time in years, a platform respected my attention. Every role felt comparable and credible.”</blockquote><p style="margin-top:24px">Elena M., Staff Product Analyst</p></div></section>
    <section class="section line-top"><div class="container"><div class="cta"><div><h2>Find work that deserves your best years.</h2><p>Discover opportunities aligned with your standards and ambitions.</p></div><a class="btn primary" href="/browse">Start browsing</a></div></div></section>
  </main>
  <footer><div class="container"><span>© opus.est</span><span>Crafted for meaningful careers.</span></div></footer>
</body>
</html>"""


def _render_browse_html(results: dict[str, Any], params: dict[str, Any], db_path: str) -> str:
    cards: list[str] = []
    for r in results["results"]:
        company = _e(r.get("company_name") or "Company")
        title = _e(r.get("title_clean") or r.get("title_raw") or "Role")
        location_bits = [r.get("city"), r.get("country")]
        location = _e(", ".join([str(x) for x in location_bits if x]))
        if not location:
            location = _e(r.get("location_type") or "unspecified")
        salary = ""
        if r.get("salary_min") or r.get("salary_max"):
            salary = f"{r.get('salary_min') or ''}-{r.get('salary_max') or ''} {r.get('salary_currency') or ''}".strip("- ")
        chips = []
        if r.get("role_family"):
            chips.append(f'<span class="chip">{_e(r.get("role_family"))}</span>')
        chips.append(f'<span class="chip">{location}</span>')
        if salary:
            chips.append(f'<span class="chip">{_e(salary)}</span>')
        score = f"{float(r.get('total_score') or 0.0):.2f}"
        url = _e(r.get("url") or "#")
        cards.append(
            f"""<article class="card">
  <div class="chips">{''.join(chips)}</div>
  <h3>{title}</h3>
  <p>{company}</p>
  <div class="footrow"><span>score {score}</span><a href="{url}" target="_blank" rel="noopener">Open role</a></div>
</article>"""
        )

    for k in (
        "normalized_title",
        "role_family",
        "country",
        "location_type",
        "seniority",
        "employment_type",
        "skills",
        "min_salary",
        "limit",
    ):
        if params.get(k) is None:
            params[k] = ""

    cards_html = "".join(cards) or '<p class="muted">No roles matched. Try broader criteria.</p>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>opus.est | Browse</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;600&family=Manrope:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--canvas:#F6F4EF;--stone:#E7E2D8;--line:#D5CEC2;--graphite:#2B2A28;--ink:#171816;--muted:#7A7770;--accent:#2F5D5A}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--canvas);font-family:Manrope,system-ui,sans-serif;color:var(--graphite)}}a{{color:inherit}}
.container{{width:min(1140px,calc(100% - 48px));margin:0 auto}}.top{{height:74px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}}
.wordmark{{font-family:Fraunces,serif;font-size:1.5rem;text-decoration:none;color:var(--ink)}}.btn{{padding:10px 14px;border:1px solid var(--line);border-radius:8px;text-decoration:none;background:#fbfaf7}}
.btn.primary{{background:var(--accent);border-color:var(--accent);color:#f5f5f3}}h1,h2,h3{{font-family:Fraunces,serif;color:var(--ink);line-height:1.1}}
main{{padding:48px 0 96px}}.meta{{color:var(--muted)}}.panel{{border:1px solid var(--line);border-radius:12px;background:#fbfaf7;padding:24px;margin:24px 0 32px}}
form{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}}label{{font-size:.78rem;color:var(--muted);display:block;margin-bottom:4px}}
input{{width:100%;padding:10px;border:1px solid var(--line);border-radius:8px;background:#f7f4ee;color:var(--graphite)}}
.actions{{grid-column:1/-1;display:flex;gap:12px;align-items:center}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.card{{border:1px solid var(--line);border-radius:8px;background:#fbfaf7;padding:24px}}.chips{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}}
.chip{{border:1px solid var(--line);border-radius:6px;padding:4px 8px;font-size:.78rem;color:var(--muted);background:#f5f2ec}}
.footrow{{margin-top:24px;padding-top:16px;border-top:1px solid var(--line);display:flex;justify-content:space-between;color:var(--muted);font-size:.88rem}}
.muted{{color:var(--muted)}}@media (max-width:1024px){{form{{grid-template-columns:repeat(3,1fr)}}.cards{{grid-template-columns:1fr 1fr}}}}@media (max-width:680px){{.container{{width:min(1140px,calc(100% - 32px))}}form,.cards{{grid-template-columns:1fr}}}}
</style></head>
<body>
<header><div class="container top"><a class="wordmark" href="/">opus.est</a><a class="btn" href="/docs">API docs</a></div></header>
<main class="container">
  <h1>Browse curated roles</h1>
  <p class="meta">Total matched: <strong>{results['total_matched']}</strong> · Returned: <strong>{results['returned_count']}</strong> · DB: <code>{_e(db_path)}</code></p>
  <section class="panel">
    <form method="get" action="/browse">
      <div><label>normalized_title</label><input name="normalized_title" value="{_e(params['normalized_title'])}"></div>
      <div><label>role_family</label><input name="role_family" value="{_e(params['role_family'])}"></div>
      <div><label>country</label><input name="country" value="{_e(params['country'])}"></div>
      <div><label>location_type</label><input name="location_type" value="{_e(params['location_type'])}"></div>
      <div><label>seniority</label><input name="seniority" value="{_e(params['seniority'])}"></div>
      <div><label>employment_type</label><input name="employment_type" value="{_e(params['employment_type'])}"></div>
      <div><label>min_salary</label><input name="min_salary" value="{_e(params['min_salary'])}"></div>
      <div><label>skills (csv)</label><input name="skills" value="{_e(params['skills'])}"></div>
      <div><label>limit</label><input name="limit" value="{_e(params['limit'])}"></div>
      <div class="actions"><button class="btn primary" type="submit">Search</button><a class="btn" href="/browse">Reset</a></div>
    </form>
  </section>
  <section class="cards">{cards_html}</section>
</main>
</body></html>"""


def search_jobs(
    *,
    db_path: str,
    normalized_title: str | None = None,
    role_family: str | None = None,
    country: str | None = None,
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
    location_type: str | None = Query(default=None),
    seniority: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    min_salary: int | None = Query(default=None, ge=0),
    skills: str | None = Query(default=None, description="Comma-separated, e.g. python,sql,aws"),
    limit: int = Query(default=20, ge=1, le=200),
    use_ranking: bool = Query(default=True),
    db_path: str = Query(default="data/jobintel_microsaas.sqlite"),
) -> dict[str, Any]:
    return search_jobs(
        db_path=db_path,
        normalized_title=normalized_title,
        role_family=role_family,
        country=country,
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
    location_type: str | None = Query(default=None),
    seniority: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    min_salary: int | None = Query(default=None, ge=0),
    skills: str | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=200),
    use_ranking: bool = Query(default=True),
    db_path: str = Query(default="data/jobintel_microsaas.sqlite"),
) -> HTMLResponse:
    results = search_jobs(
        db_path=db_path,
        normalized_title=normalized_title,
        role_family=role_family,
        country=country,
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
        "location_type": location_type,
        "seniority": seniority,
        "employment_type": employment_type,
        "min_salary": min_salary,
        "skills": skills,
        "limit": limit,
    }
    return HTMLResponse(_render_browse_html(results, params, db_path))
