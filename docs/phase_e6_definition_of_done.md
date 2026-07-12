# Phase E.6 — Definition of Done

## Goal
Define when the title normalization system is mature enough to be considered operationally reliable, even if `other` is not eliminated.

## Current Baseline
- current official benchmark dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- rows total: `81,011`
- current official `other`: `35,952`

## Operating Principle
The system is considered done when it is:
- high-precision on promoted mappings
- taxonomy-consistent
- auditable
- maintainable through a repeatable batch workflow
- explicit about what must remain in `other`

`other` is not the failure state by itself. Uncontrolled overmatch is the failure state.

## Definition of Done Criteria

### 1. Audited precision threshold
- minimum audited precision on newly promoted clusters: `>= 95%`
- target precision for low-risk promotions: `>= 97%`

Audit scope:
- sample only the titles newly captured by each production patch
- audit both positives and the main adjacent negatives

Reason:
- this keeps quality gates attached to each incremental change instead of hiding errors in aggregate coverage.

### 2. Overmatch threshold
- maximum acceptable overmatch on audited promoted clusters: `<= 2%`
- hard stop threshold: `> 5%`

Reason:
- once a patch starts contaminating adjacent families, the gain in `other` is not worth keeping.

### 3. Realistic `other` target
Use two targets, not one:

- working target for the current title-only + semantic-reviewer system: `<= 35,000`
- stretch target before requiring broader context or taxonomy expansion: `34,000–35,000`

Interpretation:
- dropping from `35,952` to below `35,000` with precision intact is a meaningful milestone
- pushing far below that with title-only logic is likely to create diminishing returns and overmatch pressure

### 4. Official `keep_other` policy
Keep a title in `other` when any of the following is true:
- the title is structurally generic (`Engineer`, `Designer`, `Producer` without enough context)
- the title is cross-domain and title-only evidence is insufficient
- the best target would be taxonomy fiction rather than a real internal label
- a candidate mapping depends on context that is not available or not stable enough
- the likely gain comes with medium-high or high overmatch risk

Reason:
- `keep_other` is a valid quality decision, not a backlog failure by itself.

### 5. Standard maintenance workflow
The system is considered maintainable only if updates follow this sequence:
1. residual analysis
2. semantic reviewer / context reviewer where needed
3. taxonomy review if target is unclear
4. shortlist of low-risk candidates
5. isolated production candidate patch
6. positive and negative tests
7. benchmark eval
8. audit
9. stop / continue decision

Reason:
- this prevents ad hoc rule sprawl and keeps each promotion explainable.

### 6. New label governance
Add a new official label only if all are true:
- the cluster is semantically coherent
- there is no clean existing target
- recurring volume is meaningful
- the label is useful for downstream systems
- the label is not brand-specific or overly narrow
- the distinction is likely inferable from title or title+context with stable signals

Practical minimum bar:
- repeated evidence across multiple companies
- clear role family destination
- enough examples to support positive and negative tests

### 7. Continuous operating loop
The system is only considered done if the team can repeat the following loop without redesigning the architecture:
- analysis
- taxonomy review
- safe batch
- tests
- eval
- stop

That is the maintenance model after initial build-out.

## Maturity Decision
The system can be considered operationally mature when all are true:
- Chapters `1–11` are closed
- current and future patches meet the precision and overmatch thresholds above
- the project reaches `other <= 35,000` without precision degradation
- there is an explicit policy for what is intentionally left in `other`
- context-gated rules remain narrow, audited, and title-first

## What Does Not Need To Be True
The system does **not** need:
- zero `other`
- full semantic auto-classification
- broad catch-all patterns
- exhaustive taxonomy expansion

Those goals would push the system away from reliability.

## Final Recommendation
- `definition_of_done_established`

## Next State
With this document in place, the project can transition from architecture build-out to ongoing controlled maintenance and selective promotion.
