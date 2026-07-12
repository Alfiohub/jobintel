from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import shutil
from pathlib import Path

# Conservative keep-set for files typically used in the active microsaas pipeline.
KEEP_PATTERNS_PRODUCTION_MINIMAL = [
    "README.md",
    "microsaas_eval_runbook.md",
    "microsaas_pipeline_flow.md",
    "gold_eval_annotation_schema.md",
    "gold_eval_set_v1_en_locv4.csv",
    "gold_eval_set_v1_en_locv4_autolabeled.csv",
    "title_onet_crosswalk.csv",
    "review_analysis_locv4/review_summary.json",
    "review_analysis_locv4/review_summary.txt",
]

# Always keep these whole trees in place.
KEEP_DIR_PREFIXES = [
    "archive/",
    "baselines/",
]


def _matches_any(path_rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path_rel, p) for p in patterns)


def _is_kept(path_rel: str, keep_patterns: list[str]) -> bool:
    if _matches_any(path_rel, keep_patterns):
        return True
    return any(path_rel.startswith(prefix) for prefix in KEEP_DIR_PREFIXES)


def _collect_docs_files(docs_dir: Path) -> list[Path]:
    return sorted([p for p in docs_dir.rglob("*") if p.is_file()])


def plan_moves(docs_dir: Path, keep_patterns: list[str]) -> tuple[list[Path], list[Path]]:
    keep: list[Path] = []
    move: list[Path] = []
    for p in _collect_docs_files(docs_dir):
        rel = p.relative_to(docs_dir).as_posix()
        if _is_kept(rel, keep_patterns):
            keep.append(p)
        else:
            move.append(p)
    return keep, move


def apply_moves(docs_dir: Path, files_to_move: list[Path], archive_dir: Path) -> int:
    moved = 0
    archive_dir.mkdir(parents=True, exist_ok=True)
    for src in files_to_move:
        rel = src.relative_to(docs_dir)
        dst = archive_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moved += 1
    return moved


def main() -> None:
    ap = argparse.ArgumentParser(description="Archive non-production docs files with dry-run first.")
    ap.add_argument("--docs-dir", default="docs", help="Docs root directory")
    ap.add_argument(
        "--profile",
        default="production-minimal",
        choices=["production-minimal"],
        help="Cleanup profile",
    )
    ap.add_argument(
        "--archive-subdir",
        default="",
        help="Optional archive subdir under docs/archive (default: repo_cleanup_YYYYMMDD)",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Apply moves. Without this flag, only prints the plan.",
    )
    ap.add_argument(
        "--show-limit",
        type=int,
        default=80,
        help="Max number of file paths to print for each section",
    )
    args = ap.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists() or not docs_dir.is_dir():
        raise RuntimeError(f"Docs directory not found: {docs_dir}")

    if args.profile == "production-minimal":
        keep_patterns = KEEP_PATTERNS_PRODUCTION_MINIMAL
    else:
        raise RuntimeError(f"Unsupported profile: {args.profile}")

    keep, move = plan_moves(docs_dir, keep_patterns)

    tag = args.archive_subdir.strip() or f"repo_cleanup_{dt.date.today().strftime('%Y%m%d')}"
    archive_dir = docs_dir / "archive" / tag

    print(f"Docs dir: {docs_dir}")
    print(f"Profile: {args.profile}")
    print(f"Archive target: {archive_dir}")
    print(f"Keep files: {len(keep)}")
    print(f"Move files: {len(move)}")
    print("")

    print("Keep sample:")
    for p in keep[: max(0, args.show_limit)]:
        print(f"- {p.relative_to(docs_dir).as_posix()}")
    if len(keep) > args.show_limit:
        print(f"- ... (+{len(keep) - args.show_limit} more)")

    print("")
    print("Move sample:")
    for p in move[: max(0, args.show_limit)]:
        print(f"- {p.relative_to(docs_dir).as_posix()}")
    if len(move) > args.show_limit:
        print(f"- ... (+{len(move) - args.show_limit} more)")

    if not args.apply:
        print("\nDry-run only. Use --apply to move files.")
        return

    moved = apply_moves(docs_dir, move, archive_dir)
    print("")
    print(f"Moved files: {moved}")
    print(f"Archive dir: {archive_dir}")


if __name__ == "__main__":
    main()
