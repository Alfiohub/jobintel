# Phase E.4 — Production Promotion Planning

## Goal
Convert the semantic-layer findings from Phase E.3 into a controlled production promotion plan, without widening rule behavior or introducing opaque mappings.

## Baseline
- production benchmark dataset: `data/jobs/jobs_titled_en_recovery_v53_safe.jsonl`
- rows_total: `81,011`
- other baseline: `36,092`
- branch context: `phase-e-semantic-bootstrap`

## Decision Summary

### Promote as candidate production remaps
These five items should move forward as a separate official candidate patch because:
- the target labels already exist in the official taxonomy
- the semantic cleanup corrected clearly incoherent internal retrieval
- each case is title-specific enough to be expressed with tight rules

1. `software_development_manager -> engineering_manager`
2. `production_engineer -> manufacturing_engineer`
3. `fpga_engineer -> electrical_engineer`
4. `it_administrator -> it_support_specialist`
5. `technical_architect -> solutions_architect`

### Defer for explicit taxonomy decision
1. `data_science_manager`

Reason for defer:
- the semantic experiment shows it is coherent as a potential new label
- but it still requires an explicit official taxonomy decision
- it should not be bundled silently with the five remaps to existing labels

## Why These Five Are Ready

### 1. Existing target labels already exist
The official taxonomy already contains:
- `engineering_manager`
- `manufacturing_engineer`
- `electrical_engineer`
- `it_support_specialist`
- `solutions_architect`

This keeps the promotion limited to routing logic, not taxonomy expansion.

### 2. Retrieval mismatch was clearly wrong before cleanup
Phase E.3 corrected these incoherent semantic matches:
- `software development manager`: `business_development_representative -> engineering_manager`
- `production engineer`: `sales_engineer -> manufacturing_engineer`
- `fpga engineer`: `ml_engineer -> electrical_engineer`
- `it administrator`: `school_administrator -> it_support_specialist`
- `technical architect`: `technical_recruiter -> solutions_architect`

### 3. Production expression can stay narrow
Recommended future rule shape:
- exact or near-exact title forms
- narrow seniority variants only
- explicit exclusions where ambiguity is known

## Out of Scope for This Promotion Plan
- `data_science_manager` as official new label
- `onboarding_specialist`
- `operations_analyst`
- `partner_manager`
- `sales_representative`
- `procurement_manager`
- naked `engineer`
- naked `designer`

## Recommended Production Patch Scope

### Patch A: existing-label remaps only
Create one isolated candidate patch covering only:
- `software development manager`
- `production engineer`
- `fpga engineer`
- `it administrator`
- `technical architect`

### Patch B: optional later taxonomy expansion
Keep separate:
- `data_science_manager`

This prevents mixing:
- low-risk routing cleanup
- medium-risk taxonomy expansion

## Regression Guardrails
- no broad regex on `engineer`, `architect`, `administrator`, or `manager`
- no new catch-all patterns
- no semantic auto-promotion
- no taxonomy changes in Patch A
- negative tests required for adjacent high-risk titles

## Required Test Design for Patch A

### Positive coverage
- `Software Development Manager`
- `Senior Software Development Manager`
- `Production Engineer`
- `Senior Production Engineer`
- `FPGA Engineer`
- `Senior FPGA Engineer`
- `IT Administrator`
- `Senior Salesforce Administrator` only if explicitly included by final rule scope
- `Technical Architect`

### Negative coverage
- `Business Development Manager`
- `Sales Engineer`
- `ML Engineer`
- `School Administrator`
- `Technical Recruiter`
- naked `Architect`
- naked `Administrator`

## Recommended Sequence
1. implement Patch A as a production-candidate patch
2. run official tests
3. run full eval on `data/jobs/jobs_titled_en_recovery_v53_safe.jsonl`
4. verify delta and inspect for overmatch
5. decide separately whether `data_science_manager` deserves taxonomy expansion

## Current Status
- five remaps to existing labels: `approved for candidate patch`
- `data_science_manager`: `defer pending explicit taxonomy decision`
- chapter status: `in progress`

## Exit Criteria for Chapter 9
- candidate production patch prepared
- regression tests defined and implemented
- eval completed against the v53 safe baseline
- promotion outcome recorded
