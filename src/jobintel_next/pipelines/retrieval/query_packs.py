from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .query import QueryParams, _sort_rows, run_retrieval_query


@dataclass(frozen=True)
class QueryPackClause:
    name: str
    query: QueryParams


@dataclass(frozen=True)
class QueryPackSpec:
    name: str
    description: str
    quality: str
    tradeoff: str
    clauses: tuple[QueryPackClause, ...]


def _clause(name: str, query: QueryParams) -> QueryPackClause:
    return QueryPackClause(name=name, query=query)


def _query_dict(q: QueryParams) -> dict[str, Any]:
    return {
        "normalized_title": q.normalized_title,
        "role_family": q.role_family,
        "language_bucket": q.language_bucket,
        "location_type": q.location_type,
        "employment_type": q.employment_type,
        "has_salary": q.has_salary,
        "has_skills": q.has_skills,
        "title_is_other": q.title_is_other,
        "skills_contains": q.skills_contains or [],
        "salary_currency": q.salary_currency,
        "sort_by": q.sort_by,
        "limit": q.limit,
    }


def get_query_packs() -> dict[str, QueryPackSpec]:
    packs = [
        QueryPackSpec(
            name="python_tech_jobs",
            description="Python jobs with stronger product signal: non-other + technical families.",
            quality="usable",
            tradeoff="Lower recall on python mentions in broad non-tech roles.",
            clauses=(
                _clause(
                    "python_non_other",
                    QueryParams(skills_contains=["python"], title_is_other=False, sort_by="published_at_desc"),
                ),
                _clause(
                    "python_software_engineering",
                    QueryParams(skills_contains=["python"], role_family="software_engineering", sort_by="published_at_desc"),
                ),
                _clause(
                    "python_data_engineering",
                    QueryParams(skills_contains=["python"], role_family="data_engineering", sort_by="published_at_desc"),
                ),
                _clause(
                    "python_machine_learning",
                    QueryParams(skills_contains=["python"], role_family="machine_learning", sort_by="published_at_desc"),
                ),
                _clause(
                    "python_data_science",
                    QueryParams(skills_contains=["python"], role_family="data_science", sort_by="published_at_desc"),
                ),
                _clause(
                    "python_sre",
                    QueryParams(skills_contains=["python"], role_family="sre", sort_by="published_at_desc"),
                ),
                _clause(
                    "python_devops",
                    QueryParams(skills_contains=["python"], role_family="devops", sort_by="published_at_desc"),
                ),
            ),
        ),
        QueryPackSpec(
            name="remote_data_jobs",
            description="Remote-oriented data roles with title normalization not other.",
            quality="strong",
            tradeoff="Does not include data-like jobs still classified as other.",
            clauses=(
                _clause(
                    "remote_data_engineering_family",
                    QueryParams(role_family="data_engineering", location_type="remote", title_is_other=False, sort_by="published_at_desc"),
                ),
                _clause(
                    "remote_data_analyst",
                    QueryParams(normalized_title="data_analyst", location_type="remote", title_is_other=False, sort_by="published_at_desc"),
                ),
                _clause(
                    "remote_data_scientist",
                    QueryParams(normalized_title="data_scientist", location_type="remote", title_is_other=False, sort_by="published_at_desc"),
                ),
            ),
        ),
        QueryPackSpec(
            name="marketing_jobs_with_salary",
            description="Marketing jobs where salary signal is present.",
            quality="strong",
            tradeoff="Biased toward geographies/companies with salary disclosure.",
            clauses=(
                _clause(
                    "marketing_salary",
                    QueryParams(role_family="marketing", has_salary=True, title_is_other=False, sort_by="published_at_desc"),
                ),
            ),
        ),
        QueryPackSpec(
            name="account_executive_jobs",
            description="High-precision account executive opportunities.",
            quality="strong",
            tradeoff="Only normalized account executive roles.",
            clauses=(
                _clause(
                    "account_executive",
                    QueryParams(normalized_title="account_executive", title_is_other=False, sort_by="published_at_desc"),
                ),
            ),
        ),
        QueryPackSpec(
            name="healthcare_clinical_jobs",
            description="Healthcare clinical jobs covered by current taxonomy.",
            quality="usable",
            tradeoff="Clinical residual long-tail in other is not included.",
            clauses=(
                _clause(
                    "healthcare_clinical",
                    QueryParams(role_family="healthcare_clinical", title_is_other=False, sort_by="published_at_desc"),
                ),
            ),
        ),
        QueryPackSpec(
            name="skilled_trades_jobs",
            description="Skilled trades jobs covered by current taxonomy pack.",
            quality="usable",
            tradeoff="Domain-specific long-tail variants can still be in other.",
            clauses=(
                _clause(
                    "skilled_trades",
                    QueryParams(role_family="skilled_trades", title_is_other=False, sort_by="published_at_desc"),
                ),
            ),
        ),
        QueryPackSpec(
            name="high_confidence_tech_jobs",
            description="Core technical normalized titles with salary/skills strong signals.",
            quality="strong",
            tradeoff="Conservative and intentionally excludes borderline technical roles.",
            clauses=(
                _clause(
                    "software_engineer",
                    QueryParams(normalized_title="software_engineer", title_is_other=False, has_skills=True, sort_by="published_at_desc"),
                ),
                _clause(
                    "data_engineer",
                    QueryParams(normalized_title="data_engineer", title_is_other=False, has_skills=True, sort_by="published_at_desc"),
                ),
                _clause(
                    "ml_engineer",
                    QueryParams(normalized_title="ml_engineer", title_is_other=False, has_skills=True, sort_by="published_at_desc"),
                ),
                _clause(
                    "devops_engineer",
                    QueryParams(normalized_title="devops_engineer", title_is_other=False, has_skills=True, sort_by="published_at_desc"),
                ),
                _clause(
                    "site_reliability_engineer",
                    QueryParams(normalized_title="site_reliability_engineer", title_is_other=False, has_skills=True, sort_by="published_at_desc"),
                ),
                _clause(
                    "solutions_architect",
                    QueryParams(normalized_title="solutions_architect", title_is_other=False, has_skills=True, sort_by="published_at_desc"),
                ),
            ),
        ),
        QueryPackSpec(
            name="other_with_strong_signals",
            description="Discovery pack: other titles but with stronger structured signals.",
            quality="noisy",
            tradeoff="Useful for curation; heterogeneity remains high by design.",
            clauses=(
                _clause(
                    "other_salary_and_skills",
                    QueryParams(normalized_title="other", has_skills=True, has_salary=True, sort_by="published_at_desc"),
                ),
                _clause(
                    "other_remote_with_skills",
                    QueryParams(normalized_title="other", has_skills=True, location_type="remote", sort_by="published_at_desc"),
                ),
            ),
        ),
    ]
    return {p.name: p for p in packs}


def list_query_pack_names() -> list[str]:
    return sorted(get_query_packs().keys())


def _compact_rows(rows: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows[:limit]:
        out.append(
            {
                "url": row.get("url"),
                "title_raw": row.get("title_raw"),
                "normalized_title": row.get("normalized_title"),
                "role_family": row.get("role_family"),
                "location_type": row.get("location_type"),
                "employment_type": row.get("employment_type"),
                "has_salary": row.get("has_salary"),
                "has_skills": row.get("has_skills"),
                "title_is_other": row.get("title_is_other"),
                "skills": row.get("skills") if isinstance(row.get("skills"), list) else [],
                "published_at": row.get("published_at"),
                "updated_at": row.get("updated_at"),
            }
        )
    return out


def run_query_pack(
    *,
    input_path: str | Path,
    pack_name: str,
    limit: int | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    packs = get_query_packs()
    if pack_name not in packs:
        raise ValueError(f"unknown query pack: {pack_name}")
    spec = packs[pack_name]

    by_url: dict[str, dict[str, Any]] = {}
    clause_counts: list[dict[str, Any]] = []
    for clause in spec.clauses:
        clause_res = run_retrieval_query(
            input_path=input_path,
            query=clause.query,
            output_path=None,
        )
        clause_counts.append(
            {
                "clause_name": clause.name,
                "query": _query_dict(clause.query),
                "matched_rows": clause_res["matched_rows"],
            }
        )
        for row in clause_res["results"]:
            url = str(row.get("url") or "")
            if url and url not in by_url:
                by_url[url] = row

    merged = list(by_url.values())
    sort_hint = spec.clauses[0].query.sort_by if spec.clauses else "published_at_desc"
    merged = _sort_rows(merged, sort_hint)

    if limit is not None:
        merged = merged[:limit]

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for row in merged:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return {
        "input_path": str(input_path),
        "pack_name": pack_name,
        "description": spec.description,
        "quality": spec.quality,
        "tradeoff": spec.tradeoff,
        "clauses": clause_counts,
        "matched_rows": len(merged),
        "results": merged,
    }


def build_query_packs_report(
    *,
    input_path: str | Path,
    report_dir: str | Path = "docs",
    sample_limit: int = 10,
) -> dict[str, Any]:
    in_path = Path(input_path)
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    packs = get_query_packs()
    pack_reports: list[dict[str, Any]] = []
    for name in sorted(packs.keys()):
        rep = run_query_pack(input_path=in_path, pack_name=name, limit=None)
        pack_reports.append(
            {
                "pack_name": name,
                "description": rep["description"],
                "quality": rep["quality"],
                "tradeoff": rep["tradeoff"],
                "filters": rep["clauses"],
                "matched_rows": rep["matched_rows"],
                "sample_rows": _compact_rows(rep["results"], limit=sample_limit),
            }
        )

    report = {
        "input_path": str(in_path),
        "packs": pack_reports,
        "known_limits": [
            "Pack composition is deterministic and rules-based only.",
            "No ranking/semantic search in this step.",
            "Pack quality depends on upstream title and skills signals.",
        ],
    }

    json_path = out_dir / "query_packs_step18.json"
    md_path = out_dir / "query_packs_step18.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Query Packs Step 18",
        "",
        f"Input: `{in_path}`",
        "",
        "## Pack List",
    ]
    for p in pack_reports:
        md_lines.append(
            f"- `{p['pack_name']}` | quality={p['quality']} | matched_rows={p['matched_rows']}"
        )

    md_lines.append("")
    md_lines.append("## Pack Details")
    for p in pack_reports:
        md_lines.append(f"### {p['pack_name']}")
        md_lines.append(f"- quality: **{p['quality']}**")
        md_lines.append(f"- description: {p['description']}")
        md_lines.append(f"- matched_rows: {p['matched_rows']}")
        md_lines.append(f"- tradeoff: {p['tradeoff']}")
        md_lines.append("- filters:")
        for clause in p["filters"]:
            md_lines.append(f"  - {clause['clause_name']}: `{clause['query']}` (matched={clause['matched_rows']})")
        md_lines.append(f"- sample rows ({len(p['sample_rows'])}):")
        for row in p["sample_rows"]:
            md_lines.append(
                f"  - {row['url']} | {row['title_raw']} | {row['normalized_title']} | "
                f"family={row['role_family']} | loc={row['location_type']} | "
                f"salary={row['has_salary']} | skills={row['has_skills']} | other={row['title_is_other']}"
            )
        md_lines.append("")

    md_lines.append("## Known Limits")
    for lim in report["known_limits"]:
        md_lines.append(f"- {lim}")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return report
