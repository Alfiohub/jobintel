# Git Workflow

## Branch naming
Use one branch per topic:
- `feat/<area>-<goal>`
- `fix/<area>-<bug>`
- `chore/<area>-<task>`

Examples:
- `feat/api-v1-filters`
- `feat/ner-cost-control`
- `chore/repo-structure`

## Commit policy
- Small, focused commits
- Message format: `<type>: <scope>`
  - `feat: add /v1 filters endpoints`
  - `chore: scaffold modules layout`

## Safety rules
- Never commit secrets (`.secrets/`, keys, tokens)
- Keep tests green on every branch before merge
- Avoid mixed commits (runtime + docs + generated data together)

## Merge checklist
1. `uv run --active pytest -q`
2. Confirm no secret files tracked
3. Confirm docs/contract updates when API/DB changes
