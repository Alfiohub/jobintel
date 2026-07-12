from automation.microsaas.titles.title_taxonomy import get_default_taxonomy


def test_validate_mapping_contract() -> None:
    tx = get_default_taxonomy()
    assert tx.validate_mapping("software_engineer", "software_engineering")
    assert not tx.validate_mapping("software_engineer", "sales")
