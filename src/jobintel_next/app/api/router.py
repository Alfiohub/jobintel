from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from jobintel_next.pipelines.retrieval import QueryParams, get_query_packs
from jobintel_next.product.alerts import (
    SMTPConfig,
    get_alert_run_detail,
    get_alert_runs_summary,
    list_alert_runs,
    persist_email_delivery_to_run,
    send_email_alerts_from_run,
)
from jobintel_next.product.auth import get_user_settings
from jobintel_next.product.job_state import clear_job_state, get_job_state, get_many_job_states, set_job_state
from jobintel_next.product.saved_searches import (
    archive_saved_search,
    check_new_matches,
    create_saved_search,
    delete_saved_search,
    disable_saved_search,
    enable_saved_search,
    get_saved_search_results,
    list_saved_searches,
    restore_saved_search,
    run_enabled_saved_searches,
    run_saved_search,
    update_saved_search,
)
from jobintel_next.serving import count_jobs, count_pack, get_facets, list_jobs, run_pack

from .dependencies import (
    CurrentUser,
    get_alert_runs_dir,
    get_current_user,
    get_dataset_path,
    get_job_state_db_path,
    get_saved_db_path,
    get_sqlite_path,
)
from .schemas import (
    AlertRunAllResponse,
    AlertRunDetailResponse,
    AlertRunsListResponse,
    AlertSummaryResponse,
    ErrorResponse,
    FacetsResponse,
    HealthResponse,
    JobCountResponse,
    JobStateClearResponse,
    JobStateResponse,
    JobStateSetRequest,
    JobListResponse,
    PackCountResponse,
    PacksListResponse,
    PackRunResponse,
    SavedSearchCheckNewResponse,
    SavedSearchCreateRequest,
    SavedSearchDeleteResponse,
    SavedSearchListResponse,
    SavedSearchMutationResponse,
    SavedSearchResultsResponse,
    SavedSearchRunResponse,
    SavedSearchUpdateRequest,
    SortBy,
)

router = APIRouter()


def _attach_job_states(results: list[dict], job_state_db_path: str, *, user_id: str) -> list[dict]:
    urls = [str(r.get("url") or "").strip() for r in results if isinstance(r, dict)]
    states = get_many_job_states(db_path=job_state_db_path, job_urls=urls, user_id=user_id)
    out: list[dict] = []
    for r in results:
        if not isinstance(r, dict):
            out.append(r)
            continue
        row = dict(r)
        url = str(row.get("url") or "").strip()
        row["job_state"] = states.get(url, "new")
        out.append(row)
    return out


def _filter_rows_by_state(
    rows: list[dict],
    *,
    job_state: str | None,
    include_dismissed: bool,
) -> list[dict]:
    state_filter = (job_state or "").strip().lower() or None
    if state_filter is not None and state_filter not in {"new", "seen", "saved", "dismissed"}:
        raise HTTPException(status_code=422, detail=f"invalid job_state: {job_state}")
    out: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        current = str(row.get("job_state") or "new").strip().lower() or "new"
        if not include_dismissed and current == "dismissed":
            continue
        if state_filter is not None and current != state_filter:
            continue
        out.append(row)
    return out


def _with_state_filters_query_echo(rep: dict, *, job_state: str | None, include_dismissed: bool) -> None:
    query = rep.get("query")
    if isinstance(query, dict):
        query["job_state"] = job_state
        query["include_dismissed"] = include_dismissed


@router.get("/health", response_model=HealthResponse)
def health(
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
) -> dict[str, str]:
    return {"status": "ok", "dataset_path": sqlite_path or dataset_path}


@router.get("/jobs", response_model=JobListResponse)
def get_jobs(
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    normalized_title: str | None = None,
    role_family: str | None = None,
    language_bucket: str | None = None,
    location_type: str | None = None,
    employment_type: str | None = None,
    has_salary: bool | None = None,
    has_skills: bool | None = None,
    title_is_other: bool | None = None,
    skills_contains: list[str] | None = Query(default=None),
    salary_currency: str | None = Query(default=None, max_length=8),
    job_state: str | None = Query(default=None),
    include_dismissed: bool = Query(default=True),
    sort_by: SortBy = "published_at_desc",
    limit: int = Query(default=20, ge=0, le=1000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    query = QueryParams(
        normalized_title=normalized_title,
        role_family=role_family,
        language_bucket=language_bucket,
        location_type=location_type,
        employment_type=employment_type,
        has_salary=has_salary,
        has_skills=has_skills,
        title_is_other=title_is_other,
        skills_contains=skills_contains,
        salary_currency=salary_currency,
        sort_by=sort_by,
        limit=None,
    )
    needs_state_filter = job_state is not None or not include_dismissed
    if not needs_state_filter:
        rep = list_jobs(
            input_path=dataset_path,
            query=query,
            limit=limit,
            offset=offset,
            sqlite_path=sqlite_path,
        )
        rep["results"] = _attach_job_states(rep.get("results", []), job_state_db_path, user_id=current_user.user_id)
        _with_state_filters_query_echo(rep, job_state=job_state, include_dismissed=include_dismissed)
        return rep

    rep_all = list_jobs(
        input_path=dataset_path,
        query=query,
        limit=1_000_000,
        offset=0,
        sqlite_path=sqlite_path,
    )
    rows = _attach_job_states(rep_all.get("results", []), job_state_db_path, user_id=current_user.user_id)
    rows = _filter_rows_by_state(rows, job_state=job_state, include_dismissed=include_dismissed)
    paged = rows[offset : offset + limit]
    rep_all["results"] = paged
    rep_all["total_count"] = len(rows)
    rep_all["limit"] = limit
    rep_all["offset"] = offset
    rep_all["returned_count"] = len(paged)
    _with_state_filters_query_echo(rep_all, job_state=job_state, include_dismissed=include_dismissed)
    return rep_all


@router.get(
    "/jobs/state",
    response_model=JobStateResponse,
    responses={422: {"model": ErrorResponse}},
)
def get_job_state_endpoint(
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    job_url: str = Query(..., min_length=1),
) -> dict:
    try:
        rep = get_job_state(db_path=job_state_db_path, job_url=job_url, user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"job_url": rep["job_url"], "state": rep["state"], "updated_at": rep.get("updated_at") or None}


@router.post(
    "/jobs/state",
    response_model=JobStateResponse,
    responses={422: {"model": ErrorResponse}},
)
def post_job_state_endpoint(
    payload: JobStateSetRequest,
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        rep = set_job_state(
            db_path=job_state_db_path,
            job_url=payload.job_url,
            state=payload.state,
            user_id=current_user.user_id,
            user_email=current_user.email,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"job_url": rep["job_url"], "state": rep["state"], "updated_at": rep["updated_at"]}


@router.post(
    "/jobs/state/clear",
    response_model=JobStateClearResponse,
    responses={422: {"model": ErrorResponse}},
)
def post_job_state_clear_endpoint(
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    job_url: str = Query(..., min_length=1),
) -> dict:
    try:
        return clear_job_state(db_path=job_state_db_path, job_url=job_url, user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/jobs/count", response_model=JobCountResponse)
def get_jobs_count(
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    normalized_title: str | None = None,
    role_family: str | None = None,
    language_bucket: str | None = None,
    location_type: str | None = None,
    employment_type: str | None = None,
    has_salary: bool | None = None,
    has_skills: bool | None = None,
    title_is_other: bool | None = None,
    skills_contains: list[str] | None = Query(default=None),
    salary_currency: str | None = Query(default=None, max_length=8),
    job_state: str | None = Query(default=None),
    include_dismissed: bool = Query(default=True),
) -> dict:
    query = QueryParams(
        normalized_title=normalized_title,
        role_family=role_family,
        language_bucket=language_bucket,
        location_type=location_type,
        employment_type=employment_type,
        has_salary=has_salary,
        has_skills=has_skills,
        title_is_other=title_is_other,
        skills_contains=skills_contains,
        salary_currency=salary_currency,
        sort_by="published_at_desc",
        limit=None,
    )
    needs_state_filter = job_state is not None or not include_dismissed
    if not needs_state_filter:
        rep = count_jobs(input_path=dataset_path, query=query, sqlite_path=sqlite_path)
        _with_state_filters_query_echo(rep, job_state=job_state, include_dismissed=include_dismissed)
        return rep

    rep_all = list_jobs(
        input_path=dataset_path,
        query=query,
        limit=1_000_000,
        offset=0,
        sqlite_path=sqlite_path,
    )
    rows = _attach_job_states(rep_all.get("results", []), job_state_db_path, user_id=current_user.user_id)
    rows = _filter_rows_by_state(rows, job_state=job_state, include_dismissed=include_dismissed)
    return {
        "operation": "count_jobs",
        "input_path": rep_all.get("input_path", dataset_path),
        "backend": rep_all.get("backend", "jsonl"),
        "query": {
            **(rep_all.get("query") or {}),
            "job_state": job_state,
            "include_dismissed": include_dismissed,
        },
        "count": len(rows),
    }


@router.get("/facets", response_model=FacetsResponse)
def get_facets_endpoint(
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    normalized_title: str | None = None,
    role_family: str | None = None,
    language_bucket: str | None = None,
    location_type: str | None = None,
    employment_type: str | None = None,
    has_salary: bool | None = None,
    has_skills: bool | None = None,
    title_is_other: bool | None = None,
    skills_contains: list[str] | None = Query(default=None),
    salary_currency: str | None = Query(default=None, max_length=8),
) -> dict:
    query = QueryParams(
        normalized_title=normalized_title,
        role_family=role_family,
        language_bucket=language_bucket,
        location_type=location_type,
        employment_type=employment_type,
        has_salary=has_salary,
        has_skills=has_skills,
        title_is_other=title_is_other,
        skills_contains=skills_contains,
        salary_currency=salary_currency,
        sort_by="published_at_desc",
        limit=None,
    )
    return get_facets(
        input_path=dataset_path,
        query=query,
        sqlite_path=sqlite_path,
    )


@router.get("/packs", response_model=PacksListResponse)
def get_packs() -> dict:
    packs = get_query_packs()
    return {
        "packs": [
            {
                "name": p.name,
                "description": p.description,
                "quality": p.quality,
                "tradeoff": p.tradeoff,
            }
            for p in sorted(packs.values(), key=lambda x: x.name)
        ]
    }


@router.get(
    "/packs/{pack_name}",
    response_model=PackRunResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_pack(
    pack_name: str,
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    job_state: str | None = Query(default=None),
    include_dismissed: bool = Query(default=True),
    limit: int = Query(default=20, ge=0, le=1000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    try:
        needs_state_filter = job_state is not None or not include_dismissed
        rep = run_pack(
            input_path=dataset_path,
            pack_name=pack_name,
            limit=1_000_000 if needs_state_filter else limit,
            offset=0 if needs_state_filter else offset,
            sqlite_path=sqlite_path,
        )
        rows = _attach_job_states(rep.get("results", []), job_state_db_path, user_id=current_user.user_id)
        rows = _filter_rows_by_state(rows, job_state=job_state, include_dismissed=include_dismissed)
        if needs_state_filter:
            rep["total_count"] = len(rows)
            rows = rows[offset : offset + limit]
            rep["limit"] = limit
            rep["offset"] = offset
        rep["results"] = rows
        rep["returned_count"] = len(rows)
        return rep
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/packs/{pack_name}/count",
    response_model=PackCountResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_pack_count(
    pack_name: str,
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    job_state: str | None = Query(default=None),
    include_dismissed: bool = Query(default=True),
) -> dict:
    try:
        needs_state_filter = job_state is not None or not include_dismissed
        if not needs_state_filter:
            return count_pack(input_path=dataset_path, pack_name=pack_name, sqlite_path=sqlite_path)
        rep = run_pack(
            input_path=dataset_path,
            pack_name=pack_name,
            limit=1_000_000,
            offset=0,
            sqlite_path=sqlite_path,
        )
        rows = _attach_job_states(rep.get("results", []), job_state_db_path, user_id=current_user.user_id)
        rows = _filter_rows_by_state(rows, job_state=job_state, include_dismissed=include_dismissed)
        return {
            "operation": "count_pack",
            "input_path": rep.get("input_path", dataset_path),
            "backend": rep.get("backend", "jsonl"),
            "pack_name": pack_name,
            "count": len(rows),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/saved-searches", response_model=SavedSearchListResponse)
def get_saved_searches(
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    lifecycle: str = Query(default="all"),
) -> dict:
    try:
        return {"saved_searches": list_saved_searches(db_path=saved_db_path, user_id=current_user.user_id, lifecycle=lifecycle)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/saved-searches",
    response_model=SavedSearchMutationResponse,
    responses={422: {"model": ErrorResponse}},
)
def post_saved_search(
    payload: SavedSearchCreateRequest,
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        saved = create_saved_search(
            db_path=saved_db_path,
            name=payload.name,
            query_type=payload.query_type,
            filters_json=payload.filters_json,
            pack_name=payload.pack_name,
            frequency=payload.frequency,
            is_enabled=payload.is_enabled,
            lifecycle=payload.lifecycle,
            user_id=current_user.user_id,
            user_email=current_user.email,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"saved_search": saved}


@router.post(
    "/saved-searches/{search_id}/update",
    response_model=SavedSearchMutationResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def post_saved_search_update(
    search_id: str,
    payload: SavedSearchUpdateRequest,
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        saved = update_saved_search(
            db_path=saved_db_path,
            search_id=search_id,
            name=payload.name,
            query_type=payload.query_type,
            filters_json=payload.filters_json,
            pack_name=payload.pack_name,
            frequency=payload.frequency,
            is_enabled=payload.is_enabled,
            lifecycle=payload.lifecycle,
            user_id=current_user.user_id,
        )
    except ValueError as exc:
        msg = str(exc)
        status = 404 if "not found" in msg else 422
        raise HTTPException(status_code=status, detail=msg) from exc
    return {"saved_search": saved}


@router.post(
    "/saved-searches/{search_id}/delete",
    response_model=SavedSearchDeleteResponse,
    responses={404: {"model": ErrorResponse}},
)
def post_saved_search_delete(
    search_id: str,
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        return delete_saved_search(db_path=saved_db_path, search_id=search_id, user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/saved-searches/{search_id}/enable",
    response_model=SavedSearchMutationResponse,
    responses={404: {"model": ErrorResponse}},
)
def post_saved_search_enable(
    search_id: str,
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        saved = enable_saved_search(db_path=saved_db_path, search_id=search_id, user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"saved_search": saved}


@router.post(
    "/saved-searches/{search_id}/disable",
    response_model=SavedSearchMutationResponse,
    responses={404: {"model": ErrorResponse}},
)
def post_saved_search_disable(
    search_id: str,
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        saved = disable_saved_search(db_path=saved_db_path, search_id=search_id, user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"saved_search": saved}


@router.post(
    "/saved-searches/{search_id}/archive",
    response_model=SavedSearchMutationResponse,
    responses={404: {"model": ErrorResponse}},
)
def post_saved_search_archive(
    search_id: str,
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        saved = archive_saved_search(db_path=saved_db_path, search_id=search_id, user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"saved_search": saved}


@router.post(
    "/saved-searches/{search_id}/restore",
    response_model=SavedSearchMutationResponse,
    responses={404: {"model": ErrorResponse}},
)
def post_saved_search_restore(
    search_id: str,
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        saved = restore_saved_search(db_path=saved_db_path, search_id=search_id, user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"saved_search": saved}


@router.post(
    "/saved-searches/{search_id}/run",
    response_model=SavedSearchRunResponse,
    responses={404: {"model": ErrorResponse}},
)
def post_saved_search_run(
    search_id: str,
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    limit: int = Query(default=100, ge=0, le=10000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    try:
        rep = run_saved_search(
            db_path=saved_db_path,
            search_id=search_id,
            indexed_input_path=dataset_path,
            indexed_sqlite_path=sqlite_path,
            limit=limit,
            offset=offset,
            user_id=current_user.user_id,
        )
        run_result = rep.get("run_result")
        if isinstance(run_result, dict):
            run_result["results"] = _attach_job_states(
                run_result.get("results", []),
                job_state_db_path,
                user_id=current_user.user_id,
            )
        return rep
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/saved-searches/{search_id}/results",
    response_model=SavedSearchResultsResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_saved_search_results_endpoint(
    search_id: str,
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    mode: str = Query(default="current"),
    scan_limit: int = Query(default=5000, ge=1, le=100000),
    limit: int = Query(default=100, ge=0, le=10000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"current", "new"}:
        raise HTTPException(status_code=422, detail=f"invalid mode: {mode}")
    try:
        rep = get_saved_search_results(
            db_path=saved_db_path,
            search_id=search_id,
            indexed_input_path=dataset_path,
            indexed_sqlite_path=sqlite_path,
            limit=limit,
            offset=offset,
            new_only=(normalized_mode == "new"),
            scan_limit=scan_limit,
            user_id=current_user.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    results = _attach_job_states(rep.get("results", []), job_state_db_path, user_id=current_user.user_id)
    rep["results"] = results
    rep["returned_count"] = len(results)
    return rep


@router.post(
    "/saved-searches/{search_id}/check-new",
    response_model=SavedSearchCheckNewResponse,
    responses={404: {"model": ErrorResponse}},
)
def post_saved_search_check_new(
    search_id: str,
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    job_state_db_path: Annotated[str, Depends(get_job_state_db_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    scan_limit: int = Query(default=5000, ge=0, le=100000),
    limit: int = Query(default=100, ge=0, le=10000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    try:
        rep = check_new_matches(
            db_path=saved_db_path,
            search_id=search_id,
            indexed_input_path=dataset_path,
            indexed_sqlite_path=sqlite_path,
            scan_limit=scan_limit,
            return_limit=limit,
            offset=offset,
            user_id=current_user.user_id,
        )
        rep["current_results"] = _attach_job_states(
            rep.get("current_results", []),
            job_state_db_path,
            user_id=current_user.user_id,
        )
        rep["new_results"] = _attach_job_states(
            rep.get("new_results", []),
            job_state_db_path,
            user_id=current_user.user_id,
        )
        return rep
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/alerts/run-all", response_model=AlertRunAllResponse)
def post_alerts_run_all(
    dataset_path: Annotated[str, Depends(get_dataset_path)],
    saved_db_path: Annotated[str, Depends(get_saved_db_path)],
    runs_dir: Annotated[str, Depends(get_alert_runs_dir)],
    sqlite_path: Annotated[str | None, Depends(get_sqlite_path)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    scan_limit: int = Query(default=5000, ge=0, le=100000),
    limit: int = Query(default=200, ge=0, le=10000),
    sample_size: int = Query(default=5, ge=0, le=100),
    send_email: bool = Query(default=False),
    email_to: str | None = Query(default=None),
) -> dict:
    rep = run_enabled_saved_searches(
        saved_db_path=saved_db_path,
        indexed_input_path=dataset_path,
        indexed_sqlite_path=sqlite_path,
        outdir=runs_dir,
        scan_limit=scan_limit,
        return_limit=limit,
        sample_size=sample_size,
        user_id=current_user.user_id,
        user_email=current_user.email,
    )
    if not send_email:
        rep["email_delivery"] = None
        return rep

    if not email_to:
        try:
            settings = get_user_settings(db_path=saved_db_path, user_id=current_user.user_id)
            email_to = str(settings.get("default_alert_email") or "").strip() or None
        except ValueError:
            email_to = None
    if not email_to:
        raise HTTPException(status_code=422, detail="email_to is required when send_email=true and no default_alert_email is set")
    try:
        smtp = SMTPConfig.from_env()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    rep["email_delivery"] = send_email_alerts_from_run(
        run_json_path=rep["json_report_path"],
        to_email=email_to,
        smtp_config=smtp,
    )
    persist_email_delivery_to_run(run_json_path=rep["json_report_path"], email_delivery=rep["email_delivery"])
    return rep


@router.get("/alerts/runs", response_model=AlertRunsListResponse)
def get_alerts_runs(
    runs_dir: Annotated[str, Depends(get_alert_runs_dir)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    return {"runs": list_alert_runs(runs_dir=runs_dir, user_id=current_user.user_id)}


@router.get(
    "/alerts/runs/{run_id}",
    response_model=AlertRunDetailResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_alerts_run_detail(
    run_id: str,
    runs_dir: Annotated[str, Depends(get_alert_runs_dir)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    try:
        return get_alert_run_detail(runs_dir=runs_dir, run_id=run_id, user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/alerts/summary", response_model=AlertSummaryResponse)
def get_alerts_summary(
    runs_dir: Annotated[str, Depends(get_alert_runs_dir)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    recent_limit: int = Query(default=20, ge=1, le=500),
    sample_new_searches: int = Query(default=5, ge=1, le=100),
) -> dict:
    return get_alert_runs_summary(
        runs_dir=runs_dir,
        user_id=current_user.user_id,
        recent_limit=recent_limit,
        sample_new_searches=sample_new_searches,
    )
