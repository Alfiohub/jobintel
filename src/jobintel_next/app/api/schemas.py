from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


SortBy = Literal["published_at_desc", "updated_at_desc", "url"]


class QueryEcho(BaseModel):
    normalized_title: str | None = None
    role_family: str | None = None
    language_bucket: str | None = None
    location_type: str | None = None
    employment_type: str | None = None
    has_salary: bool | None = None
    has_skills: bool | None = None
    title_is_other: bool | None = None
    skills_contains: list[str]
    salary_currency: str | None = None
    job_state: str | None = None
    include_dismissed: bool = True
    sort_by: str
    limit: int | None = None


class JobListResponse(BaseModel):
    operation: str
    input_path: str
    query: QueryEcho
    total_count: int
    limit: int
    offset: int
    returned_count: int
    results: list[dict[str, Any]]


class JobCountResponse(BaseModel):
    operation: str
    input_path: str
    query: QueryEcho
    count: int


class PackSummary(BaseModel):
    name: str
    description: str
    quality: str
    tradeoff: str


class PacksListResponse(BaseModel):
    packs: list[PackSummary]


class PackClauseResponse(BaseModel):
    clause_name: str
    query: dict[str, Any]
    matched_rows: int


class PackRunResponse(BaseModel):
    operation: str
    input_path: str
    pack_name: str
    description: str
    quality: str
    tradeoff: str
    clauses: list[PackClauseResponse]
    total_count: int
    limit: int
    offset: int
    returned_count: int
    results: list[dict[str, Any]]


class PackCountResponse(BaseModel):
    operation: str
    input_path: str
    pack_name: str
    count: int


class HealthResponse(BaseModel):
    status: str
    dataset_path: str


class ErrorResponse(BaseModel):
    detail: str
    model_config = ConfigDict(extra="forbid")


class FacetBucket(BaseModel):
    value: Any
    count: int


class FacetsResponse(BaseModel):
    operation: str
    input_path: str
    backend: str
    query: QueryEcho
    total_count: int
    facets: dict[str, list[FacetBucket]]


QueryType = Literal["filters", "pack"]
SavedSearchFrequency = Literal["manual", "daily", "twice_daily"]
SavedSearchLifecycle = Literal["active", "disabled", "archived"]


class SavedSearchCreateRequest(BaseModel):
    name: str
    query_type: QueryType
    filters_json: str | None = None
    pack_name: str | None = None
    frequency: SavedSearchFrequency = "daily"
    is_enabled: bool = True
    lifecycle: SavedSearchLifecycle | None = None


class SavedSearchUpdateRequest(BaseModel):
    name: str
    query_type: QueryType
    filters_json: str | None = None
    pack_name: str | None = None
    frequency: SavedSearchFrequency = "daily"
    is_enabled: bool = True
    lifecycle: SavedSearchLifecycle | None = None


class SavedSearchResponse(BaseModel):
    search_id: str
    user_id: str
    name: str
    query_type: QueryType
    filters_json: str | None = None
    pack_name: str | None = None
    frequency: SavedSearchFrequency = "daily"
    lifecycle: SavedSearchLifecycle = "active"
    is_enabled: bool
    created_at: str
    updated_at: str
    last_run_at: str | None = None
    last_seen_job_url: str | None = None


class SavedSearchListResponse(BaseModel):
    saved_searches: list[SavedSearchResponse]


class SavedSearchMutationResponse(BaseModel):
    saved_search: SavedSearchResponse


class SavedSearchRunResponse(BaseModel):
    saved_search: SavedSearchResponse
    run_result: dict[str, Any]


class SavedSearchCheckNewResponse(BaseModel):
    saved_search: SavedSearchResponse
    current_count: int
    new_count: int
    current_results: list[dict[str, Any]]
    new_results: list[dict[str, Any]]
    scan_limit: int
    return_limit: int
    offset: int


class SavedSearchDeleteResponse(BaseModel):
    deleted: bool
    saved_search: SavedSearchResponse


class SavedSearchResultsResponse(BaseModel):
    saved_search: SavedSearchResponse
    mode: str
    current_count: int
    new_count: int | None = None
    limit: int
    offset: int
    returned_count: int
    results: list[dict[str, Any]]


class AlertRunSummary(BaseModel):
    run_id: str
    user_id: str | None = None
    run_timestamp: str | None = None
    searches_total: int | None = None
    searches_enabled: int | None = None
    processed_ok: int | None = None
    processed_error: int | None = None
    total_new_matches: int | None = None
    json_report_path: str
    md_report_path: str


class AlertRunAllResponse(BaseModel):
    run_id: str
    user_id: str | None = None
    run_timestamp: str
    saved_db_path: str
    indexed_input_path: str
    indexed_sqlite_path: str | None = None
    searches_total: int
    searches_enabled: int
    searches_disabled: int
    processed_ok: int
    processed_error: int
    total_new_matches: int
    results: list[dict[str, Any]]
    json_report_path: str
    md_report_path: str
    email_delivery: dict[str, Any] | None = None


class AlertRunsListResponse(BaseModel):
    runs: list[AlertRunSummary]


class AlertRunDetailResponse(BaseModel):
    run_id: str
    user_id: str | None = None
    run_timestamp: str
    saved_db_path: str
    indexed_input_path: str
    indexed_sqlite_path: str | None = None
    searches_total: int
    searches_enabled: int
    searches_disabled: int
    processed_ok: int
    processed_error: int
    total_new_matches: int
    results: list[dict[str, Any]]
    json_report_path: str
    md_report_path: str
    email_delivery: dict[str, Any] | None = None


class RecentSearchWithNewMatches(BaseModel):
    run_id: str | None = None
    search_id: str | None = None
    name: str | None = None
    new_matches_count: int
    query_type: str | None = None


class AlertSummaryResponse(BaseModel):
    runs_count: int
    latest_run_id: str | None = None
    latest_run_total_new_matches: int | None = None
    recent_error_runs_count: int
    recent_ok_runs_count: int
    recent_searches_with_new_matches: list[RecentSearchWithNewMatches]


JobStateValue = Literal["new", "seen", "saved", "dismissed"]


class JobStateSetRequest(BaseModel):
    job_url: str
    state: JobStateValue


class JobStateResponse(BaseModel):
    job_url: str
    state: JobStateValue
    updated_at: str | None = None


class JobStateClearResponse(BaseModel):
    job_url: str
    deleted: bool
