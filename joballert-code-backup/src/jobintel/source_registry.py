from __future__ import annotations

import importlib
import pkgutil
from typing import Any, Callable, Mapping

from .interfaces import Collector

SourceBuilder = Callable[[Mapping[str, Any]], Collector | None]
SOURCE_REGISTRY: dict[str, SourceBuilder] = {}
_LOADED = False


def _load_registry() -> None:
    global _LOADED
    if _LOADED:
        return

    package_name = "jobintel.collectors"
    package = importlib.import_module(package_name)

    for mod_info in pkgutil.iter_modules(package.__path__):
        mod_name = mod_info.name
        if mod_name.startswith("_"):
            continue
        module = importlib.import_module(f"{package_name}.{mod_name}")
        source_name = getattr(module, "SOURCE_NAME", None)
        builder = getattr(module, "build_collector", None)
        if isinstance(source_name, str) and source_name and callable(builder):
            SOURCE_REGISTRY[source_name] = builder

    _LOADED = True


def build_collectors_from_sources(sources: Mapping[str, Mapping[str, Any]]) -> list[Collector]:
    _load_registry()
    collectors: list[Collector] = []
    for source_name, source_cfg in sources.items():
        builder = SOURCE_REGISTRY.get(source_name)
        if not builder:
            # Unknown source: ignored by design to keep core source-agnostic.
            continue
        col = builder(source_cfg)
        if col is not None:
            collectors.append(col)
    return collectors
