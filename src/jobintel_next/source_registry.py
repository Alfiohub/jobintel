from __future__ import annotations

from typing import Any, Mapping

from jobintel_next.ingestion.collectors.greenhouse_collector import (
    build_collector as build_greenhouse_collector,
)


def build_collectors_from_sources(sources: Mapping[str, Mapping[str, Any]]) -> list[Any]:
    collectors: list[Any] = []
    gh_cfg = sources.get("greenhouse")
    if isinstance(gh_cfg, Mapping):
        col = build_greenhouse_collector(gh_cfg)
        if col is not None:
            collectors.append(col)
    return collectors
