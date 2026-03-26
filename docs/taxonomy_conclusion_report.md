# Taxonomy Conclusion Report

## Final Architecture Decision
- Final output fields: `normalized_title`, `role_family`.
- Internal taxonomy is the source of truth.
- ESCO/O*NET are semantic support only (mapping suggestions, not master schema).

## Final Taxonomy (v1)
- Role families kept: 27
- Normalized titles kept: 58

### Role Families
- `architecture`
- `business_analysis`
- `consulting`
- `customer_success`
- `data_analytics`
- `data_engineering`
- `data_science`
- `design`
- `devops`
- `executive_leadership`
- `finance`
- `healthcare`
- `hr`
- `it_operations`
- `legal`
- `machine_learning`
- `marketing`
- `operations`
- `other`
- `partnerships`
- `product_management`
- `program_management`
- `recruiting`
- `sales`
- `software_engineering`
- `sre`
- `strategy`

### Normalized Titles
- `enterprise_architect`
- `solutions_architect`
- `business_analyst`
- `business_systems_analyst`
- `consultant`
- `implementation_consultant`
- `implementation_coordinator`
- `customer_success_manager`
- `analytics_director`
- `analytics_engineer`
- `analytics_manager`
- `business_intelligence_analyst`
- `business_intelligence_engineer`
- `data_analyst`
- `data_engineer`
- `data_scientist`
- `content_designer`
- `product_designer`
- `devops_engineer`
- `chief_revenue_officer`
- `chief_technology_officer`
- `accountant`
- `financial_analyst`
- `investment_analyst`
- `healthcare_provider`
- `hr_business_partner`
- `hr_generalist`
- `hr_manager`
- `talent_analytics_specialist`
- `it_support_specialist`
- `systems_administrator`
- `legal_counsel`
- `ml_engineer`
- `ml_scientist`
- `marketing_specialist`
- `seo_specialist`
- `localization_intern`
- `office_administrator`
- `operations_analyst`
- `operations_specialist`
- `general_application`
- `other`
- `alliance_manager`
- `product_manager`
- `program_analyst`
- `technical_program_manager`
- `technical_recruiter`
- `account_executive`
- `account_manager`
- `business_development_representative`
- `industry_lead`
- `sales_representative`
- `backend_engineer`
- `frontend_engineer`
- `fullstack_engineer`
- `software_engineer`
- `site_reliability_engineer`
- `corporate_development`

## Fallback Policy (Final)
- Strong regex/rule match -> mapped normalized title and family.
- Clear title without direct rule -> controlled fallback (data/finance/ops/marketing/engineering buckets).
- Ambiguous manager titles without clear domain signals -> `other/other`.
- No force-mapping from ESCO/O*NET categories.

## Final Decision on `manager`
- Removed generic fallback `manager -> operations`.
- Added deterministic redistribution for project/program, success, partner, accounting/finance, design, HR, campaign/growth/communications, solution services/architecture, sales, operations, engineering-manager patterns.
- Remaining ambiguous manager cases are explicitly sent to `other/other`.

## Manager Reassignment Summary
- Manager titles analyzed: 32
- Manager titles still mapped to `other`: 2
- Final reassignment distribution:
  - `technical_program_manager` / `program_management`: 7
  - `customer_success_manager` / `customer_success`: 5
  - `operations_specialist` / `operations`: 4
  - `accountant` / `finance`: 3
  - `alliance_manager` / `partnerships`: 3
  - `marketing_specialist` / `marketing`: 3
  - `other` / `other`: 2
  - `product_designer` / `design`: 2
  - `solutions_architect` / `architecture`: 2
  - `hr_manager` / `hr`: 1

## Remaining Cases Destined to `other`
- `Manager, Solution Services (Remote elegible - Costa Rica)`
- `Principal Commodity Manager`

## Quick Batch Validation (500 test db)
- Rows evaluated: 500
- `manager` rows after patch: 0
- `other` rows after patch: 11 (2.2%)
- Top 15 titles still mapped to `other`:
  - 2x `Interested in joining our team?`
  - 1x `Manager, Solution Services (Remote elegible - Costa Rica)`
  - 1x `Principal Commodity Manager`
  - 1x `Public Cloud Enablement Professional`
  - 1x `Représentant du Développement des Ventes`
  - 1x `Representante de Desarrollo de Ventas`
  - 1x `Security Risk Management Specialist`
  - 1x `Senior Design Researcher - User Science`
  - 1x `Senior Jira Administrator`
  - 1x `Software Architect - Containers / Virtualisation`
