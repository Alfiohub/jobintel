from jobintel_next.adapters.greenhouse.client import GreenhouseAPIClient
from jobintel_next.adapters.greenhouse.mapper import CanonicalRawJob
from jobintel_next.collectors.greenhouse import GreenhouseCollector
from jobintel_next.ingestion.collectors.greenhouse_collector import GreenhouseCollector as NewGreenhouseCollector
from jobintel_next.clients.greenhouse import GreenhouseClient, GreenhouseJob


def test_legacy_shims_point_to_new_paths() -> None:
    assert GreenhouseClient is GreenhouseAPIClient
    assert GreenhouseJob is CanonicalRawJob
    assert GreenhouseCollector is NewGreenhouseCollector
