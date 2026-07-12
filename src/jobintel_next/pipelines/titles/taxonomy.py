from __future__ import annotations


class TitleTaxonomy:
    def __init__(self, mapping: dict[str, str]) -> None:
        self._mapping = dict(mapping)

    @property
    def normalized_titles(self) -> set[str]:
        return set(self._mapping.keys())

    @property
    def role_families(self) -> set[str]:
        return set(self._mapping.values())

    def role_family_for(self, normalized_title: str) -> str | None:
        return self._mapping.get(normalized_title)

    def validate_mapping(self, normalized_title: str, role_family: str) -> bool:
        return self._mapping.get(normalized_title) == role_family


def get_default_taxonomy() -> TitleTaxonomy:
    # Minimal stable v1 taxonomy for the title stage.
    return TitleTaxonomy(
        {
            "software_engineer": "software_engineering",
            "engineering_manager": "software_engineering",
            "devops_engineer": "devops",
            "site_reliability_engineer": "sre",
            "ml_engineer": "machine_learning",
            "data_scientist": "data_science",
            "solutions_architect": "architecture",
            "it_support_specialist": "it_operations",
            "systems_engineer": "it_operations",
            "network_engineer": "it_operations",
            "executive_assistant": "administrative_support",
            "product_designer": "design",
            "data_engineer": "data_engineering",
            "data_analyst": "data_analytics",
            "analytics_engineer": "data_analytics",
            "product_manager": "product_management",
            "account_executive": "sales",
            "account_manager": "sales",
            "sales_manager": "sales",
            "sales_engineer": "sales",
            "business_development_representative": "sales",
            "customer_success_manager": "customer_success",
            "marketing_specialist": "marketing",
            "financial_analyst": "finance",
            "quantitative_researcher": "finance",
            "credit_analyst": "finance",
            "wealth_advisor": "finance",
            "accountant": "finance",
            "legal_counsel": "legal",
            "paralegal": "legal",
            "technical_recruiter": "recruiting",
            "people_business_partner": "people_operations",
            "hr_generalist": "people_operations",
            "technical_writer": "content",
            "story_editor": "content",
            "journalist": "content",
            "content_producer": "content",
            "ai_trainer_specialist": "operations",
            "ai_trainer_generalist": "operations",
            "ux_researcher": "design",
            "art_director": "design",
            "creative_director": "design",
            "operations_specialist": "operations",
            "flight_attendant": "operations",
            "project_manager": "program_management",
            "technical_program_manager": "program_management",
            "electrical_engineer": "industrial_engineering",
            "mechanical_engineer": "industrial_engineering",
            "manufacturing_engineer": "industrial_engineering",
            "licensed_practical_nurse": "healthcare_clinical",
            "medical_assistant": "healthcare_clinical",
            "certified_nursing_assistant": "healthcare_clinical",
            "pharmacy_technician": "healthcare_clinical",
            "patient_care_technician": "healthcare_clinical",
            "nurse_practitioner": "healthcare_clinical",
            "registered_nurse": "healthcare_clinical",
            "physician": "healthcare_clinical",
            "psychiatrist": "healthcare_clinical",
            "psychotherapist": "healthcare_clinical",
            "occupational_therapist": "healthcare_clinical",
            "respiratory_therapist": "healthcare_clinical",
            "health_information_specialist": "healthcare_clinical",
            "behavioral_support_specialist": "healthcare_clinical",
            "speech_language_pathologist": "healthcare_clinical",
            "technician": "skilled_trades",
            "car_detailer": "skilled_trades",
            "field_technician": "skilled_trades",
            "mechanic": "skilled_trades",
            "logistics_coordinator": "logistics",
            "warehouse_associate": "logistics",
            "supply_chain_specialist": "logistics",
            "logistics_manager": "logistics",
            "driver": "logistics",
            "delivery_driver": "logistics",
            "compliance_manager": "compliance_risk",
            "compliance_specialist": "compliance_risk",
            "assistant_teacher": "education",
            "substitute_teacher": "education",
            "teacher": "education",
            "school_counselor": "education",
            "school_administrator": "education",
            "store_associate": "sales",
            "customer_service_specialist": "operations",
            "non_role_recruiting_entry": "non_role",
            "other": "other",
        }
    )
