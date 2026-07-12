# Title Coverage Recovery Pass v6 — Industrial Tail Specific Expansion

## Scope
Pass focalizzato solo su industrial tail specific residuale, con regole conservative.

## Before / After
- Total rows: `81,011`
- `other` before (v5): `42,015` (`51.86%`)
- `other` after (v6): `41,968` (`51.81%`)
- Delta `other`: `-47`

## Nuove label introdotte
- Nessuna nuova label in questo pass.
- Riutilizzo label esistente: `store_associate`.

## Regole aggiunte (conservative)
- `automotive parts associate` con varianti level (`entry|mid|senior|junior`) -> `store_associate`

## Guardrail precisione
- Nessun mapping largo di tutti i `field technician`
- Nessun mapping largo di tutti i `associate`
- Nessun mapping largo di tutti i `mechanic`

## Limite tecnico noto (contesto perso)
Nel pipeline attuale la normalizzazione rimuove il contenuto tra parentesi.
Quindi:
- `field technician (mechanic) (pump, power & hvac)` -> `field technician`

Senza i token `mechanic/pump/power/hvac`, non è possibile mappare in modo sicuro quel cluster
senza overmatch su field technician generici. Il pass v6 mantiene quindi questo titolo in `other`.

## Sample titoli coperti
- `mid-level automotive parts associate` -> `store_associate` (21)
- `entry-level automotive parts associate` -> `store_associate` (19)
- `entry-level automotive parts associate (2nd shift)` -> `store_associate` (4)
- `automotive parts associate (2nd shift) - mid level` -> `store_associate` (1)

## Top residual `other` (post-v6)
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
15. `business analyst` (20)
16. `board certified behavior analyst` (20)
17. `field technician (mechanic) (pump, power & hvac)` (20)
18. `solution specialist` (20)
19. `senior people business partner` (19)
20. `solution engineer` (19)

## Cluster consigliato per pass v7
1. Generic managerial/program titles (`general manager`, strategy/program evergreen) con regole conservative
2. Business/sales support residual (`inside sales representative`, `business analyst`, `quantitative researcher`)
3. Residual engineering ambiguity (`systems/network`) solo con precision pass
4. Eventuale contextual pass su retail/industrial solo se si preserva contesto pre-normalization

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v6/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `21 passed`
