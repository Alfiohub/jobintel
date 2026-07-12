from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from jobintel_next.pipelines.retrieval import QueryParams, run_query_pack, run_retrieval_query
from jobintel_next.storage import sqlite_count_jobs, sqlite_count_pack, sqlite_list_jobs, sqlite_run_pack


def _paginate(rows: list[dict[str, Any]], *, limit: int, offset: int) -> list[dict[str, Any]]:
    if offset < 0:
        offset = 0
    if limit < 0:
        limit = 0
    end = offset + limit
    return rows[offset:end]


def list_jobs(
    *,
    input_path: str | Path,
    query: QueryParams,
    limit: int = 20,
    offset: int = 0,
    sqlite_path: str | Path | None = None,
) -> dict[str, Any]:
    if sqlite_path:
        return sqlite_list_jobs(
            sqlite_path=sqlite_path,
            query=query,
            limit=limit,
            offset=offset,
        )
    base_query = replace(query, limit=None)
    rep = run_retrieval_query(input_path=input_path, query=base_query, output_path=None)
    total = rep["matched_rows"]
    paged = _paginate(rep["results"], limit=limit, offset=offset)
    return {
        "operation": "list_jobs",
        "input_path": str(input_path),
        "backend": "jsonl",
        "query": rep["query"],
        "total_count": total,
        "limit": limit,
        "offset": offset,
        "returned_count": len(paged),
        "results": paged,
    }


def count_jobs(
    *,
    input_path: str | Path,
    query: QueryParams,
    sqlite_path: str | Path | None = None,
) -> dict[str, Any]:
    if sqlite_path:
        return sqlite_count_jobs(
            sqlite_path=sqlite_path,
            query=query,
        )
    base_query = replace(query, limit=None)
    rep = run_retrieval_query(input_path=input_path, query=base_query, output_path=None)
    return {
        "operation": "count_jobs",
        "input_path": str(input_path),
        "backend": "jsonl",
        "query": rep["query"],
        "count": rep["matched_rows"],
    }


def run_pack(
    *,
    input_path: str | Path,
    pack_name: str,
    limit: int = 20,
    offset: int = 0,
    sqlite_path: str | Path | None = None,
) -> dict[str, Any]:
    if sqlite_path:
        return sqlite_run_pack(
            sqlite_path=sqlite_path,
            pack_name=pack_name,
            limit=limit,
            offset=offset,
        )
    rep = run_query_pack(
        input_path=input_path,
        pack_name=pack_name,
        limit=None,
        output_path=None,
    )
    total = rep["matched_rows"]
    paged = _paginate(rep["results"], limit=limit, offset=offset)
    return {
        "operation": "run_pack",
        "input_path": str(input_path),
        "backend": "jsonl",
        "pack_name": pack_name,
        "description": rep["description"],
        "quality": rep["quality"],
        "tradeoff": rep["tradeoff"],
        "clauses": rep["clauses"],
        "total_count": total,
        "limit": limit,
        "offset": offset,
        "returned_count": len(paged),
        "results": paged,
    }


def count_pack(
    *,
    input_path: str | Path,
    pack_name: str,
    sqlite_path: str | Path | None = None,
) -> dict[str, Any]:
    if sqlite_path:
        return sqlite_count_pack(
            sqlite_path=sqlite_path,
            pack_name=pack_name,
        )
    rep = run_query_pack(
        input_path=input_path,
        pack_name=pack_name,
        limit=None,
        output_path=None,
    )
    return {
        "operation": "count_pack",
        "input_path": str(input_path),
        "backend": "jsonl",
        "pack_name": pack_name,
        "count": rep["matched_rows"],
    }
