from __future__ import annotations

"""
Deprecated compatibility shim.
Use `jobintel_next.adapters.greenhouse.client` and
`jobintel_next.adapters.greenhouse.mapper` instead.
"""

from jobintel_next.adapters.greenhouse.client import GreenhouseAPIClient
from jobintel_next.adapters.greenhouse.mapper import CanonicalRawJob

# Backward-compatible names for old imports.
GreenhouseClient = GreenhouseAPIClient
GreenhouseJob = CanonicalRawJob

__all__ = ["GreenhouseClient", "GreenhouseJob"]
