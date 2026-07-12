from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml
from ddgs import DDGS


GREENHOUSE_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}
SMARTRECRUITERS_HOSTS = {"jobs.smartrecruiters.com", "careers.smartrecruiters.com"}
LEVER_HOSTS = {"jobs.lever.co"}
GH_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
SR_API = "https://api.smartrecruiters.com/v1/companies/{company}/postings"
LEVER_API = "https://api.lever.co/v0/postings/{company}"
BRAVE_SEARCH_API = "https://api.search.brave.com/res/v1/web/search"

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
        u = urlparse(url)
        host = (u.netloc or "").lower()
        parts = [p for p in (u.path or "").split("/") if p]
        if not parts:
            return None

        if host in GREENHOUSE_HOSTS:
            # ignore embed/app paths
            if parts[0].lower() in {"embed", "job_board", "job_app"}:
                return None
            return "greenhouse", parts[0].lower()

        if host in SMARTRECRUITERS_HOSTS:
            company = parts[0].strip()
            if _is_bad_smartrecruiters_slug(company):
                return None
            return "smartrecruiters", company

        if host in LEVER_HOSTS or (host.startswith("jobs.") and host.endswith(".lever.co")):
            company = parts[0].strip().lower()
            if company in {"jobs", "postings", "lever", "robots.txt", "sitemap.xml", "favicon.ico"}:
                return None
            if _is_bad_lever_slug(company):
                return None
            return "lever", company

    except Exception:
        return None
    return None


def _is_bad_slug(source: str, slug: str) -> bool:
    if source == "smartrecruiters":
        return False
    s = slug.strip().lower()
    return any(k in s for k in ["referral", "internal", "test"])


def _probe_greenhouse(slug: str) -> bool:
    url = GH_API.format(slug=slug)
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "jobintel/0.1"})
        if r.status_code != 200:
            print(f"Probe failed greenhouse:{slug}: {r.status_code}")
            return False
        data = r.json()
        print(f"Probe ok greenhouse:{slug}: {len(data.get('jobs', []))} jobs")
        return isinstance(data, dict) and "jobs" in data
    except Exception:
        print(f"Probe failed greenhouse:{slug}: exception")
        return False


def _probe_smartrecruiters(company: str) -> bool:
    url = SR_API.format(company=company)
    try:
        r = requests.get(url, params={"limit": 1}, timeout=15, headers={"User-Agent": "jobintel/0.1"})
        if r.status_code != 200:
            print(f"Probe failed smartrecruiters:{company}: {r.status_code}")
            return False
        data = r.json()
        content = data.get("content", []) if isinstance(data, dict) else []
        print(f"Probe ok smartrecruiters:{company}: {len(content)} sample jobs")
        if not isinstance(data, dict):
            return False
        if not isinstance(content, list) or not content:
            return False
        first = content[0]
        return isinstance(first, dict) and bool(first.get("name") or first.get("title")) and bool(
            first.get("ref") or first.get("id") or first.get("url")
        )
    except Exception:
        print(f"Probe failed smartrecruiters:{company}: exception")
        return False


def _probe_lever(company: str) -> bool:
    url = LEVER_API.format(company=company)
    try:
        r = requests.get(url, params={"mode": "json"}, timeout=15, headers={"User-Agent": "jobintel/0.1"})
        if r.status_code != 200:
            print(f"Probe failed lever:{company}: {r.status_code}")
            return False
        data = r.json()
        size = len(data) if isinstance(data, list) else 0
        print(f"Probe ok lever:{company}: {size} sample jobs")
        if not isinstance(data, list) or not data:
            return False
        first = data[0] if data else {}
        return isinstance(first, dict) and bool(first.get("hostedUrl")) and bool(first.get("text"))
    except Exception:
        print(f"Probe failed lever:{company}: exception")
        return False


def _probe(source: str, slug: str) -> bool:
    if source == "greenhouse":
        return _probe_greenhouse(slug)
    if source == "smartrecruiters":
        return _probe_smartrecruiters(slug)
    if source == "lever":
        return _probe_lever(slug)
    return False


def _ddg_search(query: str, max_results: int) -> list[str]:
    urls: list[str] = []
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        for r in results:
            url = r.get("href") or r.get("url")
            if isinstance(url, str):
                urls.append(url)
    return urls


def _brave_search(query: str, brave_api_key: str, max_results: int) -> list[str]:
    urls: list[str] = []
    offset = 0

    # Brave Web Search supports page windows via count/offset.
    # We cap each call to count=20 and fetch enough pages for max_results.
    while len(urls) < max_results:
        count = min(20, max_results - len(urls))
        params = {
            "q": query,
            "count": count,
            "offset": offset,
        }
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": brave_api_key,
        }
        r = requests.get(BRAVE_SEARCH_API, params=params, headers=headers, timeout=20)
        if r.status_code != 200:
            raise RuntimeError(f"Brave search failed: {r.status_code} {r.text[:300]}")
        data = r.json() if r.content else {}
        results = (((data or {}).get("web") or {}).get("results") or [])
        if not isinstance(results, list) or not results:
            break

        for item in results:
            if not isinstance(item, dict):
                continue
            url = item.get("url")
            if isinstance(url, str):
                urls.append(url)
                if len(urls) >= max_results:
                    break

        offset += count
        if count < 20:
            break
        time.sleep(0.25)

    return urls[:max_results]


def _search_urls(
    provider: str,
    query: str,
    max_results: int,
    brave_api_key: str | None,
) -> list[str]:
    if provider == "ddg":
        return _ddg_search(query, max_results)
    if provider == "brave":
        if not brave_api_key:
            raise RuntimeError("Missing Brave API key. Pass --brave-api-key or set BRAVE_API_KEY.")
        return _brave_search(query, brave_api_key, max_results)
    raise RuntimeError(f"Unknown provider: {provider}")


def discover(
    queries: list[str],
    provider: str,
    max_results: int = 50,
    brave_api_key: str | None = None,
) -> dict[str, list[str]]:
    targets: dict[str, list[str]] = {"greenhouse": [], "smartrecruiters": [], "lever": []}
    seen: dict[str, set[str]] = {"greenhouse": set(), "smartrecruiters": set(), "lever": set()}

    for q in queries:
        urls = _search_urls(
            provider=provider,
            query=q,
            max_results=max_results,
            brave_api_key=brave_api_key,
        )
        for url in urls:
            print(f"{provider.upper()} hit: {url}")

            target = _extract_target(url)
            if not target:
                continue
            source, slug = target
            key = slug.lower()

            if key in seen[source] or _is_bad_slug(source, slug):
                continue
            seen[source].add(key)

            if _probe(source, slug):
                targets[source].append(slug)
            time.sleep(0.4)

    return targets


def _load_existing(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {"greenhouse": [], "smartrecruiters": [], "lever": []}

    data = yaml.safe_load(path.read_text()) or {}
    sources = data.get("sources", {}) if isinstance(data, dict) else {}
    gh_boards = sources.get("greenhouse", {}).get("boards", []) if isinstance(sources, dict) else []
    sr_companies = (
        sources.get("smartrecruiters", {}).get("companies", []) if isinstance(sources, dict) else []
    )
    lever_companies = sources.get("lever", {}).get("companies", []) if isinstance(sources, dict) else []

    return {
        "greenhouse": [b for b in gh_boards if isinstance(b, str)],
        "smartrecruiters": [c for c in sr_companies if isinstance(c, str)],
        "lever": [c for c in lever_companies if isinstance(c, str)],
    }


def write_targets(path: Path, targets: dict[str, list[str]]) -> None:
    existing = _load_existing(path)
    merged_gh = list(dict.fromkeys(existing["greenhouse"] + targets["greenhouse"]))
    merged_sr = list(dict.fromkeys(existing["smartrecruiters"] + targets["smartrecruiters"]))
    merged_lever = list(dict.fromkeys(existing["lever"] + targets["lever"]))

    payload = {
        "sources": {
            "greenhouse": {"enabled": True, "boards": merged_gh, "content": True},
            "smartrecruiters": {"enabled": True, "companies": merged_sr, "limit": 100},
            "lever": {"enabled": True, "companies": merged_lever},
        }
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["ddg", "brave"], default="ddg")
    ap.add_argument("--max-results", type=int, default=50)
    ap.add_argument("--output", default="config/generated/targets.yml")
    ap.add_argument("--brave-api-key", default="")
    args = ap.parse_args()

    queries = [
        "site:boards.greenhouse.io remote data",
        "site:boards.greenhouse.io Europe data",
        "site:boards.greenhouse.io EMEA data",
        "site:boards.greenhouse.io remote analytics",
        "site:boards.greenhouse.io data analyst",
        "site:boards.greenhouse.io Berlin data",
        "site:boards.greenhouse.io London data",
        "site:boards.greenhouse.io Amsterdam data",
        "site:boards.greenhouse.io distributed data",
        "site:boards.greenhouse.io SQL",
        "site:jobs.smartrecruiters.com remote data",
        "site:jobs.smartrecruiters.com data analyst",
        "site:jobs.smartrecruiters.com analytics",
        "site:jobs.smartrecruiters.com python",
        "site:jobs.lever.co software engineer",
        "site:jobs.lever.co data engineer",
        "site:jobs.lever.co backend engineer",
        "site:jobs.lever.co remote",
    ]

    brave_api_key = args.brave_api_key.strip() or ""
    if args.provider == "brave" and not brave_api_key:
        brave_api_key = os.environ.get("BRAVE_API_KEY", "").strip()

    targets = discover(
        queries=queries,
        provider=args.provider,
        max_results=args.max_results,
        brave_api_key=brave_api_key or None,
    )
    out = Path(args.output)
    write_targets(out, targets)
    print(f"Wrote {out}")
    print(f"GH boards: {len(targets['greenhouse'])}")
    print(f"SR companies: {len(targets['smartrecruiters'])}")
    print(f"Lever companies: {len(targets['lever'])}")


if __name__ == "__main__":
    main()
