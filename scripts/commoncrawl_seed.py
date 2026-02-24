from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml


GH_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}
SR_HOSTS = {"jobs.smartrecruiters.com", "careers.smartrecruiters.com"}
LEVER_HOSTS = {"jobs.lever.co"}

GH_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
SR_API = "https://api.smartrecruiters.com/v1/companies/{company}/postings"
LEVER_API = "https://api.lever.co/v0/postings/{company}"
CC_COLLINFO = "https://index.commoncrawl.org/collinfo.json"

LEVER_BLOCKED_SLUGS = {
    "applicant-tracking-system",
    "blog",
    "careers",
    "case-study",
    "category",
    "contact",
    "contact-sales-support",
    "customers",
    "demo",
    "events",
    "pricing",
    "reports",
    "resources",
    "search",
    "solutions",
    "summit",
    "tag",
    "v0",
}

SR_BLOCKED_SLUGS = {
    "jobs",
    "search-jobs",
    "robots.txt",
    "sitemap.xml",
    "favicon.ico",
}


def _is_bad_lever_slug(slug: str) -> bool:
    s = slug.strip().lower()
    if not s:
        return True
    if s in LEVER_BLOCKED_SLUGS:
        return True
    if len(s) < 3:
        return True
    if any(ch in s for ch in ("/", "?", "&", "=")):
        return True
    return False


def _is_bad_smartrecruiters_slug(slug: str) -> bool:
    s = slug.strip().lower()
    if not s:
        return True
    if s in SR_BLOCKED_SLUGS:
        return True
    if any(ch in s for ch in ("/", "?", "&", "=")):
        return True
    return False


def _extract_target(url: str) -> tuple[str, str] | None:
    try:
        u = urlparse(url.strip())
        host = (u.netloc or "").lower()
        parts = [p for p in (u.path or "").split("/") if p]
        if not parts:
            return None

        if host in GH_HOSTS:
            first = parts[0].lower()
            if first in {"embed", "job_board", "job_app"}:
                return None
            if any(k in first for k in ("internal", "referral", "test")):
                return None
            return "greenhouse", first

        if host in SR_HOSTS:
            company = parts[0].strip()
            if _is_bad_smartrecruiters_slug(company):
                return None
            return "smartrecruiters", company

        if host in LEVER_HOSTS or (host.startswith("jobs.") and host.endswith(".lever.co")):
            company = parts[0].strip().lower()
            if company in {"jobs", "postings", "lever", "robots.txt", "sitemap.xml", "favicon.ico"}:
                return None
            if any(k in company for k in ("internal", "referral", "test")):
                return None
            if _is_bad_lever_slug(company):
                return None
            return "lever", company

    except Exception:
        return None
    return None


def _probe_greenhouse(slug: str, timeout_s: int = 15) -> bool:
    try:
        r = requests.get(
            GH_API.format(slug=slug),
            timeout=timeout_s,
            headers={"User-Agent": "jobintel/0.1"},
        )
        if r.status_code != 200:
            return False
        data = r.json()
        return isinstance(data, dict) and "jobs" in data
    except Exception:
        return False


def _probe_smartrecruiters(company: str, timeout_s: int = 15) -> bool:
    try:
        r = requests.get(
            SR_API.format(company=company),
            params={"limit": 1},
            timeout=timeout_s,
            headers={"User-Agent": "jobintel/0.1"},
        )
        if r.status_code != 200:
            return False
        data = r.json()
        if not isinstance(data, dict):
            return False
        content = data.get("content", [])
        if not isinstance(content, list) or not content:
            return False
        first = content[0]
        return isinstance(first, dict) and bool(first.get("name") or first.get("title")) and bool(
            first.get("ref") or first.get("id") or first.get("url")
        )
    except Exception:
        return False


def _probe_lever(company: str, timeout_s: int = 15) -> bool:
    try:
        r = requests.get(
            LEVER_API.format(company=company),
            params={"mode": "json"},
            timeout=timeout_s,
            headers={"User-Agent": "jobintel/0.1"},
        )
        if r.status_code != 200:
            return False
        data = r.json()
        if not isinstance(data, list) or not data:
            return False
        first = data[0] if data else {}
        return isinstance(first, dict) and bool(first.get("hostedUrl")) and bool(first.get("text"))
    except Exception:
        return False


def _probe(source: str, slug: str, timeout_s: int = 15) -> bool:
    if source == "greenhouse":
        return _probe_greenhouse(slug, timeout_s=timeout_s)
    if source == "smartrecruiters":
        return _probe_smartrecruiters(slug, timeout_s=timeout_s)
    if source == "lever":
        return _probe_lever(slug, timeout_s=timeout_s)
    return False


def _cc_query(index_name: str, pattern: str, timeout_s: int = 30) -> list[str]:
    """
    Query Common Crawl index and return discovered URLs.
    Endpoint format:
      https://index.commoncrawl.org/{index_name}-index?url={pattern}&output=json
    """
    endpoint = f"https://index.commoncrawl.org/{index_name}-index"
    params = {"url": pattern, "output": "json"}

    r = requests.get(endpoint, params=params, timeout=timeout_s, headers={"User-Agent": "jobintel/0.1"})
    if r.status_code == 404:
        raise RuntimeError(f"Common Crawl index not found: {index_name}")
    r.raise_for_status()

    urls: list[str] = []
    for raw in r.text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        u = obj.get("url")
        if isinstance(u, str):
            urls.append(u)
    return urls


def _resolve_index_name(index_name: str, timeout_s: int = 20) -> str:
    """
    Accepts:
      - explicit index (e.g. CC-MAIN-2024-42)
      - 'latest' to auto-pick newest from collinfo
    """
    if index_name.lower() != "latest":
        return index_name

    r = requests.get(CC_COLLINFO, timeout=timeout_s, headers={"User-Agent": "jobintel/0.1"})
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or not data:
        raise RuntimeError("Common Crawl collinfo is empty.")

    ids: list[str] = []
    for item in data:
        if isinstance(item, dict):
            cid = item.get("id")
            if isinstance(cid, str) and cid.startswith("CC-MAIN-"):
                ids.append(cid)
    if not ids:
        raise RuntimeError("No valid CC-MAIN index found in collinfo.")
    return ids[0]


def _load_existing(path: Path) -> dict:
    if not path.exists():
        return {"sources": {}}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {"sources": {}}


def write_targets(path: Path, targets: dict[str, list[str]]) -> None:
    existing = _load_existing(path)
    sources = existing.get("sources")
    if not isinstance(sources, dict):
        sources = {}

    gh = sources.get("greenhouse")
    if not isinstance(gh, dict):
        gh = {"enabled": True, "boards": [], "content": True}

    sr = sources.get("smartrecruiters")
    if not isinstance(sr, dict):
        sr = {"enabled": True, "companies": [], "limit": 100}
    lever = sources.get("lever")
    if not isinstance(lever, dict):
        lever = {"enabled": True, "companies": []}

    prev_gh = [x for x in (gh.get("boards") or []) if isinstance(x, str)]
    prev_sr = [x for x in (sr.get("companies") or []) if isinstance(x, str)]
    prev_lever = [x for x in (lever.get("companies") or []) if isinstance(x, str)]

    gh["enabled"] = True
    gh["content"] = bool(gh.get("content", True))
    gh["boards"] = list(dict.fromkeys(prev_gh + targets["greenhouse"]))

    sr["enabled"] = True
    sr["limit"] = int(sr.get("limit", 100) or 100)
    merged_sr = prev_sr + targets["smartrecruiters"]
    sr_unique: list[str] = []
    seen_sr: set[str] = set()
    for company in merged_sr:
        key = company.strip().lower()
        if not key or key in seen_sr:
            continue
        seen_sr.add(key)
        sr_unique.append(company)
    sr["companies"] = sr_unique
    lever["enabled"] = True
    merged_lever = prev_lever + targets["lever"]
    lever_unique: list[str] = []
    seen_lever: set[str] = set()
    for company in merged_lever:
        key = company.strip().lower()
        if not key or key in seen_lever:
            continue
        seen_lever.add(key)
        lever_unique.append(company)
    lever["companies"] = lever_unique

    sources["greenhouse"] = gh
    sources["smartrecruiters"] = sr
    sources["lever"] = lever

    payload = {"sources": sources}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def discover(
    index_name: str,
    source: str,
    max_candidates: int,
    max_valid_gh: int,
    max_valid_sr: int,
    max_valid_lever: int,
    probe_delay_s: float,
    workers: int,
) -> dict[str, list[str]]:
    resolved_index = _resolve_index_name(index_name)
    print(f"Using Common Crawl index: {resolved_index}")

    patterns: list[str] = []
    if source in {"all", "greenhouse"}:
        patterns.extend(["boards.greenhouse.io/*", "job-boards.greenhouse.io/*"])
    if source in {"all", "smartrecruiters"}:
        patterns.extend(["jobs.smartrecruiters.com/*", "careers.smartrecruiters.com/*"])
    if source in {"all", "lever"}:
        patterns.extend(["jobs.lever.co/*", "*.lever.co/*"])

    candidates: dict[str, list[str]] = {"greenhouse": [], "smartrecruiters": [], "lever": []}
    seen: dict[str, set[str]] = {"greenhouse": set(), "smartrecruiters": set(), "lever": set()}

    total = 0
    for pattern in patterns:
        urls = _cc_query(index_name=resolved_index, pattern=pattern)
        for u in urls:
            target = _extract_target(u)
            if not target:
                continue
            source, slug = target
            key = slug.lower()
            if key in seen[source]:
                continue
            seen[source].add(key)
            candidates[source].append(slug)
            total += 1
            if total >= max_candidates:
                break
        if total >= max_candidates:
            break

    valid: dict[str, list[str]] = {"greenhouse": [], "smartrecruiters": [], "lever": []}

    def _probe_many(kind: str, items: list[str], limit: int) -> list[str]:
        if limit <= 0 or not items:
            return []
        out: list[str] = []
        seen_local: set[str] = set()
        if workers <= 1:
            for item in items:
                ok = _probe(kind, item)
                print(f"probe {'ok' if ok else 'fail'} {kind}: {item}")
                if ok and item not in seen_local:
                    out.append(item)
                    seen_local.add(item)
                    if len(out) >= limit:
                        break
                if probe_delay_s > 0:
                    time.sleep(probe_delay_s)
            return out

        if probe_delay_s > 0:
            print("Note: --probe-delay is ignored when --workers > 1")

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(_probe, kind, item): item for item in items}
            for fut in as_completed(futures):
                item = futures[fut]
                ok = False
                try:
                    ok = bool(fut.result())
                except Exception:
                    ok = False
                print(f"probe {'ok' if ok else 'fail'} {kind}: {item}")
                if ok and item not in seen_local:
                    out.append(item)
                    seen_local.add(item)
                    if len(out) >= limit:
                        break
        return out

    valid["greenhouse"] = _probe_many("greenhouse", candidates["greenhouse"], max_valid_gh)
    valid["smartrecruiters"] = _probe_many("smartrecruiters", candidates["smartrecruiters"], max_valid_sr)
    valid["lever"] = _probe_many("lever", candidates["lever"], max_valid_lever)

    return valid


def main() -> None:
    ap = argparse.ArgumentParser(description="Discover Greenhouse/SmartRecruiters/Lever seeds from Common Crawl index.")
    ap.add_argument("--index", default="latest", help="Common Crawl index name, e.g. CC-MAIN-2024-42, or 'latest'")
    ap.add_argument(
        "--source",
        default="all",
        choices=["all", "greenhouse", "smartrecruiters", "lever"],
        help="Source to discover.",
    )
    ap.add_argument("--output", default="config/generated/targets.yml")
    ap.add_argument("--max-candidates", type=int, default=800)
    ap.add_argument("--max-valid-gh", type=int, default=200)
    ap.add_argument("--max-valid-sr", type=int, default=200)
    ap.add_argument("--max-valid-lever", type=int, default=200)
    ap.add_argument("--probe-delay", type=float, default=0.2)
    ap.add_argument("--workers", type=int, default=20)
    args = ap.parse_args()

    targets = discover(
        index_name=args.index,
        source=args.source,
        max_candidates=args.max_candidates,
        max_valid_gh=args.max_valid_gh,
        max_valid_sr=args.max_valid_sr,
        max_valid_lever=args.max_valid_lever,
        probe_delay_s=args.probe_delay,
        workers=max(1, args.workers),
    )
    out = Path(args.output)
    write_targets(out, targets)
    print(f"Wrote {out}")
    print(f"GH valid boards added: {len(targets['greenhouse'])}")
    print(f"SR valid companies added: {len(targets['smartrecruiters'])}")
    print(f"Lever valid companies added: {len(targets['lever'])}")


if __name__ == "__main__":
    main()
