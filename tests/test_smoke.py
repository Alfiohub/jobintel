from jobintel_next.config import load_config


def test_config_loads() -> None:
    cfg = load_config()
    assert cfg.greenhouse_timeout_sec > 0
    assert cfg.greenhouse_max_retries >= 1
