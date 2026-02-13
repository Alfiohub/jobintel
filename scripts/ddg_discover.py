from __future__ import annotations

import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml
from ddgs import DDGS


GREENHOUSE_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}
SMARTRECRUITERS_HOSTS = {"jobs.smartrecruiters.com", "careers.smartrecruiters.com"}
GH_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
SR_API = "https://api.smartrecruiters.com/v1/companies/{company}/postings"


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
            if company.lower() in {"search-jobs", "jobs"}:
                return None
            return "smartrecruiters", company

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
        return isinstance(data, dict) and "content" in data
    except Exception:
        print(f"Probe failed smartrecruiters:{company}: exception")
        return False


def _probe(source: str, slug: str) -> bool:
    if source == "greenhouse":
        return _probe_greenhouse(slug)
    if source == "smartrecruiters":
        return _probe_smartrecruiters(slug)
    return False


def discover_from_ddg(queries: list[str], max_results: int = 50) -> dict[str, list[str]]:
    targets: dict[str, list[str]] = {"greenhouse": [], "smartrecruiters": []}
    seen: dict[str, set[str]] = {"greenhouse": set(), "smartrecruiters": set()}

    with DDGS() as ddgs:
        for q in queries:
            results = ddgs.text(q, max_results=max_results)
            for r in results:
                url = r.get("href") or r.get("url")
                if not isinstance(url, str):
                    continue
                print(f"DDG hit: {url}")

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
        return {"greenhouse": [], "smartrecruiters": []}

    data = yaml.safe_load(path.read_text()) or {}
    sources = data.get("sources", {}) if isinstance(data, dict) else {}
    gh_boards = sources.get("greenhouse", {}).get("boards", []) if isinstance(sources, dict) else []
    sr_companies = (
        sources.get("smartrecruiters", {}).get("companies", []) if isinstance(sources, dict) else []
    )

    return {
        "greenhouse": [b for b in gh_boards if isinstance(b, str)],
        "smartrecruiters": [c for c in sr_companies if isinstance(c, str)],
    }


def write_targets(path: Path, targets: dict[str, list[str]]) -> None:
    existing = _load_existing(path)
    merged_gh = list(dict.fromkeys(existing["greenhouse"] + targets["greenhouse"]))
    merged_sr = list(dict.fromkeys(existing["smartrecruiters"] + targets["smartrecruiters"]))

    payload = {
        "sources": {
            "greenhouse": {"enabled": True, "boards": merged_gh, "content": True},
            "smartrecruiters": {"enabled": True, "companies": merged_sr, "limit": 100},
        }
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
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
    ]

    targets = discover_from_ddg(queries, max_results=50)
    out = Path("config/generated/targets.yml")
    write_targets(out, targets)
    print(f"Wrote {out}")
    print(f"GH boards: {len(targets['greenhouse'])}")
    print(f"SR companies: {len(targets['smartrecruiters'])}")


if __name__ == "__main__":
    main()
