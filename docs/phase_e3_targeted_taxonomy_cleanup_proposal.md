# Phase E.3 — Targeted Taxonomy Cleanup Proposal

## Goal
Stabilize high-confidence semantic taxonomy remaps before any new safe batch promotion.

## In Scope
- software_development_manager -> engineering_manager
- production_engineer -> manufacturing_engineer
- fpga_engineer -> electrical_engineer
- it_administrator -> it_support_specialist
- technical_architect -> solutions_architect

## New Label Decision
- data_science_manager -> candidate new label
- rationale: recurring, coherent managerial data science titles
- decision required: add vs defer

## Explicitly Out of Scope
- onboarding_specialist
- operations_analyst
- partner_manager
- sales_representative
- procurement_manager

## Constraints
- taxonomy-layer proposal only
- no production classifier changes in this phase
- no broad regex expansion
- no automatic promotion from semantic reviewer to official rules

## Acceptance Criteria
- lower internal mismatch noise in semantic retrieval
- cleaner internal candidate alignment for in-scope clusters
- reviewer outputs become more interpretable
- no widening of official production behavior

## Exit Conditions
- proposal approved
- candidate patch isolated
- reviewer rerun completed
- decision recorded for `data_science_manager`
