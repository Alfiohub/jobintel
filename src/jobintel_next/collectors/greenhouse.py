from __future__ import annotations

"""
Deprecated compatibility shim.
Official path is `jobintel_next.ingestion.collectors.greenhouse_collector`.
"""

from jobintel_next.ingestion.collectors.greenhouse_collector import (  # noqa: F401
    SOURCE_NAME,
    GreenhouseCollector,
    GreenhouseCollectorConfig,
    build_collector,
)

__all__ = ["SOURCE_NAME", "GreenhouseCollector", "GreenhouseCollectorConfig", "build_collector"]
