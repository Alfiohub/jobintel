from __future__ import annotations

from automation.microsaas.run_microsaas_pipeline import (
    clean_row,
    compute_embedding,
    extract_tags,
    normalize_title,
    _extract_location_type,
    _extract_salary,
)


def test_normalize_title_account_executive() -> None:
    normalized, family, group = normalize_title("Senior Account Executive - NYC - Hybrid")
    assert normalized == "account_executive"
    assert family == "sales"
    assert group == "business"


def test_normalize_title_data_analytics_director_not_other() -> None:
    normalized, family, group = normalize_title("Data Analytics Director")
    assert normalized == "analytics_director"
    assert family == "data_analytics"
    assert group == "data"


def test_normalize_title_bi_analyst_not_other() -> None:
    normalized, family, group = normalize_title("Senior BI Analyst")
    assert normalized == "business_intelligence_analyst"
    assert family == "data_analytics"
    assert group == "data"


def test_normalize_title_field_cto_not_other() -> None:
    normalized, family, group = normalize_title("Field CTO")
    assert normalized == "chief_technology_officer"
    assert family == "executive_leadership"
    assert group == "business"


def test_normalize_title_business_analyst_not_other() -> None:
    normalized, family, group = normalize_title("Business Analyst - Retail Energy")
    assert normalized == "business_analyst"
    assert family == "business_analysis"
    assert group == "business"


def test_normalize_title_consultant_not_other() -> None:
    normalized, family, group = normalize_title("Senior Management Consultant")
    assert normalized == "consultant"
    assert family == "consulting"
    assert group == "business"


def test_normalize_title_product_management_not_other() -> None:
    normalized, family, group = normalize_title("Director, Product Management")
    assert normalized == "product_manager"
    assert family == "product_management"
    assert group == "product"


def test_normalize_title_machine_learning_scientist_not_other() -> None:
    normalized, family, group = normalize_title("Staff/Senior Machine Learning Scientist (Ad Cloud)")
    assert normalized == "ml_scientist"
    assert family == "machine_learning"
    assert group == "data"


def test_normalize_title_legal_counsel_not_other() -> None:
    normalized, family, group = normalize_title("Senior Employment Counsel")
    assert normalized == "legal_counsel"
    assert family == "legal"
    assert group == "business"


def test_normalize_title_accountant_not_other() -> None:
    normalized, family, group = normalize_title("Assistant Controller - US Region")
    assert normalized == "accountant"
    assert family == "finance"
    assert group == "finance"


def test_normalize_title_product_design_not_other() -> None:
    normalized, family, group = normalize_title("Director, Product Design")
    assert normalized == "product_designer"
    assert family == "design"
    assert group == "design"


def test_normalize_title_salesforce_admin_not_other() -> None:
    normalized, family, group = normalize_title("Senior Salesforce Administrator")
    assert normalized == "systems_administrator"
    assert family == "it_operations"
    assert group == "engineering"


def test_normalize_title_strategic_accounts_not_other() -> None:
    normalized, family, group = normalize_title("Director of Strategic Accounts, Central U.S.")
    assert normalized == "account_manager"
    assert family == "sales"
    assert group == "business"


def test_normalize_title_tpm_not_other() -> None:
    normalized, family, group = normalize_title("Director of TPM, Connected Devices")
    assert normalized == "technical_program_manager"
    assert family == "program_management"
    assert group == "product"


def test_normalize_title_chief_revenue_officer_not_other() -> None:
    normalized, family, group = normalize_title("Chief Revenue Officer")
    assert normalized == "chief_revenue_officer"
    assert family == "executive_leadership"
    assert group == "business"


def test_normalize_title_technical_support_not_other() -> None:
    normalized, family, group = normalize_title("Technical Support Specialist - Spanish")
    assert normalized == "it_support_specialist"
    assert family == "it_operations"
    assert group == "engineering"


def test_normalize_title_alliance_director_not_other() -> None:
    normalized, family, group = normalize_title("Dell Global Alliance Director")
    assert normalized == "alliance_manager"
    assert family == "partnerships"
    assert group == "business"


def test_extract_location_type_prefers_hybrid_over_remote() -> None:
    text = "This role is hybrid. You can work remotely two days per week."
    assert _extract_location_type(text) == "hybrid"


def test_extract_salary_k_suffix_and_usd() -> None:
    s_min, s_max, cur = _extract_salary("Compensation: $120k - $150k per year")
    assert s_min == 120000
    assert s_max == 150000
    assert cur == "USD"


def test_extract_salary_eur_range() -> None:
    s_min, s_max, cur = _extract_salary("Salary range 70,000 - 90,000 EUR annual gross")
    assert s_min == 70000
    assert s_max == 90000
    assert cur == "EUR"


def test_extract_salary_ignores_funding_magnitude() -> None:
    s_min, s_max, cur = _extract_salary(
        "Since launch the company is backed by $130M+ from investors and serves 250,000 patients."
    )
    assert s_min is None
    assert s_max is None
    assert cur in ("USD", None)


def test_extract_tags_role_salary_and_skills() -> None:
    row = {
        "title": "Senior Data Engineer",
        "location_raw": "New York, NY",
        "description_text": (
            "Full-time remote role. Build pipelines with Python, SQL, Airflow and AWS. "
            "Compensation: $120,000 - $150,000 per year."
        ),
        "language": "en",
    }
    clean = clean_row(row)
    tags = extract_tags(clean, normalized_title="data_engineer")

    assert tags["seniority"] == "senior"
    assert tags["employment_type"] == "full_time"
    assert tags["location_type"] == "remote"
    assert tags["salary_min"] == 120000
    assert tags["salary_max"] == 150000
    assert tags["salary_currency"] == "USD"
    assert {"python", "sql", "airflow", "aws"}.issubset(set(tags["skills"]))


def test_compute_embedding_hash_mode_returns_vector() -> None:
    emb, model = compute_embedding(
        "data engineer python sql",
        mode="hash",
        openai_model="text-embedding-3-small",
        gemini_model="text-embedding-004",
        timeout_s=10,
    )
    assert isinstance(emb, list)
    assert len(emb) == 24
    assert model == "hash_v1"
