from automation.microsaas.titles.title_cleaning import clean_title, normalize_for_match
from automation.microsaas.titles.title_location_noise import strip_simple_location_noise
from automation.microsaas.titles.title_variants import normalize_lexical_variants, strip_seniority_tokens


def _flow(text: str) -> str:
    cleaned = clean_title(text)
    norm = normalize_for_match(cleaned)
    norm = normalize_lexical_variants(norm)
    norm = strip_seniority_tokens(norm)
    return strip_simple_location_noise(norm)


def test_backend_engineer_berlin_germany() -> None:
    assert _flow("Backend Engineer - Berlin, Germany") == "backend engineer"


def test_account_manager_austin_tx() -> None:
    assert _flow("Account Manager | Austin, TX") == "account manager"


def test_designer_london() -> None:
    assert _flow("Designer - London") == "designer"


def test_data_engineer_emea() -> None:
    assert _flow("Data Engineer - EMEA") == "data engineer"


def test_senior_backend_remote_germany() -> None:
    assert _flow("Senior Backend Engineer - Remote, Germany") == "backend engineer"


def test_sales_director_apac() -> None:
    assert _flow("Sales Director, APAC") == "sales director"


def test_partner_lead_dach() -> None:
    assert _flow("Partner Lead - DACH") == "partner lead"


def test_account_executive_latam() -> None:
    assert _flow("Account Executive - LATAM") == "account executive"

