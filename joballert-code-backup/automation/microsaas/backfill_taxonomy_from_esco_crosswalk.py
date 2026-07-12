from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description='Backfill taxonomy fields from title_esco_crosswalk into jobs_indexed/extraction_cache')
    ap.add_argument('--db', default='data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite')
    ap.add_argument('--report-json', default='docs/review_analysis_locv6r/esco_backfill_report.json')
    ap.add_argument('--report-txt', default='docs/review_analysis_locv6r/esco_backfill_report.txt')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    try:
        cw_rows = con.execute(
            """
            SELECT normalized_title, esco_id, esco_label, COALESCE(mapping_confidence, 0.0)
            FROM title_esco_crosswalk
            """
        ).fetchall()

        mapped_titles = [r[0] for r in cw_rows if (r[1] or '').strip()]
        unmapped_titles = [r[0] for r in cw_rows if not (r[1] or '').strip()]

        before_jobs = con.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN taxonomy_code IS NOT NULL AND taxonomy_code <> '' THEN 1 ELSE 0 END) AS mapped
            FROM jobs_indexed
            """
        ).fetchone()

        before_cache = con.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN taxonomy_code IS NOT NULL AND taxonomy_code <> '' THEN 1 ELSE 0 END) AS mapped
            FROM extraction_cache
            """
        ).fetchone()

        jobs_updated_mapped = 0
        jobs_cleared = 0
        cache_updated_mapped = 0
        cache_cleared = 0

        if not args.dry_run:
            # Apply mapped ESCO rows
            jobs_updated_mapped = con.execute(
                """
                UPDATE jobs_indexed
                SET taxonomy_source='esco',
                    taxonomy_code=(SELECT c.esco_id FROM title_esco_crosswalk c WHERE c.normalized_title=jobs_indexed.normalized_title),
                    taxonomy_label=(SELECT c.esco_label FROM title_esco_crosswalk c WHERE c.normalized_title=jobs_indexed.normalized_title),
                    taxonomy_match_confidence=(SELECT COALESCE(c.mapping_confidence, 0.0) FROM title_esco_crosswalk c WHERE c.normalized_title=jobs_indexed.normalized_title)
                WHERE normalized_title IN (
                    SELECT normalized_title FROM title_esco_crosswalk WHERE esco_id IS NOT NULL AND esco_id <> ''
                )
                """
            ).rowcount

            cache_updated_mapped = con.execute(
                """
                UPDATE extraction_cache
                SET taxonomy_source='esco',
                    taxonomy_code=(SELECT c.esco_id FROM title_esco_crosswalk c WHERE c.normalized_title=extraction_cache.normalized_title),
                    taxonomy_label=(SELECT c.esco_label FROM title_esco_crosswalk c WHERE c.normalized_title=extraction_cache.normalized_title),
                    taxonomy_match_confidence=(SELECT COALESCE(c.mapping_confidence, 0.0) FROM title_esco_crosswalk c WHERE c.normalized_title=extraction_cache.normalized_title)
                WHERE normalized_title IN (
                    SELECT normalized_title FROM title_esco_crosswalk WHERE esco_id IS NOT NULL AND esco_id <> ''
                )
                """
            ).rowcount

            # Clear forced mappings for keep-separate titles
            jobs_cleared = con.execute(
                """
                UPDATE jobs_indexed
                SET taxonomy_source=NULL,
                    taxonomy_code=NULL,
                    taxonomy_label=NULL,
                    taxonomy_match_confidence=0.0
                WHERE normalized_title IN (
                    SELECT normalized_title FROM title_esco_crosswalk WHERE esco_id IS NULL OR esco_id=''
                )
                """
            ).rowcount

            cache_cleared = con.execute(
                """
                UPDATE extraction_cache
                SET taxonomy_source=NULL,
                    taxonomy_code=NULL,
                    taxonomy_label=NULL,
                    taxonomy_match_confidence=0.0
                WHERE normalized_title IN (
                    SELECT normalized_title FROM title_esco_crosswalk WHERE esco_id IS NULL OR esco_id=''
                )
                """
            ).rowcount

            con.commit()

        after_jobs = con.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN taxonomy_code IS NOT NULL AND taxonomy_code <> '' THEN 1 ELSE 0 END) AS mapped
            FROM jobs_indexed
            """
        ).fetchone()

        after_cache = con.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN taxonomy_code IS NOT NULL AND taxonomy_code <> '' THEN 1 ELSE 0 END) AS mapped
            FROM extraction_cache
            """
        ).fetchone()

        report = {
            'db': args.db,
            'dry_run': bool(args.dry_run),
            'crosswalk_titles_total': len(cw_rows),
            'crosswalk_titles_mapped': len(mapped_titles),
            'crosswalk_titles_keep_separate': len(unmapped_titles),
            'jobs_before_total': int(before_jobs[0] or 0),
            'jobs_before_mapped': int(before_jobs[1] or 0),
            'jobs_after_total': int(after_jobs[0] or 0),
            'jobs_after_mapped': int(after_jobs[1] or 0),
            'extraction_cache_before_total': int(before_cache[0] or 0),
            'extraction_cache_before_mapped': int(before_cache[1] or 0),
            'extraction_cache_after_total': int(after_cache[0] or 0),
            'extraction_cache_after_mapped': int(after_cache[1] or 0),
            'jobs_updated_mapped': int(jobs_updated_mapped or 0),
            'jobs_cleared': int(jobs_cleared or 0),
            'cache_updated_mapped': int(cache_updated_mapped or 0),
            'cache_cleared': int(cache_cleared or 0),
            'keep_separate_titles': sorted(unmapped_titles),
        }

    finally:
        con.close()

    report_json = Path(args.report_json)
    report_txt = Path(args.report_txt)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_txt.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = [
        'ESCO Backfill Report',
        f"DB: {report['db']}",
        f"Dry-run: {int(report['dry_run'])}",
        f"Crosswalk titles total: {report['crosswalk_titles_total']}",
        f"Crosswalk titles mapped: {report['crosswalk_titles_mapped']}",
        f"Crosswalk titles keep_separate: {report['crosswalk_titles_keep_separate']}",
        f"jobs_indexed mapped: {report['jobs_before_mapped']} -> {report['jobs_after_mapped']}",
        f"extraction_cache mapped: {report['extraction_cache_before_mapped']} -> {report['extraction_cache_after_mapped']}",
        f"jobs updated mapped: {report['jobs_updated_mapped']}",
        f"jobs cleared: {report['jobs_cleared']}",
        f"cache updated mapped: {report['cache_updated_mapped']}",
        f"cache cleared: {report['cache_cleared']}",
    ]
    report_txt.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f"Wrote: {report_json}")
    print(f"Wrote: {report_txt}")
    print(f"jobs_indexed mapped: {report['jobs_before_mapped']} -> {report['jobs_after_mapped']}")


if __name__ == '__main__':
    main()
