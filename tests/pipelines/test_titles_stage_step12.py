from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.domain.models import TitleClassification
from jobintel_next.pipelines.titles.classifier import TitleClassifier
from jobintel_next.pipelines.titles.location_noise import strip_simple_location_noise
from jobintel_next.pipelines.titles.run import run_title_stage
from jobintel_next.pipelines.titles.taxonomy import TitleTaxonomy, get_default_taxonomy
from jobintel_next.pipelines.titles.text_utils import normalize_title_for_match
from jobintel_next.pipelines.titles.variants import normalize_variants


def test_mapping_base_cases() -> None:
    clf = TitleClassifier()
    cases = [
        ("https://e/1", "Senior Software Engineer", "software_engineer", "software_engineering"),
        ("https://e/2", "Data Engineer", "data_engineer", "data_engineering"),
        ("https://e/3", "Product Manager", "product_manager", "product_management"),
        ("https://e/4", "Account Executive", "account_executive", "sales"),
        ("https://e/5", "Customer Success Manager", "customer_success_manager", "customer_success"),
        ("https://e/6", "Engineering Manager", "engineering_manager", "software_engineering"),
        ("https://e/7", "Psychiatric Mental Health Nurse Practitioner (PMHNP)", "nurse_practitioner", "healthcare_clinical"),
        ("https://e/8", "Psychiatrist (MD)", "psychiatrist", "healthcare_clinical"),
        ("https://e/9", "Psychotherapist", "psychotherapist", "healthcare_clinical"),
        ("https://e/10", "Future Technicians", "technician", "skilled_trades"),
        ("https://e/11", "Heavy Equipment Field Technician (Mechanic)", "field_technician", "skilled_trades"),
        ("https://e/12", "Heavy Equipment Shop Technician (Mechanic)", "mechanic", "skilled_trades"),
        ("https://e/13", "CDL Drivers", "driver", "logistics"),
        ("https://e/14", "Customer Delivery Driver", "delivery_driver", "logistics"),
        ("https://e/15", "Compliance Manager", "compliance_manager", "compliance_risk"),
        ("https://e/16", "Compliance Specialist", "compliance_specialist", "compliance_risk"),
        ("https://e/17", "Compliance Analyst", "compliance_specialist", "compliance_risk"),
        ("https://e/18", "Affiliate Compliance Manager", "compliance_manager", "compliance_risk"),
        ("https://e/19", "Affiliate Compliance Specialist", "compliance_specialist", "compliance_risk"),
        ("https://e/20", "Compliance Associate", "compliance_specialist", "compliance_risk"),
        ("https://e/21", "Assistant Teacher", "assistant_teacher", "education"),
        ("https://e/22", "Substitute Teacher", "substitute_teacher", "education"),
        ("https://e/23", "Retail Sales Associate - Part Time", "store_associate", "sales"),
        ("https://e/24", "Customer Service Delivery Advocate", "customer_service_specialist", "operations"),
        ("https://e/24b", "Bilingual Member Services Representative (Remote, Spanish Speaking)", "customer_service_specialist", "operations"),
        ("https://e/25", "Senior DevOps Engineer", "devops_engineer", "devops"),
        ("https://e/26", "Senior Site Reliability Engineer", "site_reliability_engineer", "sre"),
        ("https://e/27", "Site Reliability Engineer", "site_reliability_engineer", "sre"),
        ("https://e/28", "Senior Machine Learning Engineer", "ml_engineer", "machine_learning"),
        ("https://e/29", "Senior Data Scientist", "data_scientist", "data_science"),
        ("https://e/30", "Solutions Architect", "solutions_architect", "architecture"),
        ("https://e/31", "Solutions Engineer", "sales_engineer", "sales"),
        ("https://e/32", "Technical Support Engineer", "it_support_specialist", "it_operations"),
        ("https://e/33", "Executive Assistant", "executive_assistant", "administrative_support"),
        ("https://e/34", "Senior Product Designer", "product_designer", "design"),
        ("https://e/35", "Senior Performance Copywriter, Personal Finance", "marketing_specialist", "marketing"),
        ("https://e/36", "Lead Video Ad Copywriter", "marketing_specialist", "marketing"),
        ("https://e/37", "Senior Manager, Google Paid Media", "marketing_specialist", "marketing"),
        ("https://e/38", "Sales Engineer", "sales_engineer", "sales"),
        ("https://e/39", "Senior Sales Engineer", "sales_engineer", "sales"),
        ("https://e/40", "Senior Security Engineer", "software_engineer", "software_engineering"),
        ("https://e/41", "Python Engineer", "software_engineer", "software_engineering"),
        ("https://e/42", "Health Information Specialist I", "health_information_specialist", "healthcare_clinical"),
        ("https://e/43", "Associate Wealth Advisor", "wealth_advisor", "finance"),
        ("https://e/44", "Behavior Technician", "behavioral_support_specialist", "healthcare_clinical"),
        ("https://e/45", "Registered Behavior Technician", "behavioral_support_specialist", "healthcare_clinical"),
        ("https://e/46", "Intervention Specialist", "behavioral_support_specialist", "healthcare_clinical"),
        ("https://e/46b", "Direct Support Professional (DSP)", "behavioral_support_specialist", "healthcare_clinical"),
        ("https://e/47", "Sales Associate", "store_associate", "sales"),
        ("https://e/48", "Lead Store Associate", "store_associate", "sales"),
        ("https://e/49", "Rental Coordinator", "operations_specialist", "operations"),
        ("https://e/50", "AI Engineer", "ml_engineer", "machine_learning"),
        ("https://e/51", "Senior AI Engineer", "ml_engineer", "machine_learning"),
        ("https://e/52", "Forward Deployed Engineer", "software_engineer", "software_engineering"),
        ("https://e/53", "Technical Sales and Field Service Engineer", "sales_engineer", "sales"),
        ("https://e/54", "Accounting Manager", "accountant", "finance"),
        ("https://e/55", "Business Development Manager", "account_manager", "sales"),
        ("https://e/58", "Solution Architect", "solutions_architect", "architecture"),
        ("https://e/62", "Sales Manager", "sales_manager", "sales"),
        ("https://e/63", "Regional Sales Director", "sales_manager", "sales"),
        ("https://e/64", "Manager, Sales Development", "business_development_representative", "sales"),
        ("https://e/64b", "Account Director", "account_manager", "sales"),
        ("https://e/65", "Senior Brand Designer", "marketing_specialist", "marketing"),
        ("https://e/66", "Finance Manager", "financial_analyst", "finance"),
        ("https://e/67", "Operations Manager", "operations_specialist", "operations"),
        ("https://e/68", "Implementation Consultant", "operations_specialist", "operations"),
        ("https://e/69", "Customer Support Specialist", "operations_specialist", "operations"),
        ("https://e/70", "Administrative Assistant", "operations_specialist", "operations"),
        ("https://e/71", "Senior Electrical Engineer", "electrical_engineer", "industrial_engineering"),
        ("https://e/72", "Electrical Engineer", "electrical_engineer", "industrial_engineering"),
        ("https://e/72b", "Systems Engineer", "systems_engineer", "it_operations"),
        ("https://e/72c", "Senior Systems Engineer", "systems_engineer", "it_operations"),
        ("https://e/72d", "Network Engineer", "network_engineer", "it_operations"),
        ("https://e/72e", "Senior Network Engineer", "network_engineer", "it_operations"),
        ("https://e/73", "Senior Mechanical Engineer", "mechanical_engineer", "industrial_engineering"),
        ("https://e/74", "Mechanical Engineer", "mechanical_engineer", "industrial_engineering"),
        ("https://e/75", "Production Technician", "technician", "skilled_trades"),
        ("https://e/76", "Entry-level Auto Technician", "mechanic", "skilled_trades"),
        ("https://e/77", "Brake and Tire Auto Technician", "mechanic", "skilled_trades"),
        ("https://e/78", "Senior Manufacturing Engineer", "manufacturing_engineer", "industrial_engineering"),
        ("https://e/79", "Maintenance Technician", "technician", "skilled_trades"),
        ("https://e/80", "Licensed Practical Nurse (LPN)", "licensed_practical_nurse", "healthcare_clinical"),
        ("https://e/81", "Medical Assistant", "medical_assistant", "healthcare_clinical"),
        ("https://e/81b", "Certified Nursing Assistant (CNA)", "certified_nursing_assistant", "healthcare_clinical"),
        ("https://e/81c", "Specialty Pharmacy Technician", "pharmacy_technician", "healthcare_clinical"),
        ("https://e/81d", "Patient Care Technician - HVU - FT - D - N", "patient_care_technician", "healthcare_clinical"),
        ("https://e/82", "Behavioral Interventionist", "behavioral_support_specialist", "healthcare_clinical"),
        ("https://e/82b", "Board Certified Behavior Analyst", "behavioral_support_specialist", "healthcare_clinical"),
        ("https://e/82c", "BCBA (Board Certified Behavior Analyst)", "behavioral_support_specialist", "healthcare_clinical"),
        ("https://e/83", "Licensed Mental Health Therapist - Remote", "psychotherapist", "healthcare_clinical"),
        ("https://e/84", "Per Diem Clinical Research Nurse - Home Visits", "registered_nurse", "healthcare_clinical"),
        ("https://e/85", "Lead Preschool Teacher", "teacher", "education"),
        ("https://e/86", "Lead Infant Teacher", "teacher", "education"),
        ("https://e/87", "Preschool Teacher", "teacher", "education"),
        ("https://e/88", "Infant Teacher", "teacher", "education"),
        ("https://e/89", "Lead Spanish Preschool Teacher", "teacher", "education"),
        ("https://e/89b", "Lead Preschool Spanish Teacher", "teacher", "education"),
        ("https://e/90", "Infant Assistant Teacher", "assistant_teacher", "education"),
        ("https://e/91", "Toddler Teaching Assistant", "assistant_teacher", "education"),
        ("https://e/91b", "K-5th Grade Teacher - SY 26-27", "teacher", "education"),
        ("https://e/91c", "Instructional Aide", "assistant_teacher", "education"),
        ("https://e/91d", "School Counselor", "school_counselor", "education"),
        ("https://e/91e", "Virtual School Counselor - SY 26-27", "school_counselor", "education"),
        ("https://e/91f", "School Director", "school_administrator", "education"),
        ("https://e/91g", "School Office Manager - SY 26-27", "school_administrator", "education"),
        ("https://e/91h", "Assistant Spanish Teacher", "assistant_teacher", "education"),
        ("https://e/94", "Assistant Store Manager", "operations_specialist", "operations"),
        ("https://e/95", "Retail Store Manager", "operations_specialist", "operations"),
        ("https://e/96", "Store Advisor", "store_associate", "sales"),
        ("https://e/97", "Retail - Lead Store Advisor（Bicester）", "store_associate", "sales"),
        ("https://e/100", "Mid-level Automotive Parts Associate", "store_associate", "sales"),
        ("https://e/101", "Entry-level Automotive Parts Associate", "store_associate", "sales"),
        ("https://e/102", "Inside Sales Representative", "account_executive", "sales"),
        ("https://e/103", "Solution Engineer", "sales_engineer", "sales"),
        ("https://e/104", "Senior People Business Partner", "people_business_partner", "people_operations"),
        ("https://e/105", "HR Business Partner", "people_business_partner", "people_operations"),
        ("https://e/106", "Technical Writer", "technical_writer", "content"),
        ("https://e/107", "Story Desk Editor", "story_editor", "content"),
        ("https://e/107b", "Multiskilled Journalist", "journalist", "content"),
        ("https://e/107c", "UX Researcher", "ux_researcher", "design"),
        ("https://e/107d", "Creative Director", "creative_director", "design"),
        ("https://e/107e", "Art Director", "art_director", "design"),
        ("https://e/107f", "Video Editor", "story_editor", "content"),
        ("https://e/107g", "Creative Producer", "content_producer", "content"),
        ("https://e/107h", "News Producer", "content_producer", "content"),
        ("https://e/107i", "Editing AI Content Producer", "content_producer", "content"),
        ("https://e/108", "Technical Support Specialist", "it_support_specialist", "it_operations"),
        ("https://e/109", "Solution Specialist", "sales_engineer", "sales"),
        ("https://e/110", "Auto Body Repair Technician", "mechanic", "skilled_trades"),
        ("https://e/111", "Commercial HVAC Service Technician", "technician", "skilled_trades"),
        ("https://e/112", "Diesel Technician", "mechanic", "skilled_trades"),
        ("https://e/113", "Telematics Installer", "technician", "skilled_trades"),
        ("https://e/114", "Lead Plumber", "field_technician", "skilled_trades"),
        ("https://e/115", "Mechanical Technician", "technician", "skilled_trades"),
        ("https://e/116", "Content Designer II", "product_designer", "design"),
        ("https://e/117", "Lead Visual Designer", "product_designer", "design"),
        ("https://e/118", "Lead Web Designer", "product_designer", "design"),
        ("https://e/119", "UX Designer - Design systems", "product_designer", "design"),
        ("https://e/120", "UI - UX Designer", "product_designer", "design"),
        ("https://e/121", "Director, Product Design", "product_designer", "design"),
        ("https://e/122", "Licensed Vocational Nurse (LVN)", "licensed_practical_nurse", "healthcare_clinical"),
        ("https://e/123", "Staff Nurse - Emergency Department", "registered_nurse", "healthcare_clinical"),
        ("https://e/124", "Licensed Clinical Social Worker (LCSW) - Remote", "psychotherapist", "healthcare_clinical"),
        ("https://e/125", "Mental Health Therapist", "psychotherapist", "healthcare_clinical"),
        ("https://e/126", "Clinical Therapist", "psychotherapist", "healthcare_clinical"),
        ("https://e/127", "Behavior Analyst (BCBA)", "behavioral_support_specialist", "healthcare_clinical"),
        ("https://e/128", "Third Party Risk Analyst", "compliance_specialist", "compliance_risk"),
        ("https://e/129", "Fraud Analyst", "compliance_specialist", "compliance_risk"),
        ("https://e/130", "AML Analyst", "compliance_specialist", "compliance_risk"),
        ("https://e/131", "Internal Audit Manager", "compliance_manager", "compliance_risk"),
        ("https://e/132", "Compliance Officer", "compliance_manager", "compliance_risk"),
        ("https://e/133", "Operational Risk Manager", "compliance_manager", "compliance_risk"),
        ("https://e/134", "Logistics Coordinator", "logistics_coordinator", "logistics"),
        ("https://e/135", "Warehouse Associate", "warehouse_associate", "logistics"),
        ("https://e/136", "Inventory Specialist", "warehouse_associate", "logistics"),
        ("https://e/137", "Supply Chain Specialist", "supply_chain_specialist", "logistics"),
        ("https://e/138", "Supply Chain Manager", "supply_chain_specialist", "logistics"),
        ("https://e/139", "Global Logistics Manager", "logistics_manager", "logistics"),
        ("https://e/140", "Dispatcher", "logistics_coordinator", "logistics"),
        ("https://e/141", "German Language Specialist - Freelance AI Trainer Project", "ai_trainer_specialist", "operations"),
        ("https://e/142", "Voice Actor - Freelance AI Trainer Project", "ai_trainer_generalist", "operations"),
        ("https://e/143", "Morning Executive Producer", "content_producer", "content"),
        ("https://e/144", "Insurance Producer - Atlanta, GA", "account_executive", "sales"),
        ("https://e/145", "Human Resources Business Partner", "people_business_partner", "people_operations"),
        ("https://e/146", "Systems Administrator", "it_support_specialist", "it_operations"),
        ("https://e/147", "Android Engineer", "software_engineer", "software_engineering"),
        ("https://e/148", "Corporate Paralegal", "paralegal", "legal"),
        ("https://e/149", "Application Support Engineer", "it_support_specialist", "it_operations"),
        ("https://e/150", "Occupational Therapist", "occupational_therapist", "healthcare_clinical"),
        ("https://e/151", "Respiratory Therapist - Registered", "respiratory_therapist", "healthcare_clinical"),
        ("https://e/152", "Insurance Agent - Austin, TX", "account_executive", "sales"),
        ("https://e/153", "HR Generalist", "hr_generalist", "people_operations"),
        ("https://e/154", "Speech Language Pathologist", "speech_language_pathologist", "healthcare_clinical"),
        ("https://e/155", "Fullstack Developer", "software_engineer", "software_engineering"),
        ("https://e/156", "Principal Enterprise Architect", "solutions_architect", "architecture"),
        ("https://e/157", "Budtender PT", "store_associate", "sales"),
        ("https://e/158", "Outside Sales Representative - Roofing", "account_executive", "sales"),
        ("https://e/159", "Licensed Real Estate Agent - Fully Vetted Leads Provided", "account_executive", "sales"),
        ("https://e/160", "DashMart Variable Schedule Team Member", "store_associate", "sales"),
        ("https://e/161", "Sales Operations Analyst", "data_analyst", "data_analytics"),
        ("https://e/162", "Breeze Airways Flight Attendant - Part Time", "flight_attendant", "operations"),
        ("https://e/163", "Director, FP&A", "financial_analyst", "finance"),
        ("https://e/164", "Software Development Manager", "engineering_manager", "software_engineering"),
        ("https://e/165", "Production Engineer", "manufacturing_engineer", "industrial_engineering"),
        ("https://e/166", "FPGA Engineer", "electrical_engineer", "industrial_engineering"),
        ("https://e/167", "IT Administrator", "it_support_specialist", "it_operations"),
        ("https://e/168", "Technical Architect", "solutions_architect", "architecture"),
        ("https://e/169", "Salesforce Administrator", "it_support_specialist", "it_operations"),
        ("https://e/170", "Product Support Specialist", "it_support_specialist", "it_operations"),
        ("https://e/171", "AI Technical Architect", "solutions_architect", "architecture"),
        ("https://e/172", "Engineering Director", "engineering_manager", "software_engineering"),
        ("https://e/173", "Associate IT Specialist", "it_support_specialist", "it_operations"),
        ("https://e/174", "AWS Cloud Administrator", "it_support_specialist", "it_operations"),
        ("https://e/175", "Director, Sales", "sales_manager", "sales"),
    ]
    for url, title, n, f in cases:
        out = clf.classify(url=url, title_clean=title)
        assert out.normalized_title == n
        assert out.role_family == f
        assert out.classification_status == "matched"


def test_ambiguous_title_goes_other() -> None:
    clf = TitleClassifier()
    out = clf.classify(url="https://e/amb", title_clean="Team Lead")
    assert out.normalized_title == "other"
    assert out.role_family == "other"
    assert out.classification_status == "other"


def test_taxonomy_validation_forces_other_on_invalid_mapping() -> None:
    taxonomy = TitleTaxonomy({"software_engineer": "software_engineering", "other": "other"})
    clf = TitleClassifier(taxonomy=taxonomy)
    out = clf.classify(url="https://e/invalid", title_clean="Data Engineer")
    assert isinstance(out, TitleClassification)
    assert out.normalized_title == "other"
    assert "invalid_taxonomy_mapping" in out.notes


def test_finance_specialist_taxonomy_candidates_v12_4() -> None:
    taxonomy = get_default_taxonomy()
    assert taxonomy.role_family_for("quantitative_researcher") == "finance"
    assert taxonomy.role_family_for("credit_analyst") == "finance"
    assert taxonomy.role_family_for("non_role_recruiting_entry") == "non_role"


def test_non_role_recruiting_entry_titles_are_classified_explicitly() -> None:
    clf = TitleClassifier()
    cases = [
        "General Application",
        "Open Application",
        "General Interest: Join Our Talent Community",
        "Future Opportunities: Software Development",
        "Expression of Interest: Machine Learning Engineer",
        "Don't see what you're looking for?",
    ]
    for title in cases:
        out = clf.classify(url="https://e/non-role", title_clean=title)
        assert out.normalized_title == "non_role_recruiting_entry"
        assert out.role_family == "non_role"
        assert out.classification_status == "non_role"
        assert "non_role_recruiting_entry" in out.notes


def test_variants_normalization() -> None:
    assert normalize_variants("Sr Data Engineers") == "senior Data engineer"


def test_location_noise_stripping() -> None:
    assert strip_simple_location_noise("Backend Engineer - Berlin, Germany") == "Backend Engineer"
    assert strip_simple_location_noise("Account Manager | Austin, TX") == "Account Manager"


def test_normalization_preserves_only_high_signal_parenthetical_context() -> None:
    assert normalize_title_for_match("Stylist (Retail) (Part-time)") == "stylist retail"
    assert normalize_title_for_match("Floor Lead (Retail) (Part-time)") == "floor lead retail"
    assert (
        normalize_title_for_match("Field Technician (Mechanic) (Pump, Power & HVAC)")
        == "field technician mechanic pump power hvac"
    )
    assert (
        normalize_title_for_match("Inside Sales Representative (Remote) (EMEA)")
        == "inside sales representative"
    )


def test_top_other_targets_now_covered() -> None:
    clf = TitleClassifier()
    targets = [
        ("Psychiatric Mental Health Nurse Practitioner (PMHNP)", "nurse_practitioner"),
        ("Psychiatrist (MD)", "psychiatrist"),
        ("Psychotherapist", "psychotherapist"),
        ("Future Technicians", "technician"),
        ("Heavy Equipment Field Technician (Mechanic)", "field_technician"),
        ("Heavy Equipment Shop Technician (Mechanic)", "mechanic"),
        ("CDL Drivers", "driver"),
        ("Customer Delivery Driver", "delivery_driver"),
        ("Engineering Manager", "engineering_manager"),
        ("Compliance Manager", "compliance_manager"),
        ("Compliance Specialist", "compliance_specialist"),
        ("Compliance Analyst", "compliance_specialist"),
        ("Affiliate Compliance Manager", "compliance_manager"),
        ("Affiliate Compliance Specialist", "compliance_specialist"),
        ("Compliance Associate", "compliance_specialist"),
        ("Assistant Teacher", "assistant_teacher"),
        ("Substitute Teacher", "substitute_teacher"),
        ("Retail Sales Associate - Part Time", "store_associate"),
        ("Customer Service Delivery Advocate", "customer_service_specialist"),
        ("Senior DevOps Engineer", "devops_engineer"),
        ("Senior Site Reliability Engineer", "site_reliability_engineer"),
        ("Site Reliability Engineer", "site_reliability_engineer"),
        ("Senior Machine Learning Engineer", "ml_engineer"),
        ("Senior Data Scientist", "data_scientist"),
        ("Solutions Architect", "solutions_architect"),
        ("Solutions Engineer", "sales_engineer"),
        ("Technical Support Engineer", "it_support_specialist"),
        ("Executive Assistant", "executive_assistant"),
        ("Senior Product Designer", "product_designer"),
        ("Senior Performance Copywriter, Personal Finance", "marketing_specialist"),
        ("Lead Video Ad Copywriter", "marketing_specialist"),
        ("Lead Video Copywriter", "marketing_specialist"),
        ("Senior Direct Response Copywriter, Personal Finance", "marketing_specialist"),
        ("Senior Manager, Google Paid Media", "marketing_specialist"),
        ("Senior Manager, Video Ad Copywriting", "marketing_specialist"),
        ("Senior Manager, Video Copywriting", "marketing_specialist"),
        ("Senior Personal Finance Copywriter, Performance", "marketing_specialist"),
        ("Sales Engineer", "sales_engineer"),
        ("Senior Sales Engineer", "sales_engineer"),
        ("Senior Security Engineer", "software_engineer"),
        ("Python Engineer", "software_engineer"),
        ("Health Information Specialist I", "health_information_specialist"),
        ("Associate Wealth Advisor", "wealth_advisor"),
        ("Behavior Technician", "behavioral_support_specialist"),
        ("Registered Behavior Technician", "behavioral_support_specialist"),
        ("Intervention Specialist", "behavioral_support_specialist"),
        ("Direct Support Professional (DSP)", "behavioral_support_specialist"),
        ("Sales Associate", "store_associate"),
        ("Lead Store Associate", "store_associate"),
        ("Rental Coordinator", "operations_specialist"),
        ("AI Engineer", "ml_engineer"),
        ("Senior AI Engineer", "ml_engineer"),
        ("Forward Deployed Engineer", "software_engineer"),
        ("Technical Sales and Field Service Engineer", "sales_engineer"),
        ("Accounting Manager", "accountant"),
        ("Business Development Manager", "account_manager"),
        ("Business Development Executive", "account_executive"),
        ("Federal Business Development Executive", "account_executive"),
        ("ISO Business Development Executive (Hybrid)", "account_executive"),
    ]
    for idx, (title, normalized) in enumerate(targets):
        out = clf.classify(url=f"https://example.com/t{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.classification_status == "matched"


def test_copywriter_remains_other_in_this_pass() -> None:
    clf = TitleClassifier()
    out = clf.classify(url="https://example.com/cw", title_clean="Senior Performance Copywriter, Personal Finance")
    assert out.normalized_title == "marketing_specialist"
    assert out.role_family == "marketing"


def test_general_manager_remains_other() -> None:
    clf = TitleClassifier()
    out = clf.classify(url="https://example.com/gm", title_clean="General Manager")
    assert out.normalized_title == "other"


def test_marketing_strategy_manager_remains_other() -> None:
    clf = TitleClassifier()
    out = clf.classify(
        url="https://example.com/market-strategy",
        title_clean="Senior Market Strategy and Partnerships Manager",
    )
    assert out.normalized_title == "other"


def test_precision_cleanup_anti_overmatch_cases_go_other() -> None:
    clf = TitleClassifier()
    ambiguous_titles = [
        "Business Analyst",
        "Quantitative Researcher",
        "Data Science Manager",
        "Senior Firmware Engineer",
    ]
    for idx, title in enumerate(ambiguous_titles):
        out = clf.classify(url=f"https://example.com/amb-{idx}", title_clean=title)
        assert out.normalized_title == "other"
        assert out.role_family == "other"
        assert out.classification_status == "other"


def test_industrial_rules_do_not_overmatch_generic_engineer_titles() -> None:
    clf = TitleClassifier()
    ambiguous_titles = [
        "Senior Firmware Engineer",
        "Software Engineer",
        "Control Systems Engineer",
    ]
    for idx, title in enumerate(ambiguous_titles):
        out = clf.classify(url=f"https://example.com/industrial-amb-{idx}", title_clean=title)
        assert out.normalized_title != "electrical_engineer"
        assert out.normalized_title != "mechanical_engineer"
        assert out.normalized_title != "manufacturing_engineer"
        assert out.normalized_title != "systems_engineer"
        assert out.normalized_title != "network_engineer"


def test_systems_network_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Systems Engineer", "systems_engineer", "it_operations"),
        ("Senior Systems Engineer", "systems_engineer", "it_operations"),
        ("Network Engineer", "network_engineer", "it_operations"),
        ("Senior Network Engineer", "network_engineer", "it_operations"),
    ]
    for idx, (title, normalized, role_family) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/sys-net-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"

    negatives = [
        "Senior Firmware Engineer",
        "Software Engineer",
        "Platform Engineer",
        "Control Systems Engineer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/sys-net-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"systems_engineer", "network_engineer"}


def test_software_development_engineer_variants_precision_v34() -> None:
    clf = TitleClassifier()
    positives = [
        "Software Development Engineer",
        "Senior Software Development Engineer",
        "Staff Software Development Engineer",
        "Principal Software Development Engineer",
        "Software Development Engineer in Test",
        "Senior Software Development Engineer in Test",
        "Software Development Engineer in Test (SDET)",
        "Software Development Engineer III",
        "Senior Software Development Engineer L4",
        "SDET",
        "SDET-Playwright",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/sde-v34-pos-{idx}", title_clean=title)
        assert out.normalized_title == "software_engineer"
        assert out.role_family == "software_engineering"
        assert out.classification_status == "matched"

    negatives = [
        "Development Engineer",
        "Principal Engineer",
        "Senior Firmware Engineer",
        "Systems Engineer",
        "Network Engineer",
        "Manager - Software Development Engineering",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/sde-v34-neg-{idx}", title_clean=title)
        assert out.normalized_title != "software_engineer"


def test_tech_lead_core_product_precision_v38() -> None:
    clf = TitleClassifier()
    positives = [
        "Tech Lead, Android Core Product",
        "Tech Lead, Android Core Product - Berlin, Germany",
        "Tech Lead, Web Core Product & Chrome Extension",
        "Tech Lead, Web Core Product & Chrome Extension - New York, USA",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/techlead-v38-pos-{idx}", title_clean=title)
        assert out.normalized_title == "software_engineer"
        assert out.role_family == "software_engineering"
        assert out.classification_status == "matched"

    negatives = [
        "Team Lead, Android Core Product",
        "Technical Lead, Web Core Product",
        "Lead Engineer, Web Core Product & Chrome Extension",
        "Tech Lead, Data Platform",
        "Tech Lead, Android",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/techlead-v38-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "eng_tech_lead_core_product_v38"


def test_it_support_engineer_specialist_precision_v35() -> None:
    clf = TitleClassifier()
    positives = [
        "IT Support Engineer",
        "Senior IT Support Engineer",
        "Desktop Support Engineer",
        "Linux Desktop Support Engineer",
        "Associate Linux Support Engineer",
        "Network Support Engineer",
        "IT Support Specialist",
        "Senior IT Support Specialist",
        "IT Support Specialist II",
        "IT Support Analyst",
        "Associate IT Support Analyst",
        "IT Support Technician",
        "IT Support Technician II",
        "IT Support Lead",
        "IT Support Team Lead",
        "Executive IT Support",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/it-support-v35-pos-{idx}", title_clean=title)
        assert out.normalized_title == "it_support_specialist"
        assert out.role_family == "it_operations"
        assert out.classification_status == "matched"

    negatives = [
        "Customer Support Engineer",
        "Technical Customer Support Engineer - EMEA",
        "Product Support Engineer",
        "Support Specialist",
        "IT Support Manager",
        "Senior Manager, Technical Services & IT Support",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/it-support-v35-neg-{idx}", title_clean=title)
        assert out.normalized_title != "it_support_specialist"


def test_semantic_cleanup_candidate_patch_precision_v54() -> None:
    clf = TitleClassifier()
    positives = [
        ("Software Development Manager", "engineering_manager", "software_engineering"),
        ("Senior Software Development Manager", "engineering_manager", "software_engineering"),
        ("Production Engineer", "manufacturing_engineer", "industrial_engineering"),
        ("Senior Production Engineer", "manufacturing_engineer", "industrial_engineering"),
        ("FPGA Engineer", "electrical_engineer", "industrial_engineering"),
        ("Senior FPGA Engineer", "electrical_engineer", "industrial_engineering"),
        ("IT Administrator", "it_support_specialist", "it_operations"),
        ("Senior IT Administrator", "it_support_specialist", "it_operations"),
        ("Technical Architect", "solutions_architect", "architecture"),
        ("Senior Technical Architect", "solutions_architect", "architecture"),
    ]
    for idx, (title, normalized, role_family) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/v54-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"

    negatives = [
        "Business Development Manager",
        "Sales Engineer",
        "ML Engineer",
        "School Administrator",
        "Technical Recruiter",
        "Architect",
        "Administrator",
        "Product Engineer",
        "Senior Product Engineer",
        "Data Science Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/v54-neg-{idx}", title_clean=title)
        assert out.matched_rule_id not in {
            "eng_software_development_manager_core_v54",
            "industrial_production_engineer_core_v54",
            "industrial_fpga_engineer_core_v54",
            "it_administrator_core_v54",
            "arch_technical_architect_core_v54",
        }


def test_semantic_assisted_safe_batch_v55_precision() -> None:
    clf = TitleClassifier()
    positives = [
        ("Salesforce Administrator", "it_support_specialist", "it_operations"),
        ("Senior Salesforce Administrator", "it_support_specialist", "it_operations"),
        ("Professional Services Salesforce Administrator", "it_support_specialist", "it_operations"),
        ("Salesforce Administrator II", "it_support_specialist", "it_operations"),
        ("Product Support Specialist", "it_support_specialist", "it_operations"),
        ("Associate Product Support Specialist - EMEA & US hours", "it_support_specialist", "it_operations"),
        ("Senior Product Support Specialist - B2B Saas", "it_support_specialist", "it_operations"),
        ("Product Support Specialist, Weekend Coverage", "it_support_specialist", "it_operations"),
        ("AI Technical Architect", "solutions_architect", "architecture"),
        ("ServiceNow Technical Architect", "solutions_architect", "architecture"),
        ("Salesforce Technical Architect", "solutions_architect", "architecture"),
        ("Professional Services Technical Architect - West", "solutions_architect", "architecture"),
        ("Technical Architect, PS", "solutions_architect", "architecture"),
    ]
    for idx, (title, normalized, role_family) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/v55-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"

    negatives = [
        "Salesforce Engineer",
        "Salesforce Developer",
        "Lease Administrator",
        "School Administrator",
        "Support Specialist",
        "Customer Support Specialist",
        "Product Specialist",
        "Technical Architect Manager",
        "Architect",
        "Enterprise Architect",
        "Technical Recruiter",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/v55-neg-{idx}", title_clean=title)
        assert out.matched_rule_id not in {
            "it_salesforce_administrator_core_v55",
            "it_product_support_specialist_core_v55",
            "arch_technical_architect_contextual_v55",
        }


def test_recoverability_batch_v58_precision() -> None:
    clf = TitleClassifier()
    positives = [
        ("Engineering Director", "engineering_manager", "software_engineering"),
        ("Senior Manager, Software Development", "engineering_manager", "software_engineering"),
        ("Senior Manager, Software Engineering", "engineering_manager", "software_engineering"),
        ("Manager, Software Development (GO)", "engineering_manager", "software_engineering"),
        ("Manager, Software Engineering - Billing", "engineering_manager", "software_engineering"),
        ("Associate IT Specialist", "it_support_specialist", "it_operations"),
        ("RCM Application Support Specialist", "it_support_specialist", "it_operations"),
        ("Windows Platform Support (L1)", "it_support_specialist", "it_operations"),
        ("AWS Cloud Administrator", "it_support_specialist", "it_operations"),
        ("Business Applications Administrator", "it_support_specialist", "it_operations"),
        ("Virtual Platform Administrator", "it_support_specialist", "it_operations"),
        ("Director, Sales", "sales_manager", "sales"),
        ("Director, Enterprise Sales - North America", "sales_manager", "sales"),
        ("Sales Director, Tres", "sales_manager", "sales"),
        ("VP, Sales", "sales_manager", "sales"),
    ]
    for idx, (title, normalized, role_family) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/v58-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"

    negatives = [
        "Manager, Manufacturing Test Engineering (Intelligence Systems)",
        "Regional Director, Enterprise",
        "Director, Enterprise - RCT vertical - New Logos",
        "Technical Customer Engineer (Technical Support & Escalation Engineering)",
        "Information System Specialist II",
        "Senior IT Engineer",
        "Engineering Manager",
        "Sales Director of Operations",
        "Cloud Architect",
        "Product Support Engineer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/v58-neg-{idx}", title_clean=title)
        assert out.matched_rule_id not in {
            "eng_software_manager_variants_v58",
            "it_specialist_and_support_variants_v58",
            "it_admin_variants_v58",
            "sales_director_variants_v58",
        }


def test_recoverability_batch_v60_precision() -> None:
    clf = TitleClassifier()
    positives = [
        ("Senior FP&A Specialist", "financial_analyst", "finance", "finance_fpna_core_v60"),
        ("FP&A Analyst", "financial_analyst", "finance", "finance_fpna_core_v60"),
        ("Field FP&A Manager", "financial_analyst", "finance", "finance_fpna_core_v60"),
        ("Strategic Finance Lead", "financial_analyst", "finance", "finance_strategic_finance_core_v60"),
        ("Head of Strategic Finance", "financial_analyst", "finance", "finance_strategic_finance_core_v60"),
        ("Senior Credit Analyst", "credit_analyst", "finance", "finance_credit_analyst_core_v60"),
        ("Associate Credit Analyst", "credit_analyst", "finance", "finance_credit_analyst_core_v60"),
        ("Senior Thermal Engineer", "mechanical_engineer", "industrial_engineering", "industrial_thermal_engineer_v60"),
        ("Launch Fluids Engineer II", "mechanical_engineer", "industrial_engineering", "industrial_fluids_engineer_v60"),
        ("Physical Design Engineer", "electrical_engineer", "industrial_engineering", "industrial_physical_design_engineer_v60"),
        ("AI Silicon Physical Design Engineer", "electrical_engineer", "industrial_engineering", "industrial_physical_design_engineer_v60"),
    ]
    for idx, (title, normalized, role_family, rule_id) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/v60-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"
        assert out.matched_rule_id == rule_id

    negatives = [
        "Director of Finance",
        "Finance Director",
        "Strategic Finance & Analytics Manager - USA - Remote",
        "Analyst, Customer Support, Strategic Finance",
        "Finance Expert - Private Credit",
        "Private Credit Reporter",
        "Private Credit Lawyer (London)",
        "Senior Firmware Engineer",
        "Control Systems Engineer",
        "Principal Hardware Design Engineer",
        "Hardware Design Engineer, Systems Engineering",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/v60-neg-{idx}", title_clean=title)
        assert out.matched_rule_id not in {
            "finance_fpna_core_v60",
            "finance_strategic_finance_core_v60",
            "finance_credit_analyst_core_v60",
            "industrial_thermal_engineer_v60",
            "industrial_fluids_engineer_v60",
            "industrial_physical_design_engineer_v60",
        }


def test_recoverability_batch_v61_precision() -> None:
    clf = TitleClassifier()
    positives = [
        ("Sr. Technical Writer, API Docs", "technical_writer", "content", "content_technical_writer"),
        ("Technical Writer, Defense Hardware & Systems", "technical_writer", "content", "content_technical_writer"),
        ("Senior Quantitative Researcher - Options Market Making", "quantitative_researcher", "finance", "finance_quantitative_researcher_core_v61"),
        ("Quant Researcher - Systematic Equities", "quantitative_researcher", "finance", "finance_quantitative_researcher_core_v61"),
        ("Quantitative Researcher - Commodities", "quantitative_researcher", "finance", "finance_quantitative_researcher_core_v61"),
        ("Quantitative Researcher, Trading Research", "quantitative_researcher", "finance", "finance_quantitative_researcher_core_v61"),
    ]
    for idx, (title, normalized, role_family, rule_id) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/v61-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"
        assert out.matched_rule_id == rule_id

    negatives = [
        "Writer",
        "Content Writer",
        "Quantitative Researcher",
        "Junior Quantitative Researcher",
        "Quantitative Researcher, Healthcare Innovations",
        "Quantitative Research Associate, Educational Measurement",
        "Quantitative Researcher - Machine Learning",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/v61-neg-{idx}", title_clean=title)
        assert out.matched_rule_id not in {
            "content_technical_writer",
            "finance_quantitative_researcher_core_v61",
        }


def test_customer_service_edge_precision_v37() -> None:
    clf = TitleClassifier()
    positives = [
        "Client Service Associate",
        "Client Services Representative",
        "Senior Client Services Specialist",
        "Associate - Senior Associate - Client Services",
        "Registered Brokerage Client Service Associate - APAC Timezone",
        "Registered Brokerage Client Service Associate - Eastern Timezone",
        "Member Services Coordinator",
        "Client Support Specialist",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/cs-v37-pos-{idx}", title_clean=title)
        assert out.normalized_title == "customer_service_specialist"
        assert out.role_family == "operations"
        assert out.classification_status == "matched"

    negatives = [
        "IT Support Specialist",
        "Support Specialist",
        "Technical Support Specialist - German",
        "Customer Support Engineer",
        "Client Support Engineer",
        "Member Services Manager",
        "Customer Service Coordinator - Vehicle Delivery",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/cs-v37-neg-{idx}", title_clean=title)
        assert out.normalized_title != "customer_service_specialist"


def test_customer_care_advisor_executive_precision_v39() -> None:
    clf = TitleClassifier()
    positives = [
        "Customer Care Executive",
        "Customer Care Executive (English and German)",
        "Customer Care Executive (Spanish, Greek and English)",
        "Customer Care Advisor (Voice)",
        "Customer Care Advisor (Non-voice)",
        "UAE Customer Care Advisor (Voice)",
        "Customer Care Advisor, Boca Raton",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/cs-v39-pos-{idx}", title_clean=title)
        assert out.normalized_title == "customer_service_specialist"
        assert out.role_family == "operations"
        assert out.classification_status == "matched"

    negatives = [
        "Account Executive",
        "Customer Success Executive",
        "Technical Support Engineer",
        "Customer Support Engineer",
        "Senior Customer Care Engineer - Federal TS SCI w - FSP",
        "Manager, Customer Care",
        "Director, Customer Care",
        "VP Customer Care & Contact Center Shared Services",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/cs-v39-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "customer_care_advisor_executive_edge_v39"


def test_ai_trainer_specialist_family_precision_v40() -> None:
    clf = TitleClassifier()
    positives = [
        "German Language Specialist - Freelance AI Trainer Project",
        "Kotlin Coding Specialist - Freelance AI Trainer Project",
        "Audio Editing Specialist - Freelance AI Trainer Project",
        "Garment Manufacturing QC Specialist - Freelance AI Trainer Project",
        "Geospatial Reasoning Specialist (Senior) - Freelance AI Trainer Project",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/ai-trainer-v40-pos-{idx}", title_clean=title)
        assert out.normalized_title == "ai_trainer_specialist"
        assert out.role_family == "operations"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "ops_ai_trainer_specialist_family_v40"

    negatives = [
        "AI Generalist (No Experience Required) - Freelance AI Trainer Project",
        "Customer Support Specialist - Freelance Project",
        "Language Specialist",
        "Coding Specialist (Fluent in German)",
        "Freelance AI Trainer Project Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/ai-trainer-v40-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "ops_ai_trainer_specialist_family_v40"


def test_ai_trainer_non_specialist_family_precision_v41() -> None:
    clf = TitleClassifier()
    positives = [
        "Voice Actor - Freelance AI Trainer Project",
        "Social Media Annotation - Freelance AI Trainer Project",
        "Japanese Translator - Freelance AI Trainer Project",
        "Armenian Language Expert - Freelance AI Trainer Project",
        "AI Generalist (No Experience Required) - Freelance AI Trainer Project",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/ai-trainer-v41-pos-{idx}", title_clean=title)
        assert out.normalized_title == "ai_trainer_generalist"
        assert out.role_family == "operations"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "ops_ai_trainer_non_specialist_family_v41"

    negatives = [
        "Voice Actor",
        "Japanese Translator",
        "AI Generalist (No Experience Required)",
        "German Language Specialist - Freelance AI Trainer Project",
        "Customer Support Agent - Freelance Project",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/ai-trainer-v41-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "ops_ai_trainer_non_specialist_family_v41"


def test_producer_contextual_cluster_precision_v42() -> None:
    clf = TitleClassifier()
    positives = [
        "Morning Executive Producer",
        "Morning Show Producer",
        "Streaming Producer, TEGNA Central Desk",
        "Lead Producer, Live Operations",
        "Commercial Producer",
        "Videographer - Producer",
        "Producer - Editor",
        "Senior Conference Producer",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/producer-v42-pos-{idx}", title_clean=title)
        assert out.normalized_title == "content_producer"
        assert out.role_family == "content"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "content_producer_contextual_edge_v42"

    negatives = [
        "Producer",
        "Freelance Producer",
        "Insurance Producer - Atlanta, GA",
        "P&C Sales Producer",
        "Producer-in-Residence",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/producer-v42-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "content_producer_contextual_edge_v42"


def test_insurance_producer_geo_cluster_precision_v43() -> None:
    clf = TitleClassifier()
    positives = [
        "Insurance Producer - Atlanta, GA",
        "Insurance Producer - Tucson, AZ",
        "Insurance Producer- Alexandria, LA",
        "Insurance Producer -Asheboro, NC",
        "Copy of Insurance Producer -Asheville, NC",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/ins-v43-pos-{idx}", title_clean=title)
        assert out.normalized_title == "account_executive"
        assert out.role_family == "sales"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "sales_insurance_producer_geo_edge_v43"

    negatives = [
        "Producer",
        "Creative Producer",
        "News Producer",
        "Insurance Sales Manager",
        "Insurance Producer Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/ins-v43-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "sales_insurance_producer_geo_edge_v43"


def test_human_resources_business_partner_variants_precision_v44() -> None:
    clf = TitleClassifier()
    positives = [
        "Human Resources Business Partner",
        "Senior Human Resources Business Partner",
        "Human Resource Business Partner, IL",
        "Sr. Human Resources Business Partner",
        "Principal Human Resources Business Partner",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/hrbp-v44-pos-{idx}", title_clean=title)
        assert out.normalized_title == "people_business_partner"
        assert out.role_family == "people_operations"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "people_business_partner"

    negatives = [
        "Finance Business Partner",
        "Commercial Business Partner",
        "People Partner",
        "HR Manager",
        "Business Partner",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/hrbp-v44-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "people_business_partner"


def test_systems_administrator_variants_precision_v45() -> None:
    clf = TitleClassifier()
    positives = [
        "Systems Administrator",
        "System Administrator",
        "Senior Systems Administrator",
        "Lead System Administrator",
        "IT Systems Administrator - Linux",
        "Clinical System Administrator II",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/sysadmin-v45-pos-{idx}", title_clean=title)
        assert out.normalized_title == "it_support_specialist"
        assert out.role_family == "it_operations"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "it_systems_administrator_core_v45"

    negatives = [
        "Database Administrator",
        "Network Administrator",
        "Manager, Salesforce & Systems Administrator",
        "Office Administrator",
        "Project Administrator",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/sysadmin-v45-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "it_systems_administrator_core_v45"


def test_mobile_engineer_android_ios_precision_v46() -> None:
    clf = TitleClassifier()
    positives = [
        "Android Engineer",
        "Senior Android Engineer",
        "iOS Engineer",
        "Senior iOS Engineer",
        "Mobile Engineer",
        "Senior Mobile Engineer (React Native)",
        "Staff Mobile Engineer, iOS",
        "Mobile iOS Engineer",
        "iOS Engineer, Mobile",
        "(1368) Lead iOS Mobile Engineer",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/mobile-v46-pos-{idx}", title_clean=title)
        assert out.normalized_title == "software_engineer"
        assert out.role_family == "software_engineering"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "eng_mobile_engineer_android_ios_v46"

    negatives = [
        "Principal Engineer",
        "Senior Engineer",
        "Senior Firmware Engineer",
        "Network Engineer",
        "Systems Engineer",
        "Mobile Product Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/mobile-v46-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "eng_mobile_engineer_android_ios_v46"


def test_corporate_paralegal_variants_precision_v47() -> None:
    clf = TitleClassifier()
    positives = [
        "Corporate Paralegal",
        "Senior Corporate Paralegal",
        "Paralegal II, Corporate",
        "Corporate Paralegal Chicago",
        "Corporate Governance Paralegals (Remote, Toronto-based)",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/paralegal-v47-pos-{idx}", title_clean=title)
        assert out.normalized_title == "paralegal"
        assert out.role_family == "legal"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "legal_corporate_paralegal_v47"

    negatives = [
        "Paralegal",
        "Litigation Paralegal",
        "Paralegal, US Immigration",
        "Trade Compliance Paralegal",
        "Legal Counsel",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/paralegal-v47-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "legal_corporate_paralegal_v47"


def test_support_engineer_core_safe_v2_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Support Engineer",
        "Senior Support Engineer",
        "L3 Support Engineer",
        "Application Support Engineer",
        "Cloud Support Engineer",
        "Software Support Engineer",
        "Production Support Engineer",
        "Infrastructure Support Engineer",
        "Enterprise Support Engineer",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/support-safe-v2-pos-{idx}", title_clean=title)
        assert out.normalized_title == "it_support_specialist"
        assert out.role_family == "it_operations"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "it_support_engineer_core_safe_v2"

    negatives = [
        "Customer Support Engineer",
        "Product Support Engineer",
        "Support Engineering Manager",
        "Customer Support Manager",
        "Client Support Engineer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/support-safe-v2-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "it_support_engineer_core_safe_v2"


def test_healthcare_therapist_edges_safe_v2_precision() -> None:
    clf = TitleClassifier()
    positives = [
        ("Occupational Therapist", "occupational_therapist"),
        ("Contracted In-Home Occupational Therapist", "occupational_therapist"),
        ("Pediatric Occupational Therapist", "occupational_therapist"),
        ("Respiratory Therapist - Registered", "respiratory_therapist"),
        ("Respiratory Therapist - Registered - Float Pool", "respiratory_therapist"),
    ]
    for idx, (title, expected) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/therapist-safe-v2-pos-{idx}", title_clean=title)
        assert out.normalized_title == expected
        assert out.role_family == "healthcare_clinical"
        assert out.classification_status == "matched"

    negatives = [
        "Physical Therapist",
        "Mental Health Therapist",
        "Clinical Therapist",
        "Occupational Therapy Assistant",
        "Respiratory Therapy Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/therapist-safe-v2-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"occupational_therapist", "respiratory_therapist"}


def test_safe_batch_v3_client_success_manager_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Client Success Manager",
        "Senior Client Success Manager",
        "Enterprise Client Success Manager (Chicago)",
        "Client Success Manager, Array+",
        "Sr. Client Success Manager - Enterprise",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/csm-safe-v3-pos-{idx}", title_clean=title)
        assert out.normalized_title == "customer_success_manager"
        assert out.role_family == "customer_success"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "csm_client_success_manager_core_safe_v3"

    negatives = [
        "Customer Success Engineer",
        "Client Partner",
        "Client Success Director",
        "Success Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/csm-safe-v3-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "csm_client_success_manager_core_safe_v3"


def test_safe_batch_v3_devsecops_engineer_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "DevSecOps Engineer",
        "Senior DevSecOps Engineer",
        "Staff DevSecOps Engineer",
        "DevSecOps Engineer III",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/devsecops-safe-v3-pos-{idx}", title_clean=title)
        assert out.normalized_title == "devops_engineer"
        assert out.role_family == "devops"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "eng_devsecops_engineer_core_safe_v3"

    negatives = [
        "DevSecOps Manager",
        "Security Engineer",
        "Senior DevOps Engineer",
        "Principal Engineer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/devsecops-safe-v3-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "eng_devsecops_engineer_core_safe_v3"


def test_safe_batch_v3_data_architect_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Data Architect",
        "Senior Data Architect",
        "Staff Data Architect",
        "Principal Data Architect",
        "Data Architect - Platform",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/data-arch-safe-v3-pos-{idx}", title_clean=title)
        assert out.normalized_title == "solutions_architect"
        assert out.role_family == "architecture"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "arch_data_architect_core_safe_v3"

    negatives = [
        "Data Architecture Manager",
        "Enterprise Architect",
        "Software Architect",
        "Data Engineer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/data-arch-safe-v3-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "arch_data_architect_core_safe_v3"


def test_safe_batch_v4_insurance_agent_geo_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Insurance Agent",
        "Insurance Agent - Austin, TX",
        "Licensed Insurance Agent - Boston, MA",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/ins-agent-safe-v4-pos-{idx}", title_clean=title)
        assert out.normalized_title == "account_executive"
        assert out.role_family == "sales"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "sales_insurance_agent_geo_core_safe_v4"

    negatives = [
        "Licensed Real Estate Agent - Fully Vetted Leads Provided",
        "Insurance Producer - Atlanta, GA",
        "Insurance Sales Manager",
        "Agent",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/ins-agent-safe-v4-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "sales_insurance_agent_geo_core_safe_v4"


def test_safe_batch_v4_hr_generalist_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "HR Generalist",
        "Senior HR Generalist",
        "Human Resources Generalist",
        "Graduate HR Generalist - APAC",
        "People Operations Partner - HR Generalist",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/hr-generalist-safe-v4-pos-{idx}", title_clean=title)
        assert out.normalized_title == "hr_generalist"
        assert out.role_family == "people_operations"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "people_hr_generalist_core_safe_v4"

    negatives = [
        "Human Resources Business Partner",
        "HR Manager",
        "Generalist",
        "Office Manager & HR Admin",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/hr-generalist-safe-v4-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "people_hr_generalist_core_safe_v4"


def test_safe_batch_v4_speech_language_pathologist_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Speech Language Pathologist",
        "Virtual Speech Language Pathologist",
        "Pediatric Speech Language Pathologist",
        "Speech Language Pathologist, Clinical Fellow",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/slp-safe-v4-pos-{idx}", title_clean=title)
        assert out.normalized_title == "speech_language_pathologist"
        assert out.role_family == "healthcare_clinical"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "health_speech_language_pathologist_core_safe_v4"

    negatives = [
        "Speech Therapist",
        "Language Specialist",
        "Speech Writer",
        "Occupational Therapist",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/slp-safe-v4-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "health_speech_language_pathologist_core_safe_v4"


def test_safe_batch_v5_fullstack_developer_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Fullstack Developer",
        "Senior Fullstack Developer",
        ".Net Fullstack Developer",
        "Lead Fullstack Developer- Java",
        "Full Stack Developer",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/fullstack-safe-v5-pos-{idx}", title_clean=title)
        assert out.normalized_title == "software_engineer"
        assert out.role_family == "software_engineering"
        assert out.classification_status == "matched"

    out_new_rule = clf.classify(url="https://example.com/fullstack-safe-v5-new-rule", title_clean="Fullstack Developer")
    assert out_new_rule.matched_rule_id == "eng_fullstack_developer_core_safe_v5"

    negatives = [
        "Fullstack Engineer",
        "Frontend Developer",
        "Software Developer",
        "Developer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/fullstack-safe-v5-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "eng_fullstack_developer_core_safe_v5"


def test_safe_batch_v5_enterprise_architect_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Enterprise Architect",
        "Principal Enterprise Architect",
        "Senior Enterprise Architect",
        "Salesforce Enterprise Architect",
        "IT Enterprise Architect",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/ent-arch-safe-v5-pos-{idx}", title_clean=title)
        assert out.normalized_title == "solutions_architect"
        assert out.role_family == "architecture"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "arch_enterprise_architect_core_safe_v5"

    negatives = [
        "Enterprise Architecture Manager",
        "Architect",
        "Software Architect",
        "Data Architect",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/ent-arch-safe-v5-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "arch_enterprise_architect_core_safe_v5"


def test_safe_batch_v5_budtender_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Budtender",
        "Budtender PT",
        "Budtender Part Time",
        "Retail Associate - Budtender",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/budtender-safe-v5-pos-{idx}", title_clean=title)
        assert out.normalized_title == "store_associate"
        assert out.role_family == "sales"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "retail_budtender_core_safe_v5"

    negatives = [
        "Retail Associate",
        "Bartender",
        "Dispensary Manager",
        "Cannabis Associate",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/budtender-safe-v5-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "retail_budtender_core_safe_v5"


def test_safe_batch_v6_outside_sales_representative_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Outside Sales Representative",
        "Outside Sales Representative - Roofing",
        "Outside Sales Representative, Multi-Media",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/outside-sales-safe-v6-pos-{idx}", title_clean=title)
        assert out.normalized_title == "account_executive"
        assert out.role_family == "sales"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "sales_outside_sales_representative_safe_v6"

    negatives = [
        "Inside Sales Representative",
        "Sales Representative",
        "Outside Account Executive",
        "Outside Sales Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/outside-sales-safe-v6-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "sales_outside_sales_representative_safe_v6"


def test_safe_batch_v6_real_estate_agent_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Licensed Real Estate Agent",
        "Licensed Real Estate Agent - Fully Vetted Leads Provided",
        "Contract Real Estate Agent",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/re-agent-safe-v6-pos-{idx}", title_clean=title)
        assert out.normalized_title == "account_executive"
        assert out.role_family == "sales"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "sales_real_estate_agent_core_safe_v6"

    negatives = [
        "Insurance Agent",
        "Real Estate Associate",
        "Real Estate Manager",
        "Agent",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/re-agent-safe-v6-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "sales_real_estate_agent_core_safe_v6"


def test_safe_batch_v6_dashmart_team_member_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "DashMart Variable Schedule Team Member",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/dashmart-safe-v6-pos-{idx}", title_clean=title)
        assert out.normalized_title == "store_associate"
        assert out.role_family == "sales"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "retail_dashmart_team_member_safe_v6"

    negatives = [
        "DashMart Team Lead",
        "Team Member",
        "Variable Schedule Team Member",
        "DashMart Operations Associate",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/dashmart-safe-v6-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "retail_dashmart_team_member_safe_v6"


def test_safe_batch_v7_sales_operations_analyst_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Sales Operations Analyst",
        "Senior Sales Operations Analyst",
        "Enterprise Sales Operations Analyst",
        "APJ Senior Sales Operations Analyst",
        "Sales Operations Analyst - Renewals",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/sales-ops-safe-v7-pos-{idx}", title_clean=title)
        assert out.normalized_title == "data_analyst"
        assert out.role_family == "data_analytics"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "data_sales_operations_analyst_safe_v7"

    negatives = [
        "Business Operations Analyst",
        "Sales Analyst",
        "Operations Analyst",
        "Sales Operations Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/sales-ops-safe-v7-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "data_sales_operations_analyst_safe_v7"


def test_safe_batch_v7_flight_attendant_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Breeze Airways Flight Attendant - Part Time",
        "Breeze Airways Flight Attendant - Full Time",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/flight-safe-v7-pos-{idx}", title_clean=title)
        assert out.normalized_title == "flight_attendant"
        assert out.role_family == "operations"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "ops_flight_attendant_breeze_safe_v7"

    negatives = [
        "Flight Attendant",
        "Senior Flight Attendant",
        "Cabin Crew",
        "Breeze Airways Pilot - Part Time",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/flight-safe-v7-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "ops_flight_attendant_breeze_safe_v7"


def test_safe_batch_v7_director_fpna_precision() -> None:
    clf = TitleClassifier()
    positives = [
        "Director, FP&A",
        "Senior Director, FP&A - Clinical Strategy and Operations",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/fpna-safe-v7-pos-{idx}", title_clean=title)
        assert out.normalized_title == "financial_analyst"
        assert out.role_family == "finance"
        assert out.classification_status == "matched"
        assert out.matched_rule_id == "finance_director_fpna_safe_v7"

    negatives = [
        "FP&A Manager",
        "Director of Finance",
        "Finance Director",
        "Director, Sales",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/fpna-safe-v7-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "finance_director_fpna_safe_v7"


def test_healthcare_support_rules_do_not_overmatch_broad_titles() -> None:
    clf = TitleClassifier()
    ambiguous_titles = [
        "Occupational Therapist",
        "Physical Therapist",
        "Licensed Marriage and Family Therapist",
        "Medical Assistant Instructor",
        "Assistant Store Manager",
        "Nurse Manager",
        "Business Analyst",
        "Personal Care Specialist (Part Time)",
    ]
    for idx, title in enumerate(ambiguous_titles):
        out = clf.classify(url=f"https://example.com/health-amb-{idx}", title_clean=title)
        assert out.normalized_title not in {
            "licensed_practical_nurse",
            "medical_assistant",
            "registered_nurse",
        }


def test_education_childcare_rules_do_not_overmatch_generic_teacher_trainer_titles() -> None:
    clf = TitleClassifier()
    ambiguous_titles = [
        "Technical Trainer",
        "Sr. Instructor",
        "A&P Mechanic Instructor",
        "Lead Trainer",
    ]
    for idx, title in enumerate(ambiguous_titles):
        out = clf.classify(url=f"https://example.com/edu-amb-{idx}", title_clean=title)
        assert out.normalized_title not in {"teacher", "assistant_teacher"}


def test_education_grade_teacher_and_instructional_aide_precision() -> None:
    clf = TitleClassifier()
    positives = [
        ("K-5th Grade Teacher - SY 26-27", "teacher"),
        ("6-8th Grade Teacher - SY 26-27", "teacher"),
        ("9-12th Grade Teacher - SY 26-27", "teacher"),
        ("Virtual Special Education Teacher", "teacher"),
        ("Title I Teacher", "teacher"),
        ("Instructional Aide", "assistant_teacher"),
        ("1:1 Instructional Aide", "assistant_teacher"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/edu-v18-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "education"
        assert out.classification_status == "matched"

    negatives = [
        "Technical Instructor",
        "A&P Mechanic Instructor",
        "Medical Assistant Instructor",
        "Customer Education and Certification Lead",
        "Licensed Mental Health Counselor - Remote",
        "Counselor",
        "Director of Revenue (Education - Learnerships - Admissions)",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/edu-v18-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"teacher", "assistant_teacher", "school_counselor", "school_administrator"}


def test_retail_service_rules_do_not_overmatch_generic_stylist_lead_manager_titles() -> None:
    clf = TitleClassifier()
    ambiguous_titles = [
        "Stylist",
        "Floor Lead",
        "Program Manager",
        "Customer Success Manager",
        "Technical Service Operations Associate",
    ]
    for idx, title in enumerate(ambiguous_titles):
        out = clf.classify(url=f"https://example.com/retail-amb-{idx}", title_clean=title)
        assert out.normalized_title not in {"store_associate", "operations_specialist"}


def test_industrial_tail_specific_rules_do_not_overmatch_generic_titles() -> None:
    clf = TitleClassifier()
    ambiguous_titles = [
        "Field Technician",
        "Shop Technician",
        "Mechanic",
        "Parts Associate",
        "Automotive Specialist",
    ]
    for idx, title in enumerate(ambiguous_titles):
        out = clf.classify(url=f"https://example.com/ind-tail-amb-{idx}", title_clean=title)
        assert out.matched_rule_id not in {
            "trades_pump_power_hvac_field_technician",
            "trades_pump_power_hvac_shop_technician",
            "trades_automotive_parts_associate",
        }


def test_business_sales_support_precision_guardrails() -> None:
    clf = TitleClassifier()
    negatives = [
        "Business Analyst",
        "Quantitative Researcher",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/biz-guard-{idx}", title_clean=title)
        assert out.normalized_title == "other"


def test_writer_editor_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Technical Writer", "technical_writer", "content"),
        ("Senior Technical Writer", "technical_writer", "content"),
        ("Story Desk Editor", "story_editor", "content"),
    ]
    for idx, (title, normalized, role_family) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/we-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"

    negatives = [
        "Writer",
        "Content Writer",
        "Editor",
        "Managing Editor",
        "Associate Editor",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/we-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"technical_writer", "story_editor"}


def test_design_creative_precision_v21_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Multiskilled Journalist", "journalist", "content"),
        ("Multi-Skilled Journalist", "journalist", "content"),
        ("UX Researcher", "ux_researcher", "design"),
        ("Sr. UX Researcher - ArcGIS Apps", "ux_researcher", "design"),
        ("Staff UX Researcher", "ux_researcher", "design"),
        ("Art Director", "art_director", "design"),
        ("Senior Art Director", "art_director", "design"),
        ("Creative Director", "creative_director", "design"),
        ("Executive Creative Director", "creative_director", "design"),
        ("Creative Director, Art", "creative_director", "design"),
        ("Video Editor", "story_editor", "content"),
        ("Senior Video Editor", "story_editor", "content"),
        ("Videographer and Video Editor", "story_editor", "content"),
    ]
    for idx, (title, normalized, role_family) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/design-v21-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"

    negatives = [
        "Producer",
        "Insurance Producer - Tucson, AZ",
        "Editor",
        "Managing Editor",
        "Data Science Editor",
        "Designer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/design-v21-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"journalist", "ux_researcher", "art_director", "creative_director"}


def test_producer_context_precision_v26_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Creative Producer", "content_producer", "content"),
        ("News Producer", "content_producer", "content"),
        ("Newscast Producer", "content_producer", "content"),
        ("Video Producer, Product Launches", "content_producer", "content"),
        ("Editing AI Content Producer", "content_producer", "content"),
        ("Digital Producer (Manila)", "content_producer", "content"),
        ("Executive Producer", "content_producer", "content"),
        ("Senior Producer - 6 month FTC", "content_producer", "content"),
        ("Brand Partnerships Event Producer", "content_producer", "content"),
        ("Social Video Producer", "content_producer", "content"),
    ]
    for idx, (title, normalized, role_family) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/prod-v26-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"

    negatives = [
        "Producer",
        "Insurance Producer - Tucson, AZ",
        "Copy of Insurance Producer -Asheville, NC",
        "Producer Manager",
        "Senior Producer Relations Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/prod-v26-neg-{idx}", title_clean=title)
        assert out.normalized_title != "content_producer"


def test_specialist_ambiguity_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Technical Support Specialist", "it_support_specialist", "it_operations"),
        ("Senior Technical Support Specialist", "it_support_specialist", "it_operations"),
        ("Solution Specialist", "sales_engineer", "sales"),
    ]
    for idx, (title, normalized, role_family) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/spec-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == role_family
        assert out.classification_status == "matched"

    negatives = [
        "Support Specialist",
        "Technical Specialist",
        "Solution Architect",
        "Solutions Consultant",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/spec-neg-{idx}", title_clean=title)
        if title == "Solution Architect":
            assert out.normalized_title == "solutions_architect"
            continue
        if title == "Solutions Consultant":
            assert out.normalized_title == "sales_engineer"
            continue
        assert out.normalized_title not in {"it_support_specialist", "sales_engineer"}


def test_skilled_trades_expansion_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Auto Body Repair Technician", "mechanic"),
        ("Paintless Dent Repair Technician", "mechanic"),
        ("Automotive Wheel Repair Technician", "mechanic"),
        ("HVAC Technician", "technician"),
        ("Commercial HVAC Service Technician", "technician"),
        ("Diesel Technician", "mechanic"),
        ("Telematics Installer", "technician"),
        ("Lead Plumber", "field_technician"),
        ("Mechanical Technician", "technician"),
        ("Electrical Technician", "technician"),
        ("Tool Technician", "technician"),
        ("Field Service Technician", "technician"),
        ("Facilities Technician", "technician"),
        ("Manufacturing Technician", "technician"),
        ("Cultivation Technician", "technician"),
        ("Assembly Technician (Contract)", "technician"),
        ("Fire Systems Technician", "technician"),
        ("Auto Airbrush Technician", "technician"),
        ("Experienced Heavy Body Technician - $6, 000 Bonus", "technician"),
        ("Master Service Technician - $5, 000 Bonus", "technician"),
        ("Mid-Level Auto Interior Repair - Glass Repair Technician - $4, 000 Bonus", "mechanic"),
        ("Paintless Dent Repair Tech - $4, 000 Bonus", "mechanic"),
        ("PDR Technician - $6, 000 Bonus", "mechanic"),
        ("Automotive Wheel - Rim Repair Technician", "mechanic"),
        ("Rim Repair Tech", "mechanic"),
        ("Stellantis Certified Technician - $5, 000 Bonus", "mechanic"),
        ("Contract Field Service Technician", "technician"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/trades-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "skilled_trades"

    negatives = [
        "Lab Technician",
        "Engineering Technician",
        "Support Specialist",
        "A&P Mechanic Instructor",
        "General Manager (Pump, Power & HVAC)",
        "Field Service Engineer",
        "IT Services Technician",
        "Data Center Engineer",
        "Insurance Producer - Tucson, AZ",
        "Technical Delivery Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/trades-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"mechanic", "field_technician", "technician"}


def test_design_creative_expansion_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        "Content Designer II",
        "Lead Visual Designer",
        "Lead Web Designer",
        "UX Designer - Design systems",
        "UI - UX Designer",
        "Senior UX Designer",
        "Graphic Designer",
        "Motion Designer",
        "Director, Product Design",
        "Product Design Manager",
    ]
    for idx, title in enumerate(positives):
        out = clf.classify(url=f"https://example.com/design-pos-{idx}", title_clean=title)
        assert out.normalized_title == "product_designer"
        assert out.role_family == "design"

    negatives = [
        "Designer",
        "Design Engineer",
        "Principal Digital Design Engineer",
        "Civil Design Manager - Site Design",
        "Producer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/design-neg-{idx}", title_clean=title)
        assert out.normalized_title != "product_designer"


def test_healthcare_clinical_expansion_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Licensed Vocational Nurse (LVN)", "licensed_practical_nurse"),
        ("Staff Nurse", "registered_nurse"),
        ("Staff Nurse - Cardiac Surgery - Days", "registered_nurse"),
        ("Licensed Clinical Social Worker", "psychotherapist"),
        ("Licensed Clinical Social Worker (LCSW) - Remote", "psychotherapist"),
        ("Mental Health Therapist", "psychotherapist"),
        ("Clinical Therapist", "psychotherapist"),
        ("Behavior Analyst (BCBA)", "behavioral_support_specialist"),
        ("Float Pool Certified Nursing Assistant (CNA)", "certified_nursing_assistant"),
        ("Specialty Pharmacy Technician", "pharmacy_technician"),
        ("Lead Pharmacy Technician", "pharmacy_technician"),
        ("Patient Care Technician - HVU - FT - D - N", "patient_care_technician"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/hc-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "healthcare_clinical"

    negatives = [
        "Business Analyst",
        "Data Science Manager",
        "Customer Care Specialist",
        "Clinical Solutions Engineer",
        "Health Information Operations Supervisor",
        "IT Services Technician",
        "Engineering Technician",
        "Medical Director",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/hc-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {
            "registered_nurse",
            "licensed_practical_nurse",
            "psychotherapist",
            "behavioral_support_specialist",
            "certified_nursing_assistant",
            "pharmacy_technician",
            "patient_care_technician",
        }


def test_compliance_risk_expansion_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Third Party Risk Analyst", "compliance_specialist"),
        ("Risk Analyst I", "compliance_specialist"),
        ("Fraud Analyst", "compliance_specialist"),
        ("AML Analyst", "compliance_specialist"),
        ("KYC Onboarding Analyst", "compliance_specialist"),
        ("Fraud Investigator", "compliance_specialist"),
        ("Internal Audit Manager", "compliance_manager"),
        ("Director, Internal Audit", "compliance_manager"),
        ("Compliance Officer", "compliance_manager"),
        ("Operational Risk Manager", "compliance_manager"),
        ("Payroll Incident & Risk Lead", "compliance_specialist"),
        ("Payroll Risk & Compliance Expert - Middle East", "compliance_specialist"),
        ("Associate, Risk - Compliance", "compliance_specialist"),
        ("Manager, Global Product Compliance", "compliance_manager"),
        ("Senior Director, Product Compliance", "compliance_manager"),
        ("Director, Corporate and Regulatory Compliance", "compliance_manager"),
        ("Senior Staff Analyst, GRC", "compliance_specialist"),
        ("Senior GRC Lead", "compliance_specialist"),
        ("Manager, Regulatory Affairs", "compliance_manager"),
        ("Senior Director, Regulatory Affairs", "compliance_manager"),
        ("Regulatory Licensing and Affairs Team Lead - North America", "compliance_manager"),
        ("Regulatory Affairs Analyst", "compliance_specialist"),
        ("Senior Analyst, Regulatory Affairs", "compliance_specialist"),
        ("Affiliate Services Licensing Specialist, Regulatory Affairs (NORAM)", "compliance_specialist"),
        ("Senior Manager, Internal Audit", "compliance_manager"),
        ("Director of Internal Audit", "compliance_manager"),
        ("VP, Internal Audit and Controls", "compliance_manager"),
        ("Internal Audit Lead - Treasury, Finance & Operations", "compliance_manager"),
        ("Director, KYC and Compliance Onboarding", "compliance_specialist"),
        ("Specialist, Onboarding Compliance", "compliance_specialist"),
        ("Risk Strategist, Onboarding and Compliance", "compliance_specialist"),
        ("Senior Analyst, UM Regulatory Operations", "compliance_specialist"),
        ("Senior Analyst, Regulatory Operations", "compliance_specialist"),
        ("Director, Regulatory Operations", "compliance_specialist"),
        ("Regulatory Operations Lead, APAC", "compliance_specialist"),
        ("Associate Director, Regulatory Operations and Intelligence", "compliance_specialist"),
        ("VP, Regulatory Affairs, Strategy, Labeling and Operations", "compliance_specialist"),
        ("AML Onboarding Analyst", "compliance_specialist"),
        ("Client Onboarding & KYC Specialist", "compliance_specialist"),
        ("CDD Onboarding Analyst", "compliance_specialist"),
        ("Team lead - CDD Risk, Customer Onboarding", "compliance_specialist"),
        ("Associate, Operational Controls", "compliance_specialist"),
        ("Manager, Compliance Execution & Enablement", "compliance_specialist"),
        ("Contract Compliance Coordinator", "compliance_specialist"),
        ("Senior Analyst, Government Compliance", "compliance_specialist"),
        ("Product Lead - Compliance", "compliance_specialist"),
        ("Sr. Team Manager, Compliance", "compliance_manager"),
        ("Vice President, Compliance", "compliance_manager"),
        ("International Trade Compliance Leader - APAC", "compliance_manager"),
        ("Information Security GRC Specialist", "compliance_specialist"),
        ("Security Analyst - GRC", "compliance_specialist"),
        ("Senior Security Analyst - GRC", "compliance_specialist"),
        ("Cloud Security GRC Consultant", "compliance_specialist"),
        ("Technical GRC Expert", "compliance_specialist"),
        ("Risk and Compliance Professional", "compliance_specialist"),
        ("AML Governance Analyst", "compliance_specialist"),
        ("Manager, Governance, Risk & Compliance (GRC)", "compliance_manager"),
        ("Director of Governance, Risk, and Compliance (GRC)", "compliance_manager"),
        ("Director of Governance, Risk, Compliance & Trust", "compliance_manager"),
        ("GRC Director", "compliance_manager"),
        ("GRC Lead", "compliance_manager"),
        ("GRC InfoSec Manager", "compliance_manager"),
        ("Senior Security GRC Manager", "compliance_manager"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/cr-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "compliance_risk"

    negatives = [
        "Business Analyst",
        "Data Analyst",
        "Operations Specialist",
        "Controls Engineer",
        "Control Systems Engineer - Site Services",
        "Manager, Software Engineering (Fraud)",
        "Staff Engineer, Risk Insights",
        "Regulatory Affairs Scientist",
        "Internal Audit Data Science Engineer",
        "GRC Engineer",
        "Customer Onboarding Manager",
        "Onboarding Specialist",
        "SaaS Onboarding Specialist",
        "Regulatory Manager - Senior Regulatory Manager - Clinical Trials",
        "Cloud Operations Support Engineer, Compliance",
        "Senior Controls Engineer",
        "Controls Engineer",
        "Control Systems Engineer - Site Services",
        "Controls & Automation Engineer",
        "Automation & Controls Engineer",
        "Staff Controls Engineer",
        "GRC Engineer",
        "Security GRC Engineer",
        "Director, GRC, Engineering (Remote Eligible)",
        "Senior AI & Data Governance Engineer-II",
        "Lead Data Governance Engineer",
        "Identity Governance Engineer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/cr-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"compliance_specialist", "compliance_manager"}


def test_logistics_expansion_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Logistics Coordinator", "logistics_coordinator"),
        ("Logistics Specialist", "logistics_coordinator"),
        ("Dispatcher", "logistics_coordinator"),
        ("Warehouse Associate", "warehouse_associate"),
        ("Inventory Specialist", "warehouse_associate"),
        ("Material Handler", "warehouse_associate"),
        ("Supply Chain Specialist", "supply_chain_specialist"),
        ("Global Supply Chain Manager", "supply_chain_specialist"),
        ("Global Logistics Manager", "logistics_manager"),
        ("Manager, Delivery Services", "logistics_manager"),
        ("Director, Delivery", "logistics_manager"),
        ("Manager, Delivery Excellence", "logistics_manager"),
        ("Delivery Excellence Manager- East", "logistics_manager"),
        ("Fulfillment Associate", "logistics_coordinator"),
        ("Retail Delivery Associate", "logistics_coordinator"),
        ("Customer Vehicle Delivery Team", "logistics_coordinator"),
        ("Specialty Pharmacy - Delivery Clerk", "logistics_coordinator"),
        ("Area Manager, Fulfillment Operations", "logistics_manager"),
        ("Fleet Operator", "logistics_coordinator"),
        ("Autonomous Fleet Specialist", "logistics_coordinator"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/log-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "logistics"

    negatives = [
        "Technical Delivery Manager",
        "Service Delivery Manager",
        "Delivery Lead",
        "Customer Success Manager",
        "Project Delivery Lead, Battlespace",
        "Staff Cloud Architect (Delivery) - EMEA",
        "Lead Engineer - Product Delivery (all genders)",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/log-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {
            "logistics_coordinator",
            "warehouse_associate",
            "supply_chain_specialist",
            "logistics_manager",
        }


def test_customer_service_member_services_expansion_precision_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Bilingual Member Services Representative (Remote, Spanish Speaking)", "customer_service_specialist"),
        ("Member Services Representative (Temporary) (Bilingual Spanish)", "customer_service_specialist"),
        ("Sr. Member Services Advocate (Remote)", "customer_service_specialist"),
        ("Customer Service Advisor", "customer_service_specialist"),
        ("Customer Service, Associate", "customer_service_specialist"),
        ("Client Service Representative", "customer_service_specialist"),
        ("Customer Support Agent - Freelance Project", "customer_service_specialist"),
        ("Customer Support Associate, Bilingual - Greek (Starlink)", "customer_service_specialist"),
        ("Customer Support Advocate (French Speaking)", "customer_service_specialist"),
        ("Call Center Representative (Appointment Setter)", "customer_service_specialist"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/cs-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "operations"

    negatives = [
        "Senior Customer Support Engineer",
        "Technical Customer Support Engineer - EMEA",
        "Customer Support Manager",
        "Director, Customer Support",
        "Sales Representative",
        "Technical Support Representative",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/cs-neg-{idx}", title_clean=title)
        assert out.normalized_title != "customer_service_specialist"


def test_skilled_trades_auto_body_precision_v27_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Auto Body Inspector", "mechanic"),
        ("Autobody Inspector", "mechanic"),
        ("Auto Body Painter - $4, 000 Bonus", "mechanic"),
        ("Auto Body Estimator", "mechanic"),
        ("Auto Body Prep Technician", "mechanic"),
        ("Autobody Prepper - 2nd Shift", "mechanic"),
        ("Auto Body Apprentice", "mechanic"),
        ("Auto Interior Repair Tech - $4, 000 Bonus", "mechanic"),
        ("Automotive Rim Repair", "mechanic"),
        ("Auto Rim Repair", "mechanic"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/st-v27-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "skilled_trades"

    negatives = [
        "IT Services Technician",
        "Engineering Technician",
        "Robotics Field Service Engineer",
        "Data Center Technician",
        "Field Service Engineer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/st-v27-neg-{idx}", title_clean=title)
        assert out.normalized_title != "mechanic"


def test_skilled_trades_hvac_plumbing_edge_v28_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("HVAC Lead Installer (Relocation Offered!!!)", "technician"),
        ("HVAC Lead Installer", "technician"),
        ("HVAC Install Technician", "technician"),
        ("Commercial HVAC Installer", "technician"),
        ("HVAC Apprentice", "technician"),
        ("Plumbing Install Lead", "field_technician"),
        ("Plumbing Install Technician", "field_technician"),
        ("Plumbing Service Technician", "field_technician"),
        ("Plumbing Apprentice", "field_technician"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/st-v28-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "skilled_trades"

    negatives = [
        "General Manager (Pump, Power & HVAC)",
        "Data Center Engineer (HVAC)",
        "Plumbing & Fire Protection Engineer II",
        "IT Network and Low Voltage Installer",
        "Onsite POS Installer, Sr Associate",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/st-v28-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"technician", "field_technician"}


def test_design_creative_editorial_precision_v30_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Content Editor", "story_editor"),
        ("Data Science Editor", "story_editor"),
        ("Copy Editor", "story_editor"),
        ("Technical Content Editor", "story_editor"),
        ("Video Content Editor", "story_editor"),
        ("Executive Editor (based in Madrid)", "story_editor"),
        ("Associate Managing Editor - Healthcare Agency", "story_editor"),
        ("Managing Editor, Health Payer Specialist", "story_editor"),
        ("Senior Editor, Editorial Review", "story_editor"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/dc-v30-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "content"

    negatives = [
        "Manager, Editorial (Part-Time)",
        "Director, Editorial Monetization",
        "Engineering Editorial Lead",
        "Media Manager",
        "Senior Media Manager",
        "Creative Strategist",
        "Designer",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/dc-v30-neg-{idx}", title_clean=title)
        assert out.normalized_title != "story_editor"


def test_skilled_trades_tool_trailer_and_state_inspector_edge_v31_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Tool Trailer Technician", "technician"),
        ("Automotive State Inspector", "mechanic"),
        ("Automotive State Inspector (2nd Shift)", "mechanic"),
        ("Automotive Technician - State Inspector", "mechanic"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/st-v31-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "skilled_trades"

    negatives = [
        "Tool Trailer - Inside Sales",
        "IT Services Technician",
        "Data Center Technician",
        "Fleet Support Engineer",
        "Engineering Technician",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/st-v31-neg-{idx}", title_clean=title)
        assert out.normalized_title not in {"mechanic", "technician"}


def test_design_creative_media_planning_precision_v32_guardrails() -> None:
    clf = TitleClassifier()
    positives = [
        ("Media Manager", "marketing_specialist"),
        ("Senior Media Manager, (Healthcare)", "marketing_specialist"),
        ("Media Planner", "marketing_specialist"),
        ("Senior Media Planner", "marketing_specialist"),
        ("Programmatic Media Supervisor", "marketing_specialist"),
        ("Programmatic Media Strategist", "marketing_specialist"),
        ("Programmatic Media Manager", "marketing_specialist"),
        ("Assistant Media Planner", "marketing_specialist"),
        ("Integrated Media Planner", "marketing_specialist"),
        ("Offline Media Manager", "marketing_specialist"),
        ("Media Associate", "marketing_specialist"),
    ]
    for idx, (title, normalized) in enumerate(positives):
        out = clf.classify(url=f"https://example.com/dc-v32-pos-{idx}", title_clean=title)
        assert out.normalized_title == normalized
        assert out.role_family == "marketing"

    negatives = [
        "Director, Media",
        "Brand Partnerships Manager",
        "Creative Strategist",
        "Media Manager, Content Operations",
        "Senior Market Strategy and Partnerships Manager",
    ]
    for idx, title in enumerate(negatives):
        out = clf.classify(url=f"https://example.com/dc-v32-neg-{idx}", title_clean=title)
        assert out.matched_rule_id != "marketing_media_planning_edge_v32"


def test_run_title_stage_outputs_report_and_file(tmp_path: Path) -> None:
    cleaned = tmp_path / "jobs_cleaned_en.jsonl"
    rows = [
        {
            "url": "https://example.com/1",
            "title_clean": "Software Engineer",
            "description_clean": "Build APIs.",
            "location_clean": "Remote",
        },
        {
            "url": "https://example.com/2",
            "title_clean": "Unclear Role",
            "description_clean": "Something generic.",
            "location_clean": "",
        },
    ]
    with cleaned.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    out = tmp_path / "jobs_titled_en.jsonl"
    docs = tmp_path / "docs"
    report = run_title_stage(
        input_cleaned_path=cleaned,
        output_path=out,
        report_dir=docs,
    )
    assert report["rows_total"] == 2
    assert out.exists()
    assert (docs / "title_stage_step12.json").exists()
    assert (docs / "title_stage_step12.md").exists()


def test_run_title_stage_applies_partner_lane_context_rule(tmp_path: Path) -> None:
    cleaned = tmp_path / "jobs_cleaned_en.jsonl"
    extracted = tmp_path / "jobs_extracted_en.jsonl"
    output = tmp_path / "jobs_titled_en.jsonl"
    docs = tmp_path / "docs"

    cleaned.write_text(
        json.dumps(
            {
                "url": "https://e/partner-1",
                "title_clean": "Partner Growth Manager",
                "description_clean": "",
                "responsibilities_clean": "",
                "requirements_clean": "",
                "departments_raw": [],
                "location_clean": "",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    extracted.write_text(
        json.dumps(
            {
                "url": "https://e/partner-1",
                "title_clean": "Partner Growth Manager",
                "description_clean": "Own go-to-market plans, partner relationships, and revenue growth across strategic partnerships.",
                "responsibilities_clean": "Drive pipeline, bookings, and portfolio growth with named partners.",
                "requirements_clean": "",
                "departments_raw": [{"name": "Partner Development"}],
                "skills": [],
                "tags": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    report = run_title_stage(
        input_cleaned_path=cleaned,
        input_extracted_path=extracted,
        output_path=output,
        report_dir=docs,
    )
    row = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert row["normalized_title"] == "account_manager"
    assert row["role_family"] == "sales"
    assert row["classification_status"] == "matched"
    assert row["matched_rule_id"] == "ctx_partner_lane_v1"
    assert "context_rule_match" in row["notes"]
    assert report["counts_by_status"]["matched"] == 1


def test_run_title_stage_keeps_blocked_partner_lane_titles_as_other(tmp_path: Path) -> None:
    cleaned = tmp_path / "jobs_cleaned_en.jsonl"
    extracted = tmp_path / "jobs_extracted_en.jsonl"
    output = tmp_path / "jobs_titled_en.jsonl"

    cleaned.write_text(
        json.dumps(
            {
                "url": "https://e/partner-2",
                "title_clean": "Partner Director",
                "description_clean": "",
                "responsibilities_clean": "",
                "requirements_clean": "",
                "departments_raw": [],
                "location_clean": "",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    extracted.write_text(
        json.dumps(
            {
                "url": "https://e/partner-2",
                "title_clean": "Partner Director",
                "description_clean": "Lead client strategy for district education partnerships.",
                "responsibilities_clean": "Own client partnership planning across school districts.",
                "requirements_clean": "",
                "departments_raw": [{"name": "Client Strategy"}],
                "skills": [],
                "tags": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    run_title_stage(
        input_cleaned_path=cleaned,
        input_extracted_path=extracted,
        output_path=output,
    )
    row = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert row["normalized_title"] == "other"
    assert row["classification_status"] == "other"
