# Phase E.3 — Targeted Taxonomy Cleanup Patch

## Scope
- `software development manager`
- `production engineer`
- `fpga engineer`
- `it administrator`
- `technical architect`
- `data science manager` as new-label experiment

## Comparison
- `software development manager` | before `business_development_representative/sales` (0.7279) | after `engineering_manager/software_engineering` (1.0) | changed `True`
- `production engineer` | before `sales_engineer/sales` (0.665) | after `manufacturing_engineer/industrial_engineering` (1.0) | changed `True`
- `fpga engineer` | before `ml_engineer/machine_learning` (0.7244) | after `electrical_engineer/industrial_engineering` (1.0) | changed `True`
- `it administrator` | before `school_administrator/education` (0.7658) | after `it_support_specialist/it_operations` (1.0) | changed `True`
- `technical architect` | before `technical_recruiter/recruiting` (0.6613) | after `solutions_architect/architecture` (1.0) | changed `True`
- `data science manager` | before `story_editor/content` (0.692) | after `data_science_manager/data_science` (1.0) | changed `True`

## Notes
- This patch affects only the semantic layer corpus and retrieval.
- No production classifier files were modified.
