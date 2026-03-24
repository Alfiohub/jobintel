# Title Taxonomy (MVP)

Questo documento definisce la tassonomia usata per:
- `normalized_title`
- `role_family`
- `occupation_group`

Obiettivo: ridurre ambiguità, abbassare `other_like`, mantenere mapping coerente nel tempo.

## Regole generali
- Ogni titolo deve mappare a un solo `normalized_title`.
- Ogni `normalized_title` appartiene a un solo `role_family`.
- Ogni `role_family` appartiene a un solo `occupation_group`.
- Se non c’è match affidabile: `normalized_title=other`, `role_family=other`, `occupation_group=other`.

## Occupation Groups (MVP)
- `engineering`
- `data`
- `product`
- `design`
- `business`
- `finance`
- `hr`
- `other`

## Role Families (MVP)
- `software_engineering`
- `backend`
- `frontend`
- `fullstack`
- `devops`
- `sre`
- `architecture`
- `data_engineering`
- `data_science`
- `data_analytics`
- `machine_learning`
- `product_management`
- `design`
- `sales`
- `customer_success`
- `consulting`
- `business_analysis`
- `recruiting`
- `executive_leadership`
- `finance`
- `hr`
- `other`

## Normalized Titles (MVP core)
- `software_engineer`
- `backend_engineer`
- `frontend_engineer`
- `fullstack_engineer`
- `devops_engineer`
- `site_reliability_engineer`
- `enterprise_architect`
- `solutions_architect`
- `data_engineer`
- `data_scientist`
- `data_analyst`
- `analytics_engineer`
- `analytics_manager`
- `analytics_director`
- `business_intelligence_analyst`
- `business_intelligence_engineer`
- `ml_engineer`
- `product_manager`
- `product_designer`
- `account_executive`
- `business_development_representative`
- `sales_representative`
- `customer_success_manager`
- `consultant`
- `implementation_consultant`
- `business_analyst`
- `technical_recruiter`
- `hr_business_partner`
- `investment_analyst`
- `chief_technology_officer`
- `manager`
- `other`

## Mapping Examples
- `Data Analytics Director` -> `analytics_director` / `data_analytics` / `data`
- `Senior BI Analyst` -> `business_intelligence_analyst` / `data_analytics` / `data`
- `Field CTO` -> `chief_technology_officer` / `executive_leadership` / `business`
- `Business Analyst - Retail Energy` -> `business_analyst` / `business_analysis` / `business`
- `Technical Recruiter - Contract` -> `technical_recruiter` / `recruiting` / `hr`
- `Enterprise Account Executive` -> `account_executive` / `sales` / `business`

## Policy for `other`
- `other` è consentito solo quando nessuna regola/fallback è sufficientemente affidabile.
- KPI da monitorare: `other_like_pct`.
- Target operativo post-MVP: `other_like_pct < 12%`.

## Change Management
- Ogni modifica tassonomia deve:
  - aggiornare questo file
  - aggiungere/aggiornare test mirati
  - documentare impatto su `other_like_pct`.

