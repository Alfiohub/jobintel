from automation.microsaas.titles.title_cleaning import clean_title


def test_clean_title_removes_metadata_suffix() -> None:
    raw = "Senior Payroll Analyst - Shift (4 PM - 1 AM IST)"
    assert clean_title(raw) == "Senior Payroll Analyst"
