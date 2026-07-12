from __future__ import annotations

import copy
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

@dataclass(frozen=True)
class AppConfig:
    greenhouse_timeout_sec: int = 20
    greenhouse_max_retries: int = 3
    greenhouse_max_concurrency: int = 12


def load_config() -> AppConfig:
    timeout = int(os.getenv("GREENHOUSE_TIMEOUT_SEC", "20") or 20)
    retries = int(os.getenv("GREENHOUSE_MAX_RETRIES", "3") or 3)
    max_concurrency = int(os.getenv("GREENHOUSE_MAX_CONCURRENCY", "12") or 12)
    return AppConfig(
        greenhouse_timeout_sec=timeout,
        greenhouse_max_retries=retries,
        greenhouse_max_concurrency=max_concurrency,
    )


def load_sources_from_yaml(path: str | Path) -> dict[str, Any]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return {}
    sources = raw.get("sources")
    return sources if isinstance(sources, dict) else {}


def apply_env_overrides_to_sources(sources: dict[str, Any]) -> dict[str, Any]:
    """
    YAML is source of truth.
    ENV vars only override technical knobs (timeout/retries/concurrency).
    """
    out = copy.deepcopy(sources)
    gh = out.get("greenhouse")
    if not isinstance(gh, dict):
        return out
    env_cfg = load_config()
    gh["timeout_s"] = env_cfg.greenhouse_timeout_sec
    gh["retries"] = env_cfg.greenhouse_max_retries
    gh["max_concurrency"] = env_cfg.greenhouse_max_concurrency
    return out
