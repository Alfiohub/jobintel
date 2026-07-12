from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .config import apply_env_overrides_to_sources, load_config, load_sources_from_yaml
from .ingestion.collectors.greenhouse_collector import build_collector
from .pipelines.cleaning.run import run_cleaning_stage
from .pipelines.extraction.run import run_extraction_stage
from .pipelines.language.eval import run_language_eval
from .pipelines.language.gate import run_language_gate
from .pipelines.indexed.run import run_indexed_stage
from .pipelines.retrieval import (
    QueryParams,
    build_query_packs_report,
    build_retrieval_layer_report,
    list_query_pack_names,
    run_query_pack,
    run_retrieval_query,
)
from .pipelines.titles.eval import run_title_eval
from .pipelines.titles.run import run_title_stage
from .product.alerts import (
    SMTPConfig,
    cleanup_alert_runs,
    persist_digest_delivery_to_run,
    resend_digest_from_run_artifact,
    send_digest_email_from_run,
    send_email_alerts_from_run,
)
from .product.auth import get_user_settings
from .product.auth import create_local_user
from .product.attention import build_attention_items_for_user
from .product.saved_searches import (
    check_new_matches,
    create_saved_search,
    disable_saved_search,
    enable_saved_search,
    list_saved_searches,
    run_due_saved_searches,
    run_enabled_saved_searches,
    run_saved_search,
)
from .serving import build_serving_layer_report, count_jobs, count_pack, list_jobs, run_pack
from .source_registry import build_collectors_from_sources
from .storage import build_sqlite_index


def _write_rows(rows: list[dict[str, Any]], out_path: str | Path) -> None:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_ingest_run(config_path: str | Path, out_path: str | Path) -> int:
    sources = load_sources_from_yaml(config_path)
    sources = apply_env_overrides_to_sources(sources)
    collectors = build_collectors_from_sources(sources)

    rows: list[dict[str, Any]] = []
    for collector in collectors:
        rows.extend(asdict(job) for job in collector.fetch())

    _write_rows(rows, out_path)
    print(f"collectors={len(collectors)}")
    print(f"rows={len(rows)}")
    print(f"out={Path(out_path)}")
    return 0


def run_ingest_export(
    *,
    source: str,
    board: str,
    out_path: str | Path,
    content: bool,
    timeout_s: int | None,
    retries: int | None,
    max_concurrency: int | None,
) -> int:
    if source != "greenhouse":
        raise ValueError(f"unsupported source: {source}")
    env_cfg = load_config()
    collector = build_collector(
        {
            "enabled": True,
            "boards": [board],
            "content": content,
            "timeout_s": timeout_s if timeout_s is not None else env_cfg.greenhouse_timeout_sec,
            "retries": retries if retries is not None else env_cfg.greenhouse_max_retries,
            "max_concurrency": (
                max_concurrency if max_concurrency is not None else env_cfg.greenhouse_max_concurrency
            ),
        }
    )
    if collector is None:
        raise RuntimeError("invalid collector configuration")
    jobs = collector.fetch()
    _write_rows([asdict(job) for job in jobs], out_path)
    print(f"source={source}")
    print(f"board={board}")
    print(f"rows={len(jobs)}")
    print(f"out={Path(out_path)}")
    return 0


def _cmd_ingest_run(args: argparse.Namespace) -> int:
    return run_ingest_run(args.config, args.out)


def _cmd_ingest_export(args: argparse.Namespace) -> int:
    return run_ingest_export(
        source=args.source,
        board=args.board,
        out_path=args.out,
        content=not args.no_content,
        timeout_s=args.timeout_s,
        retries=args.retries,
        max_concurrency=args.max_concurrency,
    )


def _cmd_language_eval(args: argparse.Namespace) -> int:
    report = run_language_eval(
        input_path=args.input,
        outdir=args.outdir,
        limit=args.limit,
        sample_size=args.sample_size,
        top_k=args.top_k,
    )
    print(f"rows_total={report['rows_total']}")
    print(f"rows_en={report['rows_en']}")
    print(f"rows_non_en={report['rows_non_en']}")
    print(f"rows_unknown={report['rows_unknown']}")
    print(f"out_json={Path(args.outdir) / 'language_eval_step6.json'}")
    print(f"out_md={Path(args.outdir) / 'language_eval_step6.md'}")
    return 0


def _cmd_language_gate(args: argparse.Namespace) -> int:
    report = run_language_gate(
        input_path=args.input,
        outdir=args.outdir,
        report_dir=args.report_dir,
        limit=args.limit,
        top_k=args.top_k,
    )
    print(f"rows_total={report['rows_total']}")
    print(f"rows_en={report['rows_en']}")
    print(f"rows_non_en={report['rows_non_en']}")
    print(f"rows_unknown={report['rows_unknown']}")
    print(f"out_en={report['output_files']['en']}")
    print(f"out_non_en={report['output_files']['non_en']}")
    print(f"out_unknown={report['output_files']['unknown']}")
    print(f"report_json={Path(args.report_dir) / 'language_gate_step7.json'}")
    print(f"report_md={Path(args.report_dir) / 'language_gate_step7.md'}")
    return 0


def _cmd_cleaning_run(args: argparse.Namespace) -> int:
    report = run_cleaning_stage(
        input_path=args.input,
        output_path=args.out,
        report_dir=args.report_dir,
        limit=args.limit,
        sample_size=args.sample_size,
    )
    print(f"rows_total={report['rows_total']}")
    print(f"invalid_rows={report['invalid_rows']}")
    print(f"out={report['output_path']}")
    print(f"report_json={Path(args.report_dir) / 'cleaning_stage_step8.json'}")
    print(f"report_md={Path(args.report_dir) / 'cleaning_stage_step8.md'}")
    return 0


def _cmd_extraction_run(args: argparse.Namespace) -> int:
    report = run_extraction_stage(
        input_path=args.input,
        output_path=args.out,
        report_dir=args.report_dir,
        limit=args.limit,
        sample_size=args.sample_size,
    )
    print(f"rows_total={report['rows_total']}")
    print(f"invalid_rows={report['invalid_rows']}")
    print(f"out={report['output_path']}")
    print(f"report_json={Path(args.report_dir) / 'extraction_stage_step9.json'}")
    print(f"report_md={Path(args.report_dir) / 'extraction_stage_step9.md'}")
    return 0


def _cmd_titles_run(args: argparse.Namespace) -> int:
    report = run_title_stage(
        input_cleaned_path=args.input_cleaned,
        input_extracted_path=args.input_extracted,
        output_path=args.out,
        report_dir=args.report_dir,
        limit=args.limit,
        top_k_other=args.top_k_other,
    )
    print(f"rows_total={report['rows_total']}")
    print(f"invalid_rows={report['invalid_rows']}")
    print(f"out={report['output_path']}")
    print(f"report_json={Path(args.report_dir) / 'title_stage_step12.json'}")
    print(f"report_md={Path(args.report_dir) / 'title_stage_step12.md'}")
    return 0


def _cmd_titles_eval(args: argparse.Namespace) -> int:
    report = run_title_eval(
        input_path=args.input,
        outdir=args.outdir,
        limit=args.limit,
        sample_size=args.sample_size,
        top_k=args.top_k,
    )
    print(f"rows_total={report['rows_total']}")
    print(f"invalid_rows={report['invalid_rows']}")
    print(f"out_json={Path(args.outdir) / 'title_eval_step13.json'}")
    print(f"out_md={Path(args.outdir) / 'title_eval_step13.md'}")
    print(f"out_clusters={Path(args.outdir) / 'title_other_clusters_step13.json'}")
    return 0


def _cmd_indexed_run(args: argparse.Namespace) -> int:
    report = run_indexed_stage(
        input_canonical_path=args.input_canonical,
        input_language_path=args.input_language,
        input_cleaned_path=args.input_cleaned,
        input_extracted_path=args.input_extracted,
        input_titled_path=args.input_titled,
        output_path=args.out,
        report_dir=args.report_dir,
        limit=args.limit,
        sample_size=args.sample_size,
    )
    print(f"rows_total={report['rows_total']}")
    print(f"missing_components={report['missing_components']}")
    print(f"out={report['output_path']}")
    print(f"report_json={Path(args.report_dir) / 'indexed_job_stage_step14.json'}")
    print(f"report_md={Path(args.report_dir) / 'indexed_job_stage_step14.md'}")
    return 0


def _parse_optional_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    v = value.strip().lower()
    if v in {"true", "1", "yes"}:
        return True
    if v in {"false", "0", "no"}:
        return False
    raise ValueError(f"invalid bool value: {value}")


def _cmd_retrieval_query(args: argparse.Namespace) -> int:
    query = QueryParams(
        normalized_title=args.normalized_title,
        role_family=args.role_family,
        language_bucket=args.language_bucket,
        location_type=args.location_type,
        employment_type=args.employment_type,
        has_salary=_parse_optional_bool(args.has_salary),
        has_skills=_parse_optional_bool(args.has_skills),
        title_is_other=_parse_optional_bool(args.title_is_other),
        skills_contains=args.skills_contains,
        salary_currency=args.salary_currency,
        sort_by=args.sort_by,
        limit=args.limit,
    )
    report = run_retrieval_query(
        input_path=args.input,
        query=query,
        output_path=args.out,
    )
    print(f"rows_total={report['rows_total']}")
    print(f"matched_rows={report['matched_rows']}")
    print(f"invalid_rows={report['invalid_rows']}")
    if args.out:
        print(f"out={Path(args.out)}")
    else:
        for row in report["results"]:
            print(json.dumps(row, ensure_ascii=False))
    return 0


def _cmd_retrieval_report(args: argparse.Namespace) -> int:
    report = build_retrieval_layer_report(input_path=args.input, report_dir=args.report_dir)
    print(f"input={report['input_path']}")
    print(f"report_json={Path(args.report_dir) / 'retrieval_layer_step15.json'}")
    print(f"report_md={Path(args.report_dir) / 'retrieval_layer_step15.md'}")
    return 0


def _cmd_retrieval_pack(args: argparse.Namespace) -> int:
    if args.pack == "all":
        report = build_query_packs_report(
            input_path=args.input,
            report_dir=args.report_dir,
            sample_limit=args.limit,
        )
        print(f"input={report['input_path']}")
        print(f"report_json={Path(args.report_dir) / 'query_packs_step18.json'}")
        print(f"report_md={Path(args.report_dir) / 'query_packs_step18.md'}")
        return 0

    report = run_query_pack(
        input_path=args.input,
        pack_name=args.pack,
        limit=args.limit,
        output_path=args.out,
    )
    print(f"pack={report['pack_name']}")
    print(f"matched_rows={report['matched_rows']}")
    if args.out:
        print(f"out={Path(args.out)}")
    else:
        for row in report["results"]:
            print(json.dumps(row, ensure_ascii=False))
    return 0


def _cmd_serve_query(args: argparse.Namespace) -> int:
    query = QueryParams(
        normalized_title=args.normalized_title,
        role_family=args.role_family,
        language_bucket=args.language_bucket,
        location_type=args.location_type,
        employment_type=args.employment_type,
        has_salary=_parse_optional_bool(args.has_salary),
        has_skills=_parse_optional_bool(args.has_skills),
        title_is_other=_parse_optional_bool(args.title_is_other),
        skills_contains=args.skills_contains,
        salary_currency=args.salary_currency,
        sort_by=args.sort_by,
        limit=None,
    )
    report = list_jobs(
        input_path=args.input,
        query=query,
        limit=args.limit,
        offset=args.offset,
        sqlite_path=args.sqlite,
    )
    if args.out:
        _write_rows(report["results"], args.out)
        print(f"out={Path(args.out)}")
        print(f"total_count={report['total_count']}")
        print(f"returned_count={report['returned_count']}")
        return 0
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def _cmd_serve_count(args: argparse.Namespace) -> int:
    query = QueryParams(
        normalized_title=args.normalized_title,
        role_family=args.role_family,
        language_bucket=args.language_bucket,
        location_type=args.location_type,
        employment_type=args.employment_type,
        has_salary=_parse_optional_bool(args.has_salary),
        has_skills=_parse_optional_bool(args.has_skills),
        title_is_other=_parse_optional_bool(args.title_is_other),
        skills_contains=args.skills_contains,
        salary_currency=args.salary_currency,
        sort_by="published_at_desc",
        limit=None,
    )
    report = count_jobs(input_path=args.input, query=query, sqlite_path=args.sqlite)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def _cmd_serve_pack(args: argparse.Namespace) -> int:
    report = run_pack(
        input_path=args.input,
        pack_name=args.pack,
        limit=args.limit,
        offset=args.offset,
        sqlite_path=args.sqlite,
    )
    if args.out:
        _write_rows(report["results"], args.out)
        print(f"out={Path(args.out)}")
        print(f"total_count={report['total_count']}")
        print(f"returned_count={report['returned_count']}")
        return 0
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def _cmd_serve_pack_count(args: argparse.Namespace) -> int:
    report = count_pack(input_path=args.input, pack_name=args.pack, sqlite_path=args.sqlite)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def _cmd_storage_build_index(args: argparse.Namespace) -> int:
    report = build_sqlite_index(
        input_path=args.input,
        sqlite_path=args.sqlite,
        batch_size=args.batch_size,
    )
    print(f"input={report['input_path']}")
    print(f"sqlite={report['sqlite_path']}")
    print(f"rows_total={report['rows_total']}")
    print(f"invalid_rows={report['invalid_rows']}")
    print(f"inserted_rows={report['inserted_rows']}")
    return 0


def _cmd_saved_search_create(args: argparse.Namespace) -> int:
    rep = create_saved_search(
        db_path=args.saved_db,
        name=args.name,
        query_type=args.query_type,
        filters_json=args.filters_json,
        pack_name=args.pack_name,
        frequency=args.frequency,
        is_enabled=not args.disabled,
        user_id=args.user_id,
        user_email=args.user_email,
    )
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_saved_search_list(args: argparse.Namespace) -> int:
    rep = list_saved_searches(db_path=args.saved_db, user_id=args.user_id)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_saved_search_enable(args: argparse.Namespace) -> int:
    rep = enable_saved_search(db_path=args.saved_db, search_id=args.id, user_id=args.user_id)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_saved_search_disable(args: argparse.Namespace) -> int:
    rep = disable_saved_search(db_path=args.saved_db, search_id=args.id, user_id=args.user_id)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_saved_search_run(args: argparse.Namespace) -> int:
    rep = run_saved_search(
        db_path=args.saved_db,
        search_id=args.id,
        indexed_input_path=args.input,
        indexed_sqlite_path=args.sqlite,
        limit=args.limit,
        offset=args.offset,
        user_id=args.user_id,
    )
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_saved_search_check_new(args: argparse.Namespace) -> int:
    rep = check_new_matches(
        db_path=args.saved_db,
        search_id=args.id,
        indexed_input_path=args.input,
        indexed_sqlite_path=args.sqlite,
        scan_limit=args.scan_limit,
        return_limit=args.limit,
        offset=args.offset,
        user_id=args.user_id,
    )
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_saved_search_run_all(args: argparse.Namespace) -> int:
    rep = run_enabled_saved_searches(
        saved_db_path=args.saved_db,
        indexed_input_path=args.input,
        indexed_sqlite_path=args.sqlite,
        outdir=args.outdir,
        scan_limit=args.scan_limit,
        return_limit=args.limit,
        sample_size=args.sample_size,
        user_id=args.user_id,
        user_email=args.user_email,
    )
    print(f"run_id={rep['run_id']}")
    print(f"searches_enabled={rep['searches_enabled']}")
    print(f"processed_ok={rep['processed_ok']}")
    print(f"processed_error={rep['processed_error']}")
    print(f"total_new_matches={rep['total_new_matches']}")
    print(f"report_json={rep['json_report_path']}")
    print(f"report_md={rep['md_report_path']}")
    return 0


def _cmd_alerts_run_due(args: argparse.Namespace) -> int:
    rep = run_due_saved_searches(
        saved_db_path=args.saved_db,
        indexed_input_path=args.input,
        indexed_sqlite_path=args.sqlite,
        outdir=args.outdir,
        scan_limit=args.scan_limit,
        return_limit=args.limit,
        sample_size=args.sample_size,
        user_id=args.user_id,
        user_email=args.user_email,
    )
    if not bool(rep.get("lock_acquired", True)):
        print("status=skipped_locked")
        print(f"lock_path={rep.get('lock_path')}")
        print("message=another run-due execution is already in progress")
        return 2

    digest_delivery = None
    if args.send_digest_email:
        settings = None
        try:
            settings = get_user_settings(db_path=args.saved_db, user_id=args.user_id)
        except ValueError:
            settings = None
        to_email = (args.email_to or "").strip() or None
        if to_email is None:
            to_email = str((settings or {}).get("default_alert_email") or "").strip() or None
        if to_email is None:
            digest_delivery = {
                "attempted_count": 0,
                "sent_count": 0,
                "skipped_count": 1,
                "skip_reason": "missing_default_alert_email",
                "email_attempted": False,
                "email_sent": False,
                "email_skipped": 1,
                "email_error": False,
                "errors": [],
            }
        else:
            try:
                smtp = SMTPConfig.from_env()
                include_attention = bool((settings or {}).get("digest_include_attention", True))
                attention_items = []
                if include_attention:
                    attention_items = build_attention_items_for_user(
                        saved_db_path=args.saved_db,
                        job_state_db_path=getattr(args, "job_state_db", "data/jobs/job_state.db"),
                        runs_dir=args.outdir,
                        indexed_input_path=args.input,
                        indexed_sqlite_path=args.sqlite,
                        user_id=args.user_id,
                        max_items=5,
                    )
                digest_delivery = send_digest_email_from_run(
                    run_json_path=rep["json_report_path"],
                    to_email=to_email,
                    smtp_config=smtp,
                    attention_items=attention_items,
                )
            except Exception as exc:
                digest_delivery = {
                    "to_email": to_email,
                    "attempted_count": 0,
                    "sent_count": 0,
                    "skipped_count": 1,
                    "skip_reason": f"smtp_not_configured_or_failed: {exc}",
                    "email_attempted": False,
                    "email_sent": False,
                    "email_skipped": 1,
                    "email_error": True,
                    "errors": [{"error": str(exc)}],
                }
        persist_digest_delivery_to_run(
            run_json_path=rep["json_report_path"],
            digest_delivery=digest_delivery,
        )
        rep["digest_email_delivery"] = digest_delivery

    print(f"run_id={rep['run_id']}")
    print(f"searches_total={rep['searches_total']}")
    print(f"searches_due={rep['searches_due']}")
    print(f"searches_skipped_not_due={rep['searches_skipped_not_due']}")
    print(f"processed_ok={rep['processed_ok']}")
    print(f"processed_error={rep['processed_error']}")
    print(f"total_new_matches={rep['total_new_matches']}")
    print(f"started_at={rep.get('started_at')}")
    print(f"finished_at={rep.get('finished_at')}")
    print(f"duration_seconds={rep.get('duration_seconds')}")
    print(f"lock_acquired={rep.get('lock_acquired')}")
    print(f"report_json={rep['json_report_path']}")
    print(f"report_md={rep['md_report_path']}")
    if digest_delivery is not None:
        print(
            "digest_email="
            f"attempted={digest_delivery.get('attempted_count', 0)} "
            f"sent={digest_delivery.get('sent_count', 0)} "
            f"skipped={digest_delivery.get('skipped_count', 0)} "
            f"errors={digest_delivery.get('error_count', 0)}"
        )
    return 0


def _cmd_alerts_send_email(args: argparse.Namespace) -> int:
    smtp = SMTPConfig(
        host=args.smtp_host,
        port=args.smtp_port,
        from_email=args.from_email,
        user=args.smtp_user,
        password=args.smtp_password,
        use_tls=not args.no_tls,
    )
    rep = send_email_alerts_from_run(
        run_json_path=args.run_json,
        to_email=args.to,
        smtp_config=smtp,
    )
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_alerts_cleanup(args: argparse.Namespace) -> int:
    rep = cleanup_alert_runs(runs_dir=args.outdir, keep_last=args.keep_last)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_alerts_resend_digest(args: argparse.Namespace) -> int:
    try:
        smtp = SMTPConfig.from_env()
        rep = resend_digest_from_run_artifact(
            run_json_path=args.run_json,
            smtp_config=smtp,
            to_email=args.to,
        )
    except ValueError as exc:
        print(f"error={exc}")
        return 1
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_auth_create_user(args: argparse.Namespace) -> int:
    try:
        rep = create_local_user(
            db_path=args.saved_db,
            email=args.email,
            password=args.password,
            user_id=args.user_id,
            is_active=not args.inactive,
        )
    except ValueError as exc:
        print(f"error={exc}")
        return 1
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0


def _cmd_serve_report(args: argparse.Namespace) -> int:
    report = build_serving_layer_report(
        input_path=args.input,
        report_dir=args.report_dir,
    )
    print(f"input={report['input_path']}")
    print(f"report_json={Path(args.report_dir) / 'serving_layer_step19.json'}")
    print(f"report_md={Path(args.report_dir) / 'serving_layer_step19.md'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="jobintel-next official command surface")
    top = ap.add_subparsers(dest="group", required=True)

    ingest = top.add_parser("ingest", help="Ingestion commands")
    ingest_sub = ingest.add_subparsers(dest="ingest_cmd", required=True)

    run_cmd = ingest_sub.add_parser("run", help="Run structured ingestion from YAML config")
    run_cmd.add_argument("--config", required=True, help="YAML config (source of truth)")
    run_cmd.add_argument("--out", required=True, help="Output JSONL path")
    run_cmd.set_defaults(func=_cmd_ingest_run)

    exp_cmd = ingest_sub.add_parser("export", help="Export from single source/board")
    exp_cmd.add_argument("--source", default="greenhouse", choices=["greenhouse"])
    exp_cmd.add_argument("--board", required=True, help="Greenhouse board slug (e.g. found)")
    exp_cmd.add_argument("--out", required=True, help="Output JSONL path")
    exp_cmd.add_argument("--no-content", action="store_true", help="Do not request content=true")
    exp_cmd.add_argument("--timeout-s", type=int, default=None, help="HTTP timeout override")
    exp_cmd.add_argument("--retries", type=int, default=None, help="Retry override")
    exp_cmd.add_argument("--max-concurrency", type=int, default=None, help="Concurrency override")
    exp_cmd.set_defaults(func=_cmd_ingest_export)

    language = top.add_parser("language", help="Language stage commands")
    lang_sub = language.add_subparsers(dest="language_cmd", required=True)

    eval_cmd = lang_sub.add_parser("eval", help="Evaluate language stage on CanonicalRawJob JSONL")
    eval_cmd.add_argument("--input", required=True, help="Input JSONL (CanonicalRawJob or compatible raw export)")
    eval_cmd.add_argument("--outdir", required=True, help="Output directory for report and samples")
    eval_cmd.add_argument("--limit", type=int, default=None, help="Optional max rows to analyze")
    eval_cmd.add_argument("--sample-size", type=int, default=50, help="Sample rows per bucket")
    eval_cmd.add_argument("--top-k", type=int, default=20, help="Top titles/reasons per bucket")
    eval_cmd.set_defaults(func=_cmd_language_eval)

    gate_cmd = lang_sub.add_parser("gate", help="Route CanonicalRawJob rows by language bucket")
    gate_cmd.add_argument("--input", required=True, help="Input JSONL (CanonicalRawJob or compatible raw export)")
    gate_cmd.add_argument("--outdir", default="data/jobs", help="Output directory for bucketed JSONL")
    gate_cmd.add_argument("--report-dir", default="docs", help="Directory for language gate report")
    gate_cmd.add_argument("--limit", type=int, default=None, help="Optional max rows to process")
    gate_cmd.add_argument("--top-k", type=int, default=20, help="Top reasons per bucket")
    gate_cmd.set_defaults(func=_cmd_language_gate)

    cleaning = top.add_parser("cleaning", help="Cleaning stage commands")
    cleaning_sub = cleaning.add_subparsers(dest="cleaning_cmd", required=True)
    cleaning_run = cleaning_sub.add_parser("run", help="Run cleaning stage on CanonicalRawJob JSONL")
    cleaning_run.add_argument("--input", required=True, help="Input JSONL (typically jobs_en_filtered.jsonl)")
    cleaning_run.add_argument("--out", required=True, help="Output JSONL path for cleaned rows")
    cleaning_run.add_argument("--report-dir", default="docs", help="Directory for cleaning report")
    cleaning_run.add_argument("--limit", type=int, default=None, help="Optional max rows to process")
    cleaning_run.add_argument("--sample-size", type=int, default=5, help="Sample rows in report")
    cleaning_run.set_defaults(func=_cmd_cleaning_run)

    extraction = top.add_parser("extraction", help="Extraction stage commands")
    extraction_sub = extraction.add_subparsers(dest="extraction_cmd", required=True)
    extraction_run = extraction_sub.add_parser("run", help="Run extraction stage on cleaned jobs JSONL")
    extraction_run.add_argument("--input", required=True, help="Input JSONL (typically jobs_cleaned_en.jsonl)")
    extraction_run.add_argument("--out", required=True, help="Output JSONL path for extracted rows")
    extraction_run.add_argument("--report-dir", default="docs", help="Directory for extraction report")
    extraction_run.add_argument("--limit", type=int, default=None, help="Optional max rows to process")
    extraction_run.add_argument("--sample-size", type=int, default=5, help="Sample rows in report")
    extraction_run.set_defaults(func=_cmd_extraction_run)

    titles = top.add_parser("titles", help="Title classification stage commands")
    titles_sub = titles.add_subparsers(dest="titles_cmd", required=True)
    titles_run = titles_sub.add_parser("run", help="Run title normalization/classification stage")
    titles_run.add_argument("--input-cleaned", required=True, help="Input cleaned JSONL")
    titles_run.add_argument("--input-extracted", default=None, help="Optional extracted JSONL for lightweight context")
    titles_run.add_argument("--out", required=True, help="Output JSONL path for title classifications")
    titles_run.add_argument("--report-dir", default="docs", help="Directory for title stage report")
    titles_run.add_argument("--limit", type=int, default=None, help="Optional max rows to process")
    titles_run.add_argument("--top-k-other", type=int, default=20, help="Top other titles in report")
    titles_run.set_defaults(func=_cmd_titles_run)

    titles_eval = titles_sub.add_parser("eval", help="Evaluate title stage output and cluster other titles")
    titles_eval.add_argument("--input", required=True, help="Input JSONL (typically jobs_titled_en.jsonl)")
    titles_eval.add_argument("--outdir", required=True, help="Output directory for eval reports")
    titles_eval.add_argument("--limit", type=int, default=None, help="Optional max rows to analyze")
    titles_eval.add_argument("--sample-size", type=int, default=50, help="Sample rows per group")
    titles_eval.add_argument("--top-k", type=int, default=20, help="Top titles per group")
    titles_eval.set_defaults(func=_cmd_titles_eval)

    indexed = top.add_parser("indexed", help="Indexed record composition stage")
    indexed_sub = indexed.add_subparsers(dest="indexed_cmd", required=True)
    indexed_run = indexed_sub.add_parser("run", help="Compose final IndexedJob records from upstream stages")
    indexed_run.add_argument(
        "--input-canonical",
        default="data/jobs/jobs_en_filtered.jsonl",
        help="Canonical input JSONL (typically language-gated EN file)",
    )
    indexed_run.add_argument(
        "--input-language",
        default="data/jobs/jobs_en_filtered.jsonl",
        help="Language decision input JSONL (must include language_* fields)",
    )
    indexed_run.add_argument(
        "--input-cleaned",
        default="data/jobs/jobs_cleaned_en.jsonl",
        help="Cleaned stage output JSONL",
    )
    indexed_run.add_argument(
        "--input-extracted",
        default="data/jobs/jobs_extracted_en.jsonl",
        help="Extraction stage output JSONL",
    )
    indexed_run.add_argument(
        "--input-titled",
        default="data/jobs/jobs_titled_en.jsonl",
        help="Title stage output JSONL",
    )
    indexed_run.add_argument("--out", default="data/jobs/jobs_indexed_en.jsonl", help="Output indexed JSONL path")
    indexed_run.add_argument("--report-dir", default="docs", help="Directory for indexed stage report")
    indexed_run.add_argument("--limit", type=int, default=None, help="Optional max rows to process")
    indexed_run.add_argument("--sample-size", type=int, default=10, help="Sample rows in report")
    indexed_run.set_defaults(func=_cmd_indexed_run)

    retrieval = top.add_parser("retrieval", help="Query/filter layer over indexed jobs")
    retrieval_sub = retrieval.add_subparsers(dest="retrieval_cmd", required=True)

    retrieval_query = retrieval_sub.add_parser("query", help="Query indexed jobs with filters and sorting")
    retrieval_query.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    retrieval_query.add_argument("--out", default=None, help="Optional output JSONL path")
    retrieval_query.add_argument("--normalized-title", default=None, help="Filter by normalized_title")
    retrieval_query.add_argument("--role-family", default=None, help="Filter by role_family")
    retrieval_query.add_argument("--language-bucket", default=None, help="Filter by language_bucket")
    retrieval_query.add_argument("--location-type", default=None, help="Filter by location_type")
    retrieval_query.add_argument("--employment-type", default=None, help="Filter by employment_type")
    retrieval_query.add_argument("--has-salary", default=None, help="Filter by has_salary (true/false)")
    retrieval_query.add_argument("--has-skills", default=None, help="Filter by has_skills (true/false)")
    retrieval_query.add_argument("--title-is-other", default=None, help="Filter by title_is_other (true/false)")
    retrieval_query.add_argument(
        "--skills-contains",
        action="append",
        default=None,
        help="Required skill token; repeatable",
    )
    retrieval_query.add_argument("--salary-currency", default=None, help="Filter by salary_currency")
    retrieval_query.add_argument(
        "--sort-by",
        choices=["published_at_desc", "updated_at_desc", "url"],
        default="published_at_desc",
        help="Sort order",
    )
    retrieval_query.add_argument("--limit", type=int, default=None, help="Optional max result rows")
    retrieval_query.set_defaults(func=_cmd_retrieval_query)

    retrieval_report = retrieval_sub.add_parser("report", help="Generate retrieval layer step15 report")
    retrieval_report.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    retrieval_report.add_argument("--report-dir", default="docs", help="Output docs directory")
    retrieval_report.set_defaults(func=_cmd_retrieval_report)

    retrieval_pack = retrieval_sub.add_parser("pack", help="Run predefined product query packs")
    retrieval_pack.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    retrieval_pack.add_argument("--out", default=None, help="Optional output JSONL path for single pack run")
    retrieval_pack.add_argument(
        "--pack",
        required=True,
        choices=["all", *list_query_pack_names()],
        help="Pack name or 'all' to build step18 report",
    )
    retrieval_pack.add_argument("--report-dir", default="docs", help="Report directory when --pack all")
    retrieval_pack.add_argument("--limit", type=int, default=20, help="Result/sample limit")
    retrieval_pack.set_defaults(func=_cmd_retrieval_pack)

    serve = top.add_parser("serve", help="Serving/API foundation over indexed jobs")
    serve_sub = serve.add_subparsers(dest="serve_cmd", required=True)

    serve_query = serve_sub.add_parser("query", help="List jobs with filters and pagination")
    serve_query.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    serve_query.add_argument("--sqlite", default=None, help="Optional SQLite path (if set, query SQLite backend)")
    serve_query.add_argument("--out", default=None, help="Optional output JSONL path")
    serve_query.add_argument("--normalized-title", default=None, help="Filter by normalized_title")
    serve_query.add_argument("--role-family", default=None, help="Filter by role_family")
    serve_query.add_argument("--language-bucket", default=None, help="Filter by language_bucket")
    serve_query.add_argument("--location-type", default=None, help="Filter by location_type")
    serve_query.add_argument("--employment-type", default=None, help="Filter by employment_type")
    serve_query.add_argument("--has-salary", default=None, help="Filter by has_salary (true/false)")
    serve_query.add_argument("--has-skills", default=None, help="Filter by has_skills (true/false)")
    serve_query.add_argument("--title-is-other", default=None, help="Filter by title_is_other (true/false)")
    serve_query.add_argument(
        "--skills-contains",
        action="append",
        default=None,
        help="Required skill token; repeatable",
    )
    serve_query.add_argument("--salary-currency", default=None, help="Filter by salary_currency")
    serve_query.add_argument(
        "--sort-by",
        choices=["published_at_desc", "updated_at_desc", "url"],
        default="published_at_desc",
        help="Sort order",
    )
    serve_query.add_argument("--limit", type=int, default=20, help="Page size")
    serve_query.add_argument("--offset", type=int, default=0, help="Result offset")
    serve_query.set_defaults(func=_cmd_serve_query)

    serve_count = serve_sub.add_parser("count", help="Count jobs matching filters")
    serve_count.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    serve_count.add_argument("--sqlite", default=None, help="Optional SQLite path (if set, query SQLite backend)")
    serve_count.add_argument("--normalized-title", default=None, help="Filter by normalized_title")
    serve_count.add_argument("--role-family", default=None, help="Filter by role_family")
    serve_count.add_argument("--language-bucket", default=None, help="Filter by language_bucket")
    serve_count.add_argument("--location-type", default=None, help="Filter by location_type")
    serve_count.add_argument("--employment-type", default=None, help="Filter by employment_type")
    serve_count.add_argument("--has-salary", default=None, help="Filter by has_salary (true/false)")
    serve_count.add_argument("--has-skills", default=None, help="Filter by has_skills (true/false)")
    serve_count.add_argument("--title-is-other", default=None, help="Filter by title_is_other (true/false)")
    serve_count.add_argument(
        "--skills-contains",
        action="append",
        default=None,
        help="Required skill token; repeatable",
    )
    serve_count.add_argument("--salary-currency", default=None, help="Filter by salary_currency")
    serve_count.set_defaults(func=_cmd_serve_count)

    serve_pack = serve_sub.add_parser("pack", help="Run predefined query pack with pagination")
    serve_pack.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    serve_pack.add_argument("--sqlite", default=None, help="Optional SQLite path (if set, query SQLite backend)")
    serve_pack.add_argument("--out", default=None, help="Optional output JSONL path")
    serve_pack.add_argument("--pack", required=True, choices=list_query_pack_names(), help="Query pack name")
    serve_pack.add_argument("--limit", type=int, default=20, help="Page size")
    serve_pack.add_argument("--offset", type=int, default=0, help="Result offset")
    serve_pack.set_defaults(func=_cmd_serve_pack)

    serve_pack_count = serve_sub.add_parser("pack-count", help="Count records in predefined query pack")
    serve_pack_count.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    serve_pack_count.add_argument("--sqlite", default=None, help="Optional SQLite path (if set, query SQLite backend)")
    serve_pack_count.add_argument("--pack", required=True, choices=list_query_pack_names(), help="Query pack name")
    serve_pack_count.set_defaults(func=_cmd_serve_pack_count)

    serve_report = serve_sub.add_parser("report", help="Generate serving layer step19 report")
    serve_report.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    serve_report.add_argument("--report-dir", default="docs", help="Output docs directory")
    serve_report.set_defaults(func=_cmd_serve_report)

    storage = top.add_parser("storage", help="Storage/index commands")
    storage_sub = storage.add_subparsers(dest="storage_cmd", required=True)
    storage_build = storage_sub.add_parser("build-index", help="Build SQLite index from indexed JSONL")
    storage_build.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Input indexed JSONL")
    storage_build.add_argument("--sqlite", required=True, help="Output SQLite DB path")
    storage_build.add_argument("--batch-size", type=int, default=2000, help="Insert batch size")
    storage_build.set_defaults(func=_cmd_storage_build_index)

    saved = top.add_parser("saved-search", help="Saved search / alerts foundation commands")
    saved_sub = saved.add_subparsers(dest="saved_cmd", required=True)

    saved_create = saved_sub.add_parser("create", help="Create a saved search")
    saved_create.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Saved searches SQLite path")
    saved_create.add_argument("--name", required=True, help="Saved search display name")
    saved_create.add_argument("--query-type", required=True, choices=["filters", "pack"], help="Search type")
    saved_create.add_argument("--filters-json", default=None, help="JSON filters payload for query-type=filters")
    saved_create.add_argument("--pack-name", default=None, help="Pack name for query-type=pack")
    saved_create.add_argument(
        "--frequency",
        default="daily",
        choices=["manual", "daily", "twice_daily"],
        help="Execution frequency for scheduling",
    )
    saved_create.add_argument("--disabled", action="store_true", help="Create disabled search")
    saved_create.add_argument("--user-id", default="local-user", help="User scope id")
    saved_create.add_argument("--user-email", default="local@example.com", help="User email for bootstrap")
    saved_create.set_defaults(func=_cmd_saved_search_create)

    saved_list = saved_sub.add_parser("list", help="List saved searches")
    saved_list.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Saved searches SQLite path")
    saved_list.add_argument("--user-id", default="local-user", help="User scope id")
    saved_list.set_defaults(func=_cmd_saved_search_list)

    saved_enable = saved_sub.add_parser("enable", help="Enable a saved search")
    saved_enable.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Saved searches SQLite path")
    saved_enable.add_argument("--id", required=True, help="search_id")
    saved_enable.add_argument("--user-id", default="local-user", help="User scope id")
    saved_enable.set_defaults(func=_cmd_saved_search_enable)

    saved_disable = saved_sub.add_parser("disable", help="Disable a saved search")
    saved_disable.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Saved searches SQLite path")
    saved_disable.add_argument("--id", required=True, help="search_id")
    saved_disable.add_argument("--user-id", default="local-user", help="User scope id")
    saved_disable.set_defaults(func=_cmd_saved_search_disable)

    saved_run = saved_sub.add_parser("run", help="Run a saved search")
    saved_run.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Saved searches SQLite path")
    saved_run.add_argument("--id", required=True, help="search_id")
    saved_run.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Indexed JSONL input")
    saved_run.add_argument("--sqlite", default=None, help="Optional indexed SQLite path")
    saved_run.add_argument("--limit", type=int, default=100, help="Page size")
    saved_run.add_argument("--offset", type=int, default=0, help="Result offset")
    saved_run.add_argument("--user-id", default="local-user", help="User scope id")
    saved_run.set_defaults(func=_cmd_saved_search_run)

    saved_check = saved_sub.add_parser("check-new", help="Check new matches since last seen state")
    saved_check.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Saved searches SQLite path")
    saved_check.add_argument("--id", required=True, help="search_id")
    saved_check.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Indexed JSONL input")
    saved_check.add_argument("--sqlite", default=None, help="Optional indexed SQLite path")
    saved_check.add_argument("--scan-limit", type=int, default=5000, help="Max rows scanned for diff")
    saved_check.add_argument("--limit", type=int, default=100, help="Returned rows page size")
    saved_check.add_argument("--offset", type=int, default=0, help="Result offset")
    saved_check.add_argument("--user-id", default="local-user", help="User scope id")
    saved_check.set_defaults(func=_cmd_saved_search_check_new)

    saved_run_all = saved_sub.add_parser("run-all", help="Run all enabled saved searches and persist local alerts report")
    saved_run_all.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Saved searches SQLite path")
    saved_run_all.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Indexed JSONL input")
    saved_run_all.add_argument("--sqlite", default=None, help="Optional indexed SQLite path")
    saved_run_all.add_argument("--outdir", default="data/alerts/runs", help="Output directory for run artifacts")
    saved_run_all.add_argument("--scan-limit", type=int, default=5000, help="Max rows scanned per search for diff")
    saved_run_all.add_argument("--limit", type=int, default=200, help="Rows loaded per search before sampling")
    saved_run_all.add_argument("--sample-size", type=int, default=5, help="Sample new matches per search in report")
    saved_run_all.add_argument("--user-id", default="local-user", help="User scope id")
    saved_run_all.add_argument("--user-email", default="local@example.com", help="User email")
    saved_run_all.set_defaults(func=_cmd_saved_search_run_all)

    alerts = top.add_parser("alerts", help="Alert delivery commands")
    alerts_sub = alerts.add_subparsers(dest="alerts_cmd", required=True)
    alerts_email = alerts_sub.add_parser("send-email", help="Send email alerts from runner JSON artifact")
    alerts_email.add_argument("--run-json", required=True, help="Path to run artifact JSON")
    alerts_email.add_argument("--to", required=True, help="Destination email")
    alerts_email.add_argument("--smtp-host", required=True, help="SMTP host")
    alerts_email.add_argument("--smtp-port", type=int, default=587, help="SMTP port")
    alerts_email.add_argument("--smtp-user", default=None, help="SMTP username")
    alerts_email.add_argument("--smtp-password", default=None, help="SMTP password")
    alerts_email.add_argument("--from-email", required=True, help="From email")
    alerts_email.add_argument("--no-tls", action="store_true", help="Disable STARTTLS")
    alerts_email.set_defaults(func=_cmd_alerts_send_email)

    alerts_cleanup = alerts_sub.add_parser("cleanup", help="Cleanup old alert run artifacts")
    alerts_cleanup.add_argument("--outdir", default="data/alerts/runs", help="Alert runs directory")
    alerts_cleanup.add_argument("--keep-last", type=int, default=20, help="Keep only N most recent runs")
    alerts_cleanup.set_defaults(func=_cmd_alerts_cleanup)

    alerts_resend = alerts_sub.add_parser("resend-digest", help="Resend digest email from an existing run artifact")
    alerts_resend.add_argument("--run-json", required=True, help="Path to run artifact JSON")
    alerts_resend.add_argument("--to", default=None, help="Destination email (fallback: digest_delivery.to_email in artifact)")
    alerts_resend.set_defaults(func=_cmd_alerts_resend_digest)

    alerts_due = alerts_sub.add_parser("run-due", help="Run only enabled saved searches due by frequency")
    alerts_due.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Saved searches SQLite path")
    alerts_due.add_argument("--job-state-db", default="data/jobs/job_state.db", help="Job state SQLite path")
    alerts_due.add_argument("--input", default="data/jobs/jobs_indexed_en.jsonl", help="Indexed JSONL input")
    alerts_due.add_argument("--sqlite", default=None, help="Optional indexed SQLite path")
    alerts_due.add_argument("--outdir", default="data/alerts/runs", help="Output directory for run artifacts")
    alerts_due.add_argument("--scan-limit", type=int, default=5000, help="Max rows scanned per search for diff")
    alerts_due.add_argument("--limit", type=int, default=200, help="Rows loaded per search before sampling")
    alerts_due.add_argument("--sample-size", type=int, default=5, help="Sample new matches per search in report")
    alerts_due.add_argument("--user-id", default="local-user", help="User scope id")
    alerts_due.add_argument("--user-email", default="local@example.com", help="User email")
    alerts_due.add_argument("--send-digest-email", action="store_true", help="Send one per-user digest email after due run")
    alerts_due.add_argument("--email-to", default=None, help="Digest destination; fallback to user's default_alert_email")
    alerts_due.set_defaults(func=_cmd_alerts_run_due)

    auth = top.add_parser("auth", help="Local auth/account commands")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True)
    auth_create = auth_sub.add_parser("create-user", help="Create or upsert a local user")
    auth_create.add_argument("--saved-db", default="data/jobs/saved_searches.db", help="Auth SQLite path")
    auth_create.add_argument("--email", required=True, help="User email")
    auth_create.add_argument("--password", required=True, help="Plain password (hashed before storage)")
    auth_create.add_argument("--user-id", default=None, help="Optional explicit user_id")
    auth_create.add_argument("--inactive", action="store_true", help="Create user as inactive")
    auth_create.set_defaults(func=_cmd_auth_create_user)
    return ap


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
