from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from .pipeline import PipelineConfig


@dataclass(frozen=True, slots=True)
class GreenhouseConfig:
    enabled: bool
    boards: tuple[str, ...]
    content: bool = True


@dataclass(frozen=True, slots=True)
class SmartRecruitersCfg:
    enabled: bool
    companies: tuple[str, ...]
    limit: int = 100


@dataclass(frozen=True, slots=True)
class LeverCfg:
    enabled: bool
    companies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NotifyConfig:
    mode: str
    telegram_bot_token: str
    telegram_chat_id: str


@dataclass(frozen=True, slots=True)
class StorageConfig:
    sqlite_path: str


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    include_roles: tuple[str, ...]
    include_skills: tuple[str, ...]
    exclude_keywords: tuple[str, ...]
    weights: Mapping[str, int]


@dataclass(frozen=True, slots=True)
class EnrichmentConfig:
    enabled: bool
    min_quality_score: float


@dataclass(frozen=True, slots=True)
class AppConfig:
    pipeline: PipelineConfig
    greenhouse: GreenhouseConfig
    smartrecruiters: SmartRecruitersCfg
    lever: LeverCfg
    sources_raw: Mapping[str, Mapping[str, Any]]
    enrichment: EnrichmentConfig
    scoring: ScoringConfig
    storage: StorageConfig
    notify: NotifyConfig


def _get(d: Mapping[str, Any], path: str, default: Any) -> Any:
    cur: Any = d

    for part in path.split("."):
        if not isinstance(cur, Mapping) or part not in cur:
            return default
        cur = cur[part]

    return cur


def load_config(path: str | Path) -> AppConfig:

    data = yaml.safe_load(Path(path).read_text()) or {}
    raw_sources = _get(data, "sources", {}) or {}
    if not isinstance(raw_sources, Mapping):
        raw_sources = {}

    pipeline = PipelineConfig(
        int(_get(data, "pipeline.instant_threshold", 85)),
        int(_get(data, "pipeline.digest_threshold", 70)),
        int(_get(data, "pipeline.digest_max_items", 15)),
    )

    greenhouse = GreenhouseConfig(
        bool(_get(data, "sources.greenhouse.enabled", True)),
        tuple(_get(data, "sources.greenhouse.boards", []) or []),
        bool(_get(data, "sources.greenhouse.content", True)),
    )

    smartrecruiters = SmartRecruitersCfg(
        bool(_get(data, "sources.smartrecruiters.enabled", False)),
        tuple(_get(data, "sources.smartrecruiters.companies", []) or []),
        int(_get(data, "sources.smartrecruiters.limit", 100)),
    )
    lever = LeverCfg(
        bool(_get(data, "sources.lever.enabled", False)),
        tuple(_get(data, "sources.lever.companies", []) or []),
    )

    scoring = ScoringConfig(
        tuple(_get(data, "scoring.include.roles", []) or []),
        tuple(_get(data, "scoring.include.skills", []) or []),
        tuple(_get(data, "scoring.exclude.keywords", []) or []),
        _get(data, "scoring.weights", {}) or {},
    )
    enrichment = EnrichmentConfig(
        bool(_get(data, "enrichment.enabled", True)),
        float(_get(data, "enrichment.min_quality_score", 0.25)),
    )

    storage = StorageConfig(
        str(_get(data, "storage.sqlite_path", "data/jobintel.sqlite"))
    )

    notify = NotifyConfig(
        str(_get(data, "notify.mode", "stdout")),
        str(_get(data, "notify.telegram.bot_token", "")),
        str(_get(data, "notify.telegram.chat_id", "")),
    )

    return AppConfig(
        pipeline,
        greenhouse,
        smartrecruiters,
        lever,
        {k: v for k, v in raw_sources.items() if isinstance(k, str) and isinstance(v, Mapping)},
        enrichment,
        scoring,
        storage,
        notify,
    )
