from automation.microsaas.titles.title_classifier import TitleClassifier


def test_rule_match_specific_architect() -> None:
    c = TitleClassifier()
    r = c.classify("Partner Innovation Architect")
    assert r.normalized_title == "solutions_architect"
    assert r.role_family == "architecture"
    assert r.classification_status == "matched"
    assert r.matched_rule_id == "arch_partner_innovation"


def test_rule_match_nurse_practitioner() -> None:
    c = TitleClassifier()
    r = c.classify("Psychiatric Mental Health Nurse Practitioner (PMHNP)")
    assert r.normalized_title == "nurse_practitioner"
    assert r.role_family == "healthcare_clinical"


def test_rule_match_psychiatrist() -> None:
    c = TitleClassifier()
    r = c.classify("Psychiatrist (MD)")
    assert r.normalized_title == "psychiatrist"
    assert r.role_family == "healthcare_clinical"


def test_rule_match_cdl_driver() -> None:
    c = TitleClassifier()
    r = c.classify("CDL Drivers")
    assert r.normalized_title == "driver"
    assert r.role_family == "logistics"


def test_rule_match_field_technician() -> None:
    c = TitleClassifier()
    r = c.classify("Heavy Equipment Field Technician (Mechanic)")
    assert r.normalized_title == "field_technician"
    assert r.role_family == "skilled_trades"


def test_rule_match_executive_assistant() -> None:
    c = TitleClassifier()
    r = c.classify("Executive Assistant")
    assert r.normalized_title == "executive_assistant"
    assert r.role_family == "administrative_support"


def test_rule_match_project_manager() -> None:
    c = TitleClassifier()
    r = c.classify("Project Manager")
    assert r.normalized_title == "project_manager"
    assert r.role_family == "program_management"


def test_rule_match_program_manager() -> None:
    c = TitleClassifier()
    r = c.classify("Program Manager")
    assert r.normalized_title == "project_manager"
    assert r.role_family == "program_management"


def test_rule_match_accounting_manager() -> None:
    c = TitleClassifier()
    r = c.classify("Accounting Manager")
    assert r.normalized_title == "accountant"
    assert r.role_family == "finance"


def test_rule_match_licensed_mental_health_therapist() -> None:
    c = TitleClassifier()
    r = c.classify("Licensed Mental Health Therapist")
    assert r.normalized_title == "psychotherapist"
    assert r.role_family == "healthcare_clinical"


def test_rule_match_wealth_advisor() -> None:
    c = TitleClassifier()
    r = c.classify("Associate Wealth Advisor")
    assert r.normalized_title == "investment_analyst"
    assert r.role_family == "finance"


def test_rule_match_store_associate() -> None:
    c = TitleClassifier()
    r = c.classify("Lead Store Associate")
    assert r.normalized_title == "store_associate"
    assert r.role_family == "sales"


def test_rule_match_case_manager() -> None:
    c = TitleClassifier()
    r = c.classify("Bilingual Case Manager")
    assert r.normalized_title == "operations_specialist"
    assert r.role_family == "operations"


def test_rule_match_partnerships_manager() -> None:
    c = TitleClassifier()
    r = c.classify("Senior Market Strategy and Partnerships Manager")
    assert r.normalized_title == "alliance_manager"
    assert r.role_family == "partnerships"


def test_general_manager_kept_other_with_reason() -> None:
    c = TitleClassifier()
    r = c.classify("General Manager")
    assert r.normalized_title == "other"
    assert r.role_family == "other"
    assert "ambiguous_general_manager" in r.notes


def test_intervention_specialist_maps_to_mental_health_specialist() -> None:
    c = TitleClassifier()
    r = c.classify("Intervention Specialist")
    assert r.normalized_title == "mental_health_specialist"
    assert r.role_family == "healthcare_clinical"


def test_registered_nurse_rule() -> None:
    c = TitleClassifier()
    r = c.classify("Registered Nurse (RN)")
    assert r.normalized_title == "registered_nurse"
    assert r.role_family == "healthcare_clinical"


def test_primary_care_physician_rule() -> None:
    c = TitleClassifier()
    r = c.classify("Primary Care Physician")
    assert r.normalized_title == "healthcare_provider"
    assert r.role_family == "healthcare"


def test_business_development_manager_maps_sales() -> None:
    c = TitleClassifier()
    r = c.classify("Business Development Manager")
    assert r.normalized_title == "account_manager"
    assert r.role_family == "sales"


def test_social_media_manager_maps_marketing() -> None:
    c = TitleClassifier()
    r = c.classify("Social Media Manager")
    assert r.normalized_title == "marketing_specialist"
    assert r.role_family == "marketing"


def test_rental_coordinator_maps_operations_specialist() -> None:
    c = TitleClassifier()
    r = c.classify("Rental Coordinator")
    assert r.normalized_title == "operations_specialist"
    assert r.role_family == "operations"


def test_customer_support_specialist_maps_customer_service_specialist() -> None:
    c = TitleClassifier()
    r = c.classify("Customer Support Specialist")
    assert r.normalized_title == "customer_service_specialist"
    assert r.role_family == "operations"


def test_senior_qa_engineer_maps_software_engineer() -> None:
    c = TitleClassifier()
    r = c.classify("Senior QA Engineer")
    assert r.normalized_title == "software_engineer"
    assert r.role_family == "software_engineering"


def test_manager_software_engineering_maps_engineering_manager() -> None:
    c = TitleClassifier()
    r = c.classify("Manager, Software Engineering")
    assert r.normalized_title == "engineering_manager"
    assert r.role_family == "software_engineering"


def test_clinical_research_nurse_maps_registered_nurse() -> None:
    c = TitleClassifier()
    r = c.classify("Per Diem Clinical Research Nurse - Home Visits")
    assert r.normalized_title == "registered_nurse"
    assert r.role_family == "healthcare_clinical"


def test_occupational_therapist_maps_healthcare_allied() -> None:
    c = TitleClassifier()
    r = c.classify("Occupational Therapist")
    assert r.normalized_title == "occupational_therapist"
    assert r.role_family == "healthcare_clinical"


def test_medical_assistant_maps_healthcare_allied() -> None:
    c = TitleClassifier()
    r = c.classify("Medical Assistant")
    assert r.normalized_title == "medical_assistant"
    assert r.role_family == "healthcare_clinical"


def test_floor_lead_retail_maps_store_associate() -> None:
    c = TitleClassifier()
    r = c.classify("Floor Lead (Retail) (Part-time)")
    assert r.normalized_title == "store_associate"
    assert r.role_family == "sales"


def test_accounts_payable_specialist_maps_finance() -> None:
    c = TitleClassifier()
    r = c.classify("Accounts Payable Specialist")
    assert r.normalized_title == "financial_analyst"
    assert r.role_family == "finance"


def test_regional_safety_manager_maps_operations() -> None:
    c = TitleClassifier()
    r = c.classify("Regional Safety Manager")
    assert r.normalized_title == "operations_specialist"
    assert r.role_family == "operations"


def test_telematics_installer_maps_technician() -> None:
    c = TitleClassifier()
    r = c.classify("Telematics Installer")
    assert r.normalized_title == "technician"
    assert r.role_family == "skilled_trades"


def test_quantitative_researcher_maps_data_science() -> None:
    c = TitleClassifier()
    r = c.classify("Quantitative Researcher")
    assert r.normalized_title == "data_scientist"
    assert r.role_family == "data_science"


def test_senior_product_analyst_maps_business_analyst() -> None:
    c = TitleClassifier()
    r = c.classify("Senior Product Analyst")
    assert r.normalized_title == "business_analyst"
    assert r.role_family == "business_analysis"


def test_account_development_representative_maps_bdr() -> None:
    c = TitleClassifier()
    r = c.classify("Account Development Representative")
    assert r.normalized_title == "business_development_representative"
    assert r.role_family == "sales"


def test_administrative_assistant_maps_admin_support() -> None:
    c = TitleClassifier()
    r = c.classify("Administrative Assistant")
    assert r.normalized_title == "administrative_assistant"
    assert r.role_family == "administrative_support"


def test_chief_of_staff_maps_admin_support() -> None:
    c = TitleClassifier()
    r = c.classify("Chief of Staff")
    assert r.normalized_title == "chief_of_staff"
    assert r.role_family == "administrative_support"


def test_technical_writer_maps_content_designer() -> None:
    c = TitleClassifier()
    r = c.classify("Technical Writer")
    assert r.normalized_title == "content_designer"
    assert r.role_family == "design"


def test_senior_brand_designer_maps_product_designer() -> None:
    c = TitleClassifier()
    r = c.classify("Senior Brand Designer")
    assert r.normalized_title == "product_designer"
    assert r.role_family == "design"


def test_auto_painter_maps_skilled_trades() -> None:
    c = TitleClassifier()
    r = c.classify("Auto Painter")
    assert r.normalized_title == "auto_painter"
    assert r.role_family == "skilled_trades"


def test_producer_maps_content_designer() -> None:
    c = TitleClassifier()
    r = c.classify("Producer")
    assert r.normalized_title == "content_designer"
    assert r.role_family == "design"


def test_story_desk_editor_maps_content_designer() -> None:
    c = TitleClassifier()
    r = c.classify("Story Desk Editor")
    assert r.normalized_title == "content_designer"
    assert r.role_family == "design"


def test_multiskilled_journalist_maps_content_designer() -> None:
    c = TitleClassifier()
    r = c.classify("Multiskilled Journalist")
    assert r.normalized_title == "content_designer"
    assert r.role_family == "design"


def test_media_manager_maps_content_designer() -> None:
    c = TitleClassifier()
    r = c.classify("Media Manager")
    assert r.normalized_title == "content_designer"
    assert r.role_family == "design"


def test_personal_care_specialist_maps_healthcare_clinical() -> None:
    c = TitleClassifier()
    r = c.classify("Personal Care Specialist (Part Time)")
    assert r.normalized_title == "personal_care_specialist"
    assert r.role_family == "healthcare_clinical"


def test_collaborating_physician_maps_healthcare_provider() -> None:
    c = TitleClassifier()
    r = c.classify("Collaborating Physician (1099 Contract) - Virtual Women's Health")
    assert r.normalized_title == "healthcare_provider"
    assert r.role_family == "healthcare"


def test_auto_body_repair_tech_maps_mechanic_v27() -> None:
    c = TitleClassifier()
    r = c.classify("Autobody Repair Tech - $4,000 Bonus")
    assert r.normalized_title == "mechanic"
    assert r.role_family == "skilled_trades"
    assert r.matched_rule_id == "trades_auto_body_repair_precision_v27"


def test_auto_body_prepper_maps_mechanic_v27() -> None:
    c = TitleClassifier()
    r = c.classify("Auto Body Prepper")
    assert r.normalized_title == "mechanic"
    assert r.role_family == "skilled_trades"
    assert r.matched_rule_id == "trades_auto_body_repair_precision_v27"


def test_paintless_dent_repair_tech_maps_mechanic_v27() -> None:
    c = TitleClassifier()
    r = c.classify("Paintless Dent Repair Tech - $6,000 Bonus")
    assert r.normalized_title == "mechanic"
    assert r.role_family == "skilled_trades"
    assert r.matched_rule_id == "trades_auto_body_repair_precision_v27"


def test_it_services_technician_not_overmatched_v27() -> None:
    c = TitleClassifier()
    r = c.classify("IT Services Technician")
    assert r.normalized_title != "mechanic"
    assert r.matched_rule_id != "trades_auto_body_repair_precision_v27"


def test_engineering_technician_not_overmatched_v27() -> None:
    c = TitleClassifier()
    r = c.classify("Engineering Technician")
    assert r.normalized_title != "mechanic"
    assert r.matched_rule_id != "trades_auto_body_repair_precision_v27"


def test_field_service_engineer_not_overmatched_v27() -> None:
    c = TitleClassifier()
    r = c.classify("Robotics Field Service Engineer")
    assert r.normalized_title != "mechanic"
    assert r.matched_rule_id != "trades_auto_body_repair_precision_v27"


def test_amt_instructor_maps_teacher() -> None:
    c = TitleClassifier()
    r = c.classify("AMT Instructor")
    assert r.normalized_title == "teacher"
    assert r.role_family == "education"


def test_instructional_aide_maps_assistant_teacher() -> None:
    c = TitleClassifier()
    r = c.classify("Instructional Aide")
    assert r.normalized_title == "assistant_teacher"
    assert r.role_family == "education"


def test_account_director_maps_account_manager() -> None:
    c = TitleClassifier()
    r = c.classify("Account Director")
    assert r.normalized_title == "account_manager"
    assert r.role_family == "sales"


def test_deal_desk_analyst_maps_business_analyst() -> None:
    c = TitleClassifier()
    r = c.classify("Deal Desk Analyst")
    assert r.normalized_title == "business_analyst"
    assert r.role_family == "business_analysis"


def test_fpa_manager_maps_financial_analyst() -> None:
    c = TitleClassifier()
    r = c.classify("FP&A Manager")
    assert r.normalized_title == "financial_analyst"
    assert r.role_family == "finance"
