from automation.microsaas.titles.title_variants import (
    expand_abbreviations,
    normalize_plural_forms,
)


def test_plural_managers_to_manager() -> None:
    assert normalize_plural_forms("engineering managers") == "engineering manager"


def test_plural_technicians_to_technician() -> None:
    assert normalize_plural_forms("field technicians") == "field technician"


def test_plural_drivers_to_driver() -> None:
    assert normalize_plural_forms("cdl drivers") == "cdl driver"


def test_plural_psychotherapists_to_psychotherapist() -> None:
    assert normalize_plural_forms("licensed psychotherapists") == "licensed psychotherapist"


def test_abbreviation_sr_to_senior() -> None:
    assert expand_abbreviations("sr data analyst") == "senior data analyst"


def test_abbreviation_jr_to_junior() -> None:
    assert expand_abbreviations("jr software engineer") == "junior software engineer"


def test_abbreviation_vp_to_vice_president() -> None:
    assert expand_abbreviations("vp sales") == "vice president sales"
