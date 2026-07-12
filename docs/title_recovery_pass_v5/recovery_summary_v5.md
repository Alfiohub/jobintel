# Title Coverage Recovery Pass v5 — Retail / Service Operations Expansion

## Scope
Pass focalizzato solo su cluster retail / service operations residuale, con regole conservative.

## Before / After
- Total rows: `81,011`
- `other` before (v4): `42,186` (`52.07%`)
- `other` after (v5): `42,015` (`51.86%`)
- Delta `other`: `-171`

## Nuove label introdotte
- Nessuna nuova label in questo pass.
- Riutilizzo label esistenti: `store_associate`, `operations_specialist`.

## Regole aggiunte (conservative)
- `store advisor|lead store advisor|store associate|retail advisor` -> `store_associate`
- `assistant store manager|retail store manager|store manager|retail manager|store leader|store director|retail assistant manager` -> `operations_specialist`
- `stylist/floor lead` coperti solo se con contesto `retail` (ma vedi nota su normalizzazione)

## Nota importante (precisione)
Nel pipeline corrente la normalizzazione rimuove il contenuto tra parentesi.
Quindi:
- `Stylist (Retail) (Part-time)` -> `stylist`
- `Floor Lead (Retail) (Part-time)` -> `floor lead`

Senza il contesto `retail`, mappare `stylist` o `floor lead` sarebbe overmatch.
Per questo in v5 restano `other` (scelta conservativa).

## Sample titoli coperti
- `assistant store manager` -> `operations_specialist` (16)
- `store manager` -> `operations_specialist` (13)
- `retail store manager` -> `operations_specialist` (13)
- `store director` -> `operations_specialist` (2)
- `store advisor` -> `store_associate` (2)
- `retail - lead store advisor（bicester）` -> `store_associate` (2)

## Top residual `other` (post-v5)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (28)
6. `social enterprise and program delivery-evergreen` (27)
7. `stylist (retail) (part-time)` (27)
8. `personal care specialist (part time)` (26)
9. `senior systems engineer` (25)
10. `floor lead (retail) (part-time)` (25)
11. `inside sales representative` (24)
12. `quantitative researcher` (24)
13. `senior network engineer` (23)
14. `network engineer` (22)
15. `mid-level automotive parts associate` (21)
16. `business analyst` (20)
17. `board certified behavior analyst` (20)
18. `field technician (mechanic) (pump, power & hvac)` (20)
19. `solution specialist` (20)
20. `senior people business partner` (19)

## Cluster consigliato per pass v6
1. Generic managerial/program titles (`general manager`, strategy/program evergreen) con regole conservative
2. Business/sales support residual (`inside sales representative`, `business analyst`, `quantitative researcher`) con pass precisione dedicato
3. Industrial tail specifico (`field technician (mechanic) pump/power/hvac`, `automotive parts associate`)
4. Retail contextual recovery (solo se si mantiene segnali pre-normalization per distinguere `stylist (retail)` da `stylist`)

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v5/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `20 passed`
